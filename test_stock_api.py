import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime
import pandas as pd
from decimal import Decimal
import sys
import os

# Add the parent directory to the path to import the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("./main.py"))))

from main import app, StockData

class TestDataEndpointInputValidation(unittest.TestCase):
    """Test input validation for /data endpoint"""
    
    def setUp(self):
        self.client = TestClient(app)
    
    @patch('main.get_connection')
    def test_post_data_with_mock(self, mock_get_connection):
        """Helper method to test POST /data with mocked database"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor
    
    def test_valid_data_types(self):
        """Test that valid data types are accepted"""
        valid_stock_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            "high": 105.75,
            "low": 99.25,
            "close": 103.00,
            "volume": 1000000
        }
        
        # Test Pydantic model validation
        stock = StockData(
            datetime=datetime(2023, 1, 1, 9, 30),
            open=100.50,
            high=105.75,
            low=99.25,
            close=103.00,
            volume=1000000
        )
        
        self.assertEqual(stock.open, Decimal('100.50'))
        self.assertEqual(stock.high, Decimal('105.75'))
        self.assertEqual(stock.low, Decimal('99.25'))
        self.assertEqual(stock.close, Decimal('103.00'))
        self.assertEqual(stock.volume, 1000000)
        self.assertIsInstance(stock.datetime, datetime)
    
    @patch('main.get_connection')
    def test_invalid_datetime_type(self, mock_get_connection):
        """Test that invalid datetime type is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "invalid-date",
            "open": 100.50,
            "high": 105.75,
            "low": 99.25,
            "close": 103.00,
            "volume": 1000000
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    @patch('main.get_connection')
    def test_invalid_decimal_type_open(self, mock_get_connection):
        """Test that invalid open price type is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": "not_a_number",
            "high": 105.75,
            "low": 99.25,
            "close": 103.00,
            "volume": 1000000
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    @patch('main.get_connection')
    def test_invalid_decimal_type_high(self, mock_get_connection):
        """Test that invalid high price type is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            "high": "invalid",
            "low": 99.25,
            "close": 103.00,
            "volume": 1000000
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    @patch('main.get_connection')
    def test_invalid_decimal_type_low(self, mock_get_connection):
        """Test that invalid low price type is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            "high": 105.75,
            "low": [],
            "close": 103.00,
            "volume": 1000000
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    @patch('main.get_connection')
    def test_invalid_decimal_type_close(self, mock_get_connection):
        """Test that invalid close price type is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            "high": 105.75,
            "low": 99.25,
            "close": {"invalid": "object"},
            "volume": 1000000
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    @patch('main.get_connection')
    def test_invalid_volume_type(self, mock_get_connection):
        """Test that invalid volume type is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            "high": 105.75,
            "low": 99.25,
            "close": 103.00,
            "volume": "not_an_integer"
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    def test_decimal_places_validation(self):
        """Test that prices with more than 2 decimal places are handled correctly"""
        with self.assertRaises(ValueError):
            StockData(
                datetime=datetime.now(),
                open=100.123,  # More than 2 decimal places
                high=105.75,
                low=99.25,
                close=103.00,
                volume=1000000
            )
    
    @patch('main.get_connection')
    def test_negative_volume(self, mock_get_connection):
        """Test that negative volume is rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        invalid_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            "high": 105.75,
            "low": 99.25,
            "close": 103.00,
            "volume": -1000
        }
        
        response = self.client.post("/data", json=invalid_data)
        self.assertEqual(response.status_code, 422)
    
    @patch('main.get_connection')
    def test_missing_required_fields(self, mock_get_connection):
        """Test that missing required fields are rejected"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        incomplete_data = {
            "datetime": "2023-01-01T09:30:00",
            "open": 100.50,
            # Missing high, low, close, volume
        }
        
        response = self.client.post("/data", json=incomplete_data)
        self.assertEqual(response.status_code, 422)


class TestMovingAverageCalculations(unittest.TestCase):
    """Test correctness of moving average calculations"""
    
    def setUp(self):
        """Set up test data for moving average calculations"""
        self.test_data = [
            {'datetime': datetime(2023, 1, 1), 'close': 100},
            {'datetime': datetime(2023, 1, 2), 'close': 102},
            {'datetime': datetime(2023, 1, 3), 'close': 104},
            {'datetime': datetime(2023, 1, 4), 'close': 106},
            {'datetime': datetime(2023, 1, 5), 'close': 108},
            {'datetime': datetime(2023, 1, 6), 'close': 110},
            {'datetime': datetime(2023, 1, 7), 'close': 112},
            {'datetime': datetime(2023, 1, 8), 'close': 114},
            {'datetime': datetime(2023, 1, 9), 'close': 116},
            {'datetime': datetime(2023, 1, 10), 'close': 118},
        ]
    
    def test_short_moving_average_calculation(self):
        """Test correctness of short moving average calculation"""
        df = pd.DataFrame(self.test_data)
        df.set_index('datetime', inplace=True)
        
        # Calculate 3-period moving average
        short_window = 3
        df['short_ma'] = df['close'].rolling(window=short_window).mean()
        
        # Manual calculation for verification:
        # Index 2: (100 + 102 + 104) / 3 = 102.0
        self.assertAlmostEqual(df['short_ma'].iloc[2], 102.0, places=2)
        
        # Index 3: (102 + 104 + 106) / 3 = 104.0
        self.assertAlmostEqual(df['short_ma'].iloc[3], 104.0, places=2)
        
        # Index 4: (104 + 106 + 108) / 3 = 106.0
        self.assertAlmostEqual(df['short_ma'].iloc[4], 106.0, places=2)
    
    def test_long_moving_average_calculation(self):
        """Test correctness of long moving average calculation"""
        df = pd.DataFrame(self.test_data)
        df.set_index('datetime', inplace=True)
        
        # Calculate 5-period moving average
        long_window = 5
        df['long_ma'] = df['close'].rolling(window=long_window).mean()
        
        # Manual calculation for verification:
        # Index 4: (100 + 102 + 104 + 106 + 108) / 5 = 104.0
        self.assertAlmostEqual(df['long_ma'].iloc[4], 104.0, places=2)
        
        # Index 5: (102 + 104 + 106 + 108 + 110) / 5 = 106.0
        self.assertAlmostEqual(df['long_ma'].iloc[5], 106.0, places=2)
        
        # Index 6: (104 + 106 + 108 + 110 + 112) / 5 = 108.0
        self.assertAlmostEqual(df['long_ma'].iloc[6], 108.0, places=2)
    
    def test_moving_average_nan_values(self):
        """Test that moving averages produce NaN for insufficient data"""
        df = pd.DataFrame(self.test_data)
        df.set_index('datetime', inplace=True)
        
        # Calculate moving averages
        df['short_ma'] = df['close'].rolling(window=3).mean()
        df['long_ma'] = df['close'].rolling(window=5).mean()
        
        # First 2 values should be NaN for 3-period MA
        self.assertTrue(pd.isna(df['short_ma'].iloc[0]))
        self.assertTrue(pd.isna(df['short_ma'].iloc[1]))
        
        # First 4 values should be NaN for 5-period MA
        self.assertTrue(pd.isna(df['long_ma'].iloc[0]))
        self.assertTrue(pd.isna(df['long_ma'].iloc[1]))
        self.assertTrue(pd.isna(df['long_ma'].iloc[2]))
        self.assertTrue(pd.isna(df['long_ma'].iloc[3]))
    
    def test_signal_generation_logic(self):
        """Test correctness of trading signal generation"""
        df = pd.DataFrame(self.test_data)
        df.set_index('datetime', inplace=True)
        
        # Calculate moving averages
        df['short_ma'] = df['close'].rolling(window=3).mean()
        df['long_ma'] = df['close'].rolling(window=5).mean()
        df.dropna(inplace=True)
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1  # Buy signal
        df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1  # Sell signal
        
        # Verify signal values are only -1, 0, or 1
        valid_signals = df['signal'].isin([-1, 0, 1]).all()
        self.assertTrue(valid_signals)
        
        # Test specific signal logic
        for i in range(len(df)):
            if df['short_ma'].iloc[i] > df['long_ma'].iloc[i]:
                self.assertEqual(df['signal'].iloc[i], 1)
            elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i]:
                self.assertEqual(df['signal'].iloc[i], -1)
            else:
                self.assertEqual(df['signal'].iloc[i], 0)
    
    def test_returns_calculation(self):
        """Test correctness of returns calculation"""
        df = pd.DataFrame(self.test_data)
        df.set_index('datetime', inplace=True)
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        
        # Manual verification for first few returns
        # Return from day 1 to day 2: (102 - 100) / 100 = 0.02
        self.assertAlmostEqual(df['returns'].iloc[1], 0.02, places=4)
        
        # Return from day 2 to day 3: (104 - 102) / 102 ≈ 0.0196
        self.assertAlmostEqual(df['returns'].iloc[2], 0.019607843137254902, places=4)
        
        # First value should be NaN
        self.assertTrue(pd.isna(df['returns'].iloc[0]))
    
    @patch('main.get_connection')
    def test_strategy_endpoint_calculation_flow(self, mock_get_connection):
        """Test the complete calculation flow in the strategy endpoint"""
        # Mock database connection and data
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Prepare test data with required fields
        test_data = [
            {'datetime': datetime(2023, 1, i+1), 'open': 100+i, 'high': 105+i, 
             'low': 95+i, 'close': 100+i*2, 'volume': 1000+i*100}
            for i in range(25)  # Enough data for moving averages
        ]
        
        mock_cursor.fetchall.return_value = test_data
        
        client = TestClient(app)
        response = client.get("/strategy/performance?short_window=5&long_window=10")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure and data types
        self.assertIn('buy_signals', data)
        self.assertIn('sell_signals', data)
        self.assertIn('total_trades', data)
        self.assertIn('cumulative_return', data)
        self.assertIn('data_points', data)
        
        self.assertIsInstance(data['buy_signals'], int)
        self.assertIsInstance(data['sell_signals'], int)
        self.assertIsInstance(data['total_trades'], int)
        self.assertIsInstance(data['cumulative_return'], (int, float))
        self.assertIsInstance(data['data_points'], int)
        
        # Verify total trades is sum of buy and sell signals
        self.assertEqual(data['total_trades'], data['buy_signals'] + data['sell_signals'])


if __name__ == '_main_':
    # Run only the specified tests
    unittest.main(verbosity=2)