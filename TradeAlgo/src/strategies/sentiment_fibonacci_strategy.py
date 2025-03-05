from ..api.alpaca_client import AlpacaClient
from ..utils.sentiment_analyzer import TwitterSentimentAnalyzer
from ..utils.fibonacci import FibonacciAnalyzer
from ..utils.technical_analysis import TechnicalAnalyzer
from ..utils.market_sentiment import MarketSentimentAnalyzer
from ..utils.technical_indicators import TechnicalIndicators
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentFibonacciStrategy:
    def __init__(self, alpaca_client):
        """Initialize strategy with required components."""
        self.alpaca = alpaca_client
        self.fibonacci = FibonacciAnalyzer()
        self.sentiment = MarketSentimentAnalyzer(alpaca_client)
        self.technical = TechnicalIndicators()
        logger.info("Strategy initialized")

    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze a symbol using sentiment, technical, and Fibonacci analysis."""
        try:
            # Get market sentiment analysis
            sentiment_analysis = self.sentiment.analyze_symbol(symbol)
            if not sentiment_analysis:
                logger.warning(f"Could not get sentiment analysis for {symbol}")
                return None
                
            # Get historical data for technical analysis
            bars = self.alpaca.get_bars(symbol, timeframe='1D', limit=100)
            if not bars:
                logger.warning(f"Could not get price data for {symbol}")
                return None
                
            prices = [bar.close for bar in bars]
            highs = [bar.high for bar in bars]
            lows = [bar.low for bar in bars]
            volumes = [bar.volume for bar in bars]
            
            # Calculate Fibonacci levels
            fib_levels = self.fibonacci.calculate_levels(highs[-20:], lows[-20:])
            current_price = prices[-1]
            
            # Get technical signals
            technical_signals = self.technical.calculate_all_signals(
                prices, volumes, highs, lows
            )
            
            # Combine analyses
            return {
                'symbol': symbol,
                'sentiment': sentiment_analysis,
                'fibonacci': {
                    'levels': fib_levels,
                    'current_price': current_price,
                    'nearest_level': self.fibonacci.find_nearest_level(current_price, fib_levels)
                },
                'technical': technical_signals
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
            
    def generate_trade_decision(self, analysis: Dict) -> Optional[Dict]:
        """Generate a trade decision based on combined analysis."""
        try:
            if not analysis:
                return None
                
            sentiment_score = analysis['sentiment']['score']
            sentiment_strength = analysis['sentiment']['strength']
            
            current_price = analysis['fibonacci']['current_price']
            nearest_level = analysis['fibonacci']['nearest_level']
            fib_levels = analysis['fibonacci']['levels']
            
            technical_signals = analysis['technical']
            
            # Base confidence on sentiment score
            confidence = abs(sentiment_score)
            
            # Determine trade direction
            if sentiment_score > 0:
                direction = 'buy'
                # Check if price is near support
                if nearest_level['type'] == 'support' and \
                   abs(current_price - nearest_level['price']) / current_price < 0.02:
                    confidence *= 1.2  # Boost confidence for buying near support
            else:
                direction = 'sell'
                # Check if price is near resistance
                if nearest_level['type'] == 'resistance' and \
                   abs(current_price - nearest_level['price']) / current_price < 0.02:
                    confidence *= 1.2  # Boost confidence for selling near resistance
                    
            # Adjust confidence based on technical signals
            if technical_signals['trend_strength'] > 0.7:
                confidence *= 1.1  # Strong trend
            if technical_signals['volume_trend'] > 0:
                confidence *= 1.1  # Confirming volume
                
            # Set stop loss and take profit based on Fibonacci levels
            if direction == 'buy':
                stop_loss = next((level['price'] for level in fib_levels 
                                if level['price'] < current_price), current_price * 0.98)
                take_profit = next((level['price'] for level in fib_levels 
                                  if level['price'] > current_price), current_price * 1.02)
            else:
                stop_loss = next((level['price'] for level in fib_levels 
                                if level['price'] > current_price), current_price * 1.02)
                take_profit = next((level['price'] for level in fib_levels 
                                  if level['price'] < current_price), current_price * 0.98)
                
            # Only generate trade if confidence exceeds threshold
            if confidence < 0.5:
                return None
                
            return {
                'symbol': analysis['symbol'],
                'direction': direction,
                'confidence': confidence,
                'current_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'sentiment': sentiment_strength,
                'nearest_fib_level': nearest_level,
                'technical_signals': technical_signals
            }
            
        except Exception as e:
            logger.error(f"Error generating trade decision: {e}")
            return None
            
    def calculate_position_size(self, account_value: float, risk_per_trade: float,
                              current_price: float, stop_loss: float) -> int:
        """Calculate position size based on risk management rules."""
        try:
            # Calculate dollar risk per trade (default 2% of account)
            max_risk_amount = account_value * (risk_per_trade or 0.02)
            
            # Calculate per-share risk
            per_share_risk = abs(current_price - stop_loss)
            
            # Calculate number of shares based on risk
            shares = int(max_risk_amount / per_share_risk)
            
            # Ensure minimum position size
            min_position_value = 25000  # Minimum position value
            min_shares = int(min_position_value / current_price)
            
            return max(shares, min_shares)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0

    def run(self, symbols=None):
        """Run the strategy on a list of symbols."""
        try:
            # If no symbols provided, get trending symbols
            if not symbols:
                trending = self.sentiment.get_trending_symbols()
                symbols = [symbol for symbol, _ in trending]
            
            # Get account information
            account = self.alpaca.get_account()
            if not account:
                logger.error("Could not get account information")
                return False
            
            # Calculate maximum positions based on available buying power
            max_positions = min(
                int(float(account.buying_power) / 25000),  # Assume minimum $25k per position
                int(os.getenv('MAX_POSITIONS', 5))  # Or use configured max positions
            )
            
            # Get current positions
            current_positions = self.alpaca.get_open_positions()
            current_symbols = [p.symbol for p in current_positions]
            
            # Calculate how many new positions we can take
            available_positions = max_positions - len(current_positions)
            
            if available_positions <= 0:
                logger.info("Maximum number of positions reached")
                return True
            
            # Analyze each symbol
            potential_trades = []
            for symbol in symbols:
                # Skip if we already have a position in this symbol
                if symbol in current_symbols:
                    continue
                
                # Analyze the symbol
                analysis = self.analyze_symbol(symbol)
                if not analysis:
                    continue
                
                # Generate trade decision
                decision = self.generate_trade_decision(analysis)
                if not decision or decision['action'] == 'HOLD':
                    continue
                
                # Add to potential trades if confidence is high enough
                if decision['confidence'] >= 0.7:
                    potential_trades.append(decision)
            
            # Sort potential trades by confidence
            potential_trades.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Execute top trades up to available positions
            executed_trades = 0
            for trade in potential_trades[:available_positions]:
                order = self.execute_trade(trade)
                if order:
                    logger.info(f"Executed {trade['action']} order for {trade['symbol']}")
                    executed_trades += 1
            
            logger.info(f"Executed {executed_trades} new trades")
            return True
            
        except Exception as e:
            logger.error(f"Error running strategy: {e}")
            return False 