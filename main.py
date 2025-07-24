import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
import pandas as pd
from db import get_connection
from datetime import datetime
from fastapi import FastAPI, HTTPException,Query
from pydantic import BaseModel, condecimal,conint
from typing import List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor



app = FastAPI()


def get_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor
    )
    return conn

class StockData(BaseModel):
    datetime: datetime
    open: condecimal(decimal_places=2)
    high: condecimal(decimal_places=2)
    low: condecimal(decimal_places=2)
    close: condecimal(decimal_places=2)
    volume: conint(ge=0) 

@app.get("/data", response_model=List[StockData])
def get_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stock_data ORDER BY datetime ASC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.get("/init")
def init_db():
    try:
        df = pd.read_excel("data.xlsx", header=0)  
    except Exception as e:
        return {"error": f"Failed to read Excel file: {str(e)}"}

    print("\nRaw data from Excel:")
    print(df.head(3))
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"Data types:\n{df.dtypes}")

    df.columns = df.columns.str.lower()

    required_columns = {'datetime', 'open', 'high', 'low', 'close', 'volume'}
    if not required_columns.issubset(set(df.columns)):
        return {"error": f"Missing required columns. Needed: {required_columns}, Found: {df.columns.tolist()}"}

    header_like_rows = df.apply(lambda row: any(str(row[col]).lower() == col for col in df.columns), axis=1)
    df = df[~header_like_rows]

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])

    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.dropna()

    print("\nCleaned data ready for insertion:")
    print(df.head(3))
    print(f"\nFinal shape: {df.shape}")

    if df.empty:
        return {"error": "No valid data remaining after cleaning"}

    conn = get_connection()
    cur = conn.cursor()
    
    inserted_rows = 0
    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO stock_data (datetime, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (datetime) DO NOTHING
            """, (
                row["datetime"],
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                int(row["volume"])
            ))
            inserted_rows += cur.rowcount
        except Exception as e:
            print(f"Error inserting row {row}: {e}")
            continue

    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "rows_inserted": inserted_rows,
        "sample_data": df.head(3).to_dict("records")
    }

@app.post("/data")
def add_stock_data(stock: StockData):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO stock_data (datetime, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (datetime) DO NOTHING;
        """, (
            stock.datetime,
            stock.open,
            stock.high,
            stock.low,
            stock.close,
            stock.volume
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

    return {"message": "Stock data added successfully"}


@app.get("/strategy/performance")
def moving_average_strategy(
    short_window: int = Query(5, gt=0),
    long_window: int = Query(20, gt=0)
):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT datetime, open, high, low, close, volume FROM stock_data ORDER BY datetime ASC;")
        rows = cur.fetchall()
        cur.close()

        if not rows or len(rows) < long_window:
            return {"message": f"Not enough valid data. Need at least {long_window} rows."}

        df = pd.DataFrame(rows)

        df["datetime"] = pd.to_datetime(df["datetime"])

        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(inplace=True)

        if len(df) < long_window:
            return {"message": f"Not enough valid data after filtering. Have {len(df)} rows."}

        df.set_index("datetime", inplace=True)

        df["short_ma"] = df["close"].rolling(window=short_window).mean()
        df["long_ma"] = df["close"].rolling(window=long_window).mean()
        df.dropna(inplace=True)

        if df.empty:
            return {"message": "Not enough data to calculate moving averages"}

        df["signal"] = 0
        df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1
        df.loc[df["short_ma"] < df["long_ma"], "signal"] = -1

        df["position"] = df["signal"].shift()
        df.dropna(inplace=True)

        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["position"] * df["returns"]

        cumulative_return = (df["strategy_returns"] + 1).prod() - 1
        buy_signals = int((df["position"] == 1).sum())
        sell_signals = int((df["position"] == -1).sum())

        return {
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "total_trades": buy_signals + sell_signals,
            "cumulative_return": round(cumulative_return, 4),
            "data_points": len(df)
        }

    finally:
        conn.close()