import pandas as pd
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def get_sp500_symbols():
    """Get list of current S&P 500 symbols."""
    try:
        # Get S&P 500 table from Wikipedia
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        return df['Symbol'].tolist()
    except Exception as e:
        logger.error(f"Error fetching S&P 500 symbols: {e}")
        # Return a default list of major S&P 500 companies if fetch fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'BRK-B', 'JPM', 'V', 'XOM',
                'UNH', 'JNJ', 'WMT', 'MA', 'PG', 'HD', 'CVX', 'BAC', 'ABBV', 'PFE']

def filter_tradable_symbols(alpaca_client, symbols):
    """Filter symbols that are tradable on Alpaca."""
    tradable_symbols = []
    for symbol in symbols:
        try:
            # Check if the asset is tradable
            asset = alpaca_client.trading_client.get_asset(symbol)
            if asset.tradable:
                tradable_symbols.append(symbol)
        except Exception as e:
            logger.warning(f"Symbol {symbol} not available on Alpaca: {e}")
            continue
    return tradable_symbols 