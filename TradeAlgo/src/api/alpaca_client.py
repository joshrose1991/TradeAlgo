from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlpacaClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize API clients
        self.trading_client = TradingClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY'),
            paper=True  # Use paper trading by default
        )
        
        self.data_client = StockHistoricalDataClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY')
        )
        
        logger.info("Alpaca client initialized")

    def get_account(self):
        """Get account information."""
        try:
            return self.trading_client.get_account()
        except Exception as e:
            logger.error(f"Error getting account information: {e}")
            return None

    def get_position(self, symbol):
        """Get position for a specific symbol."""
        try:
            return self.trading_client.get_position(symbol)
        except Exception as e:
            logger.error(f"Error getting position for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol, start_date, end_date=None, timeframe=TimeFrame.Day):
        """Get historical bar data for a symbol."""
        try:
            if end_date is None:
                end_date = datetime.now()

            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start_date,
                end=end_date
            )
            return self.data_client.get_stock_bars(request)
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None

    def place_market_order(self, symbol, qty, side, take_profit=None, stop_loss=None):
        """Place a market order with optional take profit and stop loss."""
        try:
            # Create market order
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit the order
            order = self.trading_client.submit_order(order_data)
            logger.info(f"Market order placed for {symbol}: {order.id}")
            
            # Place take profit order if specified
            if take_profit:
                tp_order = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY,
                    time_in_force=TimeInForce.GTC,
                    limit_price=take_profit
                )
                self.trading_client.submit_order(tp_order)
                logger.info(f"Take profit order placed for {symbol} at {take_profit}")
            
            # Place stop loss order if specified
            if stop_loss:
                sl_order = StopOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY,
                    time_in_force=TimeInForce.GTC,
                    stop_price=stop_loss
                )
                self.trading_client.submit_order(sl_order)
                logger.info(f"Stop loss order placed for {symbol} at {stop_loss}")
            
            return order
        except Exception as e:
            logger.error(f"Error placing market order for {symbol}: {e}")
            return None

    def close_position(self, symbol):
        """Close position for a specific symbol."""
        try:
            return self.trading_client.close_position(symbol)
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            return None

    def get_open_positions(self):
        """Get all open positions."""
        try:
            return self.trading_client.get_all_positions()
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []

    def calculate_position_size(self, symbol, risk_per_trade, stop_loss_price):
        """Calculate position size based on risk management rules."""
        try:
            account = self.get_account()
            if not account:
                return 0
            
            equity = float(account.equity)
            risk_amount = equity * float(os.getenv('RISK_PER_TRADE', risk_per_trade))
            
            # Get current price
            latest_trade = self.get_historical_data(
                symbol,
                start_date=datetime.now() - timedelta(days=1),
                timeframe=TimeFrame.Minute
            )
            if not latest_trade:
                return 0
            
            current_price = float(latest_trade[symbol][0].close)
            
            # Calculate position size based on risk
            price_difference = abs(current_price - stop_loss_price)
            if price_difference == 0:
                return 0
                
            position_size = risk_amount / price_difference
            return round(position_size)
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0 