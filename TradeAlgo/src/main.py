import os
import logging
from dotenv import load_dotenv
from strategies.sentiment_fibonacci_strategy import SentimentFibonacciStrategy
from utils.sp500 import get_sp500_symbols, filter_tradable_symbols
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Set your Alpaca API keys
        os.environ['ALPACA_API_KEY'] = "PKPPJM2YUA2TLFFHV6OW"
        os.environ['ALPACA_SECRET_KEY'] = "9HjwRnheDOQA64Z2pil8oxDZKTWNgeSgIZJc606s"
        
        # Initialize strategy
        strategy = SentimentFibonacciStrategy()
        logger.info("Strategy initialized")
        
        # Get S&P 500 symbols and filter tradable ones
        sp500_symbols = get_sp500_symbols()
        tradable_symbols = filter_tradable_symbols(strategy.alpaca, sp500_symbols)
        logger.info(f"Found {len(tradable_symbols)} tradable S&P 500 symbols")
        
        # Define trading schedule
        market_open = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
        
        while True:
            now = datetime.now()
            
            # Check if market is open
            if now.weekday() < 5 and market_open.time() <= now.time() <= market_close.time():
                logger.info("Running strategy on S&P 500 symbols...")
                
                # Run the strategy on tradable S&P 500 symbols
                success = strategy.run(tradable_symbols)
                
                if success:
                    logger.info("Strategy execution completed successfully")
                else:
                    logger.error("Strategy execution failed")
                
                # Wait for 5 minutes before next iteration
                time.sleep(300)
            else:
                # Wait for next market open
                if now.time() > market_close.time():
                    next_run = (now + timedelta(days=1)).replace(
                        hour=market_open.hour,
                        minute=market_open.minute,
                        second=0,
                        microsecond=0
                    )
                else:
                    next_run = now.replace(
                        hour=market_open.hour,
                        minute=market_open.minute,
                        second=0,
                        microsecond=0
                    )
                
                sleep_seconds = (next_run - now).total_seconds()
                logger.info(f"Market is closed. Waiting for {sleep_seconds/3600:.2f} hours until next run")
                time.sleep(sleep_seconds)
    
    except KeyboardInterrupt:
        logger.info("Strategy stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main() 