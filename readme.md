# Stock Market Data Analysis API

This project provides a FastAPI application for managing and analyzing stock market data. It allows for storing stock data, initializing the database from a CSV file, and performing basic moving average strategy analysis.

## Features

- **Stock Data Management**:
  - Add individual stock data entries.
  - Retrieve all stored stock data.
- **Database Initialization**:
  - Populate the `stock_data` table from a CSV file (`data.xlsx`).
  - Handles data cleaning, type conversion, and duplicate entries.
  - You can use "/init" endpoint
- **Moving Average Strategy Performance**:
  - Calculate the performance of a simple moving average crossover strategy.
  - Provides insights into buy/sell signals, total trades, and cumulative returns.

## Technologies Used

- **FastAPI**: Web framework for building the API.
- **PostgreSQL**: Relational database for storing stock data.
- **Pandas**: For data manipulation and analysis, especially during database initialization and strategy calculation.
- **Psycopg2**: PostgreSQL adapter for Python.
- **SQLAlchemy**: ORM for interacting with the database.
- **Docker & Docker Compose**: For containerization and easy setup of the application and database.

## Project Structure

- `Dockerfile`: Defines the Docker image for the FastAPI application.
- `docker-compose.yml`: Orchestrates the `backend` (FastAPI app) and `db` (PostgreSQL) services.
- `main.py`: Contains the FastAPI application code, including API endpoints and business logic.
- `db.py`: Contains database connection and session management logic using SQLAlchemy.
- `test_stock_api.py`: Unit tests for the API endpoints and data models.
- `init_db.sql`: SQL script for initial database table creation.
- `data.xlsx - HINDALCO.csv`: CSV file containing stock data for initialization.
- `requirements.txt`: Lists Python dependencies.

## Setup and Running

### Prerequisites

- Docker Desktop (or Docker Engine and Docker Compose) installed on your system.

### Steps

1.  **Clone the Repository (if applicable):**

    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Place `data.xlsx` and `init_db.sql`:**

    - Ensure you have the `data.xlsx` file in the root directory. This will be mounted into the Docker container.
    - Ensure you have the `init_db.sql` file in the root directory. This will be used to initialize the PostgreSQL database.

3.  **Build and Run with Docker Compose:**
    Navigate to the root directory of the project where `docker-compose.yml` is located and run:

    ```bash
    docker-compose up --build -d
    ```

    - `docker-compose up`: Starts the services defined in `docker-compose.yml`.
    - `--build`: Builds the Docker image for the `backend` service if it doesn't exist or if the `Dockerfile` has changed.
    - `-d`: Runs the services in detached mode (in the background).

## API Endpoints

The API will be accessible at `http://localhost:8000`.

### 1. Initialize Database from CSV

- **Endpoint**: `GET /init`
- **Description**: Reads stock data from `data.xlsx`, cleans it, and inserts it into the PostgreSQL database. Handles potential duplicates by using `ON CONFLICT (datetime) DO NOTHING`.
- **Example Response (Success)**:
  ```json
  {
    "status": "success",
    "rows_inserted": 100,
    "sample_data": [
      {
        "datetime": "2023-01-01T00:00:00",
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": 102.0,
        "volume": 1000
      }
    ]
  }
  ```
- **Example Response (Error)**:
  ```json
  {
    "error": "Failed to read CSV file: [error details]"
  }
  ```
  or
  ```json
  {
    "error": "Missing required columns. Needed: {'datetime', 'open', 'high', 'low', 'close', 'volume'}, Found: ['col1', 'col2']"
  }
  ```

### 2. Get All Stock Data

- **Endpoint**: `GET /data`
- **Description**: Retrieves all stock data records from the `stock_data` table, ordered by datetime.
- **Response Model**: `List[StockData]`
- **Example Response**:
  ```json
  [
    {
      "datetime": "2023-01-01T00:00:00",
      "open": 100.5,
      "high": 105.75,
      "low": 95.25,
      "close": 102.0,
      "volume": 1000
    },
    {
      "datetime": "2023-01-02T00:00:00",
      "open": 102.1,
      "high": 107.2,
      "low": 98.0,
      "close": 105.5,
      "volume": 1200
    }
  ]
  ```

### 3. Add Stock Data

- **Endpoint**: `POST /data`
- **Description**: Adds a new stock data entry to the `stock_data` table.
- **Request Body**: `StockData` model
  ```json
  {
    "datetime": "2023-01-01T00:00:00",
    "open": 100.5,
    "high": 105.75,
    "low": 95.25,
    "close": 102.0,
    "volume": 1000
  }
  ```
- **Example Response**:
  ```json
  {
    "message": "Stock data added successfully"
  }
  ```

### 4. Get Moving Average Strategy Performance

- **Endpoint**: `GET /strategy/performance`
- **Description**: Calculates the performance of a simple moving average crossover strategy based on the `close` price.
- **Query Parameters**:
  - `short_window` (int, optional, default: 5): The period for the short-term moving average. Must be greater than 0.
  - `long_window` (int, optional, default: 20): The period for the long-term moving average. Must be greater than 0.
- **Example Response (Success)**:
  ```json
  {
    "buy_signals": 5,
    "sell_signals": 3,
    "total_trades": 8,
    "cumulative_return": 0.0754,
    "data_points": 25
  }
  ```
- **Example Response (Insufficient Data)**:
  ```json
  {
    "message": "Not enough valid data. Need at least 20 rows."
  }
  ```

## Running Tests

To run the unit tests, ensure your Docker containers are running (or you have the necessary environment variables set for database connection) and execute:

```bash
 coverage run -m unittest discover
```

## Get coverage

```bash
coverage report -m
```
