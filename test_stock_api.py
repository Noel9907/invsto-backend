import unittest
from fastapi.testclient import TestClient
from main import app, StockData
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from decimal import Decimal
import json

client = TestClient(app)


class TestDataEndpointValidation(unittest.TestCase):
    """Test suite for /data endpoint input validation"""

    def test_valid_data_post(self):
        """Test posting valid stock data"""
        with patch("main.get_connection") as mock_get_connection:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_connection.return_value = mock_conn

            payload = {
                "datetime": "2023-01-01T00:00:00",
                "open": 100.50,
                "high": 105.75,
                "low": 95.25,
                "close": 102.00,
                "volume": 1000
            }

            response = client.post("/data", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Stock data added successfully"})

    def test_missing_datetime_field(self):
        """Test validation when datetime field is missing"""
        payload = {
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)
        error_detail = response.json()["detail"]
        self.assertTrue(any("datetime" in str(error) for error in error_detail))

    def test_missing_open_field(self):
        """Test validation when open field is missing"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_missing_volume_field(self):
        """Test validation when volume field is missing"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_datetime_type(self):
        """Test validation with invalid datetime format"""
        payload = {
            "datetime": "not-a-date",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_open_type(self):
        """Test validation with invalid open price type"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": "not-a-number",
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_high_type(self):
        """Test validation with invalid high price type"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.0,
            "high": "invalid",
            "low": 95.0,
            "close": 102.0,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_low_type(self):
        """Test validation with invalid low price type"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.0,
            "high": 105.0,
            "low": [],  # invalid type
            "close": 102.0,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_close_type(self):
        """Test validation with invalid close price type"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": {"invalid": "object"},
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_invalid_volume_type(self):
        """Test validation with invalid volume type"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": "not-an-integer"
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_negative_volume(self):
        """Test validation with negative volume (should fail)"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 102.0,
            "volume": -100
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_zero_volume(self):
        """Test validation with zero volume (should pass)"""
        with patch("main.get_connection") as mock_get_connection:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_connection.return_value = mock_conn

            payload = {
                "datetime": "2023-01-01T00:00:00",
                "open": 100.0,
                "high": 105.0,
                "low": 95.0,
                "close": 102.0,
                "volume": 0
            }
            response = client.post("/data", json=payload)
            self.assertEqual(response.status_code, 200)

    def test_decimal_precision_validation(self):
        """Test that decimal places are properly handled"""
        with patch("main.get_connection") as mock_get_connection:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_connection.return_value = mock_conn

            payload = {
                "datetime": "2023-01-01T00:00:00",
                "open": 100.12,  # Exactly 2 decimal places
                "high": 105.45,
                "low": 95.78,
                "close": 102.99,
                "volume": 1000
            }
            response = client.post("/data", json=payload)
            self.assertEqual(response.status_code, 200)

    def test_excessive_decimal_places(self):
        """Test validation with more than 2 decimal places"""
        payload = {
            "datetime": "2023-01-01T00:00:00",
            "open": 100.123456,  # More than 2 decimal places
            "high": 105.456789,
            "low": 95.789123,
            "close": 102.999999,
            "volume": 1000
        }
        response = client.post("/data", json=payload)
        # This should fail due to decimal constraint
        self.assertEqual(response.status_code, 422)


class TestMovingAverageCalculations(unittest.TestCase):
    """Test suite for moving average calculation correctness"""

    def test_simple_moving_average_calculation(self):
        """Test basic moving average calculation with known values"""
        # Create test data with predictable values
        close_prices = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        df = pd.DataFrame({
            "close": close_prices
        })
        
        # Calculate 3-period moving average
        window = 3
        df["ma"] = df["close"].rolling(window=window).mean()
        
        # Verify specific calculations
        # MA for index 2 (3rd item): (10+20+30)/3 = 20
        self.assertEqual(df["ma"].iloc[2], 20.0)
        # MA for index 3 (4th item): (20+30+40)/3 = 30
        self.assertEqual(df["ma"].iloc[3], 30.0)
        # MA for index 9 (last item): (80+90+100)/3 = 90
        self.assertEqual(df["ma"].iloc[9], 90.0)

    def test_moving_average_with_different_windows(self):
        """Test moving averages with different window sizes"""
        close_prices = list(range(1, 21))  # [1, 2, 3, ..., 20]
        df = pd.DataFrame({"close": close_prices})
        
        # Test 5-period MA
        df["ma5"] = df["close"].rolling(window=5).mean()
        # At index 4: (1+2+3+4+5)/5 = 3.0
        self.assertEqual(df["ma5"].iloc[4], 3.0)
        
        # Test 10-period MA
        df["ma10"] = df["close"].rolling(window=10).mean()
        # At index 9: (1+2+...+10)/10 = 5.5
        self.assertEqual(df["ma10"].iloc[9], 5.5)

    def test_moving_average_signal_generation(self):
        """Test signal generation logic in moving average strategy"""
        # Create test data with a clear trend change
        close_prices = [100] * 5 + [110] * 5 + [120] * 5 + [130] * 10  # Upward trend
        data = {
            "datetime": pd.date_range("2023-01-01", periods=len(close_prices)),
            "close": close_prices
        }
        df = pd.DataFrame(data)
        df.set_index("datetime", inplace=True)
        
        short_window = 3
        long_window = 8
        
        df["short_ma"] = df["close"].rolling(window=short_window).mean()
        df["long_ma"] = df["close"].rolling(window=long_window).mean()
        df.dropna(inplace=True)
        
        # Generate signals
        df["signal"] = 0
        df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1
        df.loc[df["short_ma"] < df["long_ma"], "signal"] = -1
        
        # Check that we have some buy signals in the later periods due to upward trend
        buy_signals = (df["signal"] == 1).sum()
        self.assertGreater(buy_signals, 0, "Should have some buy signals with upward trend")

    def test_edge_case_insufficient_data(self):
        """Test moving average calculation with insufficient data"""
        close_prices = [10, 20, 30]  # Only 3 data points
        df = pd.DataFrame({"close": close_prices})
        
        # Try to calculate 5-period MA (more than available data)
        df["ma5"] = df["close"].rolling(window=5).mean()
        
        # All values should be NaN since we don't have enough data
        self.assertTrue(df["ma5"].isna().all())

    def test_moving_average_with_identical_values(self):
        """Test moving average when all values are the same"""
        close_prices = [100] * 10  # All values are 100
        df = pd.DataFrame({"close": close_prices})
        
        df["ma3"] = df["close"].rolling(window=3).mean()
        df.dropna(inplace=True)
        
        # All moving averages should equal 100
        self.assertTrue((df["ma3"] == 100).all())


class TestStrategyPerformanceEndpoint(unittest.TestCase):
    """Test suite for /strategy/performance endpoint"""

    @patch("main.get_connection")
    def test_strategy_performance_success(self, mock_get_connection):
        """Test successful strategy performance calculation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Create realistic test data
        data = [
            {
                "datetime": f"2023-01-{i+1:02d}T00:00:00",
                "open": 100 + i * 0.5,
                "high": 105 + i * 0.5,
                "low": 95 + i * 0.5,
                "close": 100 + i * 0.5,  # Gradual uptrend
                "volume": 1000 + i * 10
            }
            for i in range(30)
        ]

        mock_cursor.fetchall.return_value = data
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        response = client.get("/strategy/performance?short_window=5&long_window=20")
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn("buy_signals", result)
        self.assertIn("sell_signals", result)
        self.assertIn("total_trades", result)
        self.assertIn("cumulative_return", result)
        self.assertIn("data_points", result)
        
        # Verify data types
        self.assertIsInstance(result["buy_signals"], int)
        self.assertIsInstance(result["sell_signals"], int)
        self.assertIsInstance(result["total_trades"], int)
        self.assertIsInstance(result["cumulative_return"], (int, float))
        self.assertIsInstance(result["data_points"], int)

    @patch("main.get_connection")
    def test_strategy_performance_insufficient_data(self, mock_get_connection):
        """Test strategy performance with insufficient data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Only 10 data points, but long_window is 20
        data = [
            {
                "datetime": f"2023-01-{i+1:02d}T00:00:00",
                "open": 100,
                "high": 105,
                "low": 95,
                "close": 100,
                "volume": 1000
            } for i in range(10)
        ]
        
        mock_cursor.fetchall.return_value = data
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        response = client.get("/strategy/performance?short_window=5&long_window=20")
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn("message", result)
        self.assertIn("Not enough valid data", result["message"])

    @patch("main.get_connection")
    def test_strategy_performance_empty_database(self, mock_get_connection):
        """Test strategy performance with empty database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        response = client.get("/strategy/performance")
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn("message", result)
        self.assertIn("Not enough valid data", result["message"])

    @patch("main.get_connection")
    def test_strategy_performance_custom_windows(self, mock_get_connection):
        """Test strategy performance with custom window parameters"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Create valid test data with proper date format
        data = [
            {
                "datetime": f"2023-01-{i+1:02d}T00:00:00",
                "open": 100,
                "high": 105,
                "low": 95,
                "close": 100 + (i % 10),  # Cyclical pattern
                "volume": 1000
            }
            for i in range(30)  # Only 30 days to avoid invalid dates
        ]

        mock_cursor.fetchall.return_value = data
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Test with custom windows
        response = client.get("/strategy/performance?short_window=3&long_window=15")
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn("buy_signals", result)
        self.assertIn("sell_signals", result)

    def test_strategy_performance_invalid_parameters(self):
        """Test strategy performance with invalid parameters"""
        # Test with zero window
        response = client.get("/strategy/performance?short_window=0&long_window=20")
        self.assertEqual(response.status_code, 422)
        
        # Test with negative window
        response = client.get("/strategy/performance?short_window=-5&long_window=20")
        self.assertEqual(response.status_code, 422)


class TestGetDataEndpoint(unittest.TestCase):
    """Test suite for GET /data endpoint"""

    @patch("main.get_connection")
    def test_get_data_success(self, mock_get_connection):
        """Test successful data retrieval"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        test_data = [
            {
                "datetime": "2023-01-01T00:00:00",
                "open": Decimal("100.50"),
                "high": Decimal("105.75"),
                "low": Decimal("95.25"),
                "close": Decimal("102.00"),
                "volume": 1000
            }
        ]
        
        mock_cursor.fetchall.return_value = test_data
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        response = client.get("/data")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


class TestStockDataModel(unittest.TestCase):
    """Test suite for StockData pydantic model"""

    def test_valid_stock_data_creation(self):
        """Test creating valid StockData instance"""
        data = {
            "datetime": datetime(2023, 1, 1),
            "open": Decimal("100.50"),
            "high": Decimal("105.75"),
            "low": Decimal("95.25"),
            "close": Decimal("102.00"),
            "volume": 1000
        }
        
        stock = StockData(**data)
        self.assertEqual(stock.datetime, datetime(2023, 1, 1))
        self.assertEqual(stock.open, Decimal("100.50"))
        self.assertEqual(stock.volume, 1000)

    def test_volume_validation(self):
        """Test volume validation constraints"""
        data = {
            "datetime": datetime(2023, 1, 1),
            "open": Decimal("100.50"),
            "high": Decimal("105.75"),
            "low": Decimal("95.25"),
            "close": Decimal("102.00"),
            "volume": -1  # Invalid negative volume
        }
        
        with self.assertRaises(ValueError):
            StockData(**data)


if __name__ == "_main_":
    # Run all tests
    unittest.main(verbosity=2)