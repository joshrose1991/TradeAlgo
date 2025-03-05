import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FibonacciAnalyzer:
    def __init__(self):
        # Standard Fibonacci ratios
        self.fib_ratios = {
            'Extension_1.618': 1.618,
            'Extension_1.272': 1.272,
            'Retracement_1.000': 1.000,
            'Retracement_0.786': 0.786,
            'Retracement_0.618': 0.618,
            'Retracement_0.500': 0.500,
            'Retracement_0.382': 0.382,
            'Retracement_0.236': 0.236,
            'Retracement_0.000': 0.000
        }

    def calculate_fibonacci_levels(self, high_price, low_price, trend='uptrend'):
        """Calculate Fibonacci retracement and extension levels."""
        try:
            price_range = high_price - low_price
            levels = {}
            
            if trend == 'uptrend':
                # Calculate levels for uptrend
                for key, ratio in self.fib_ratios.items():
                    if 'Extension' in key:
                        levels[key] = high_price + (price_range * ratio)
                    else:
                        levels[key] = high_price - (price_range * ratio)
            else:
                # Calculate levels for downtrend
                for key, ratio in self.fib_ratios.items():
                    if 'Extension' in key:
                        levels[key] = low_price - (price_range * ratio)
                    else:
                        levels[key] = low_price + (price_range * ratio)
            
            return levels
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {e}")
            return None

    def find_swing_points(self, prices, window=20):
        """Find swing high and low points in price data."""
        try:
            highs = []
            lows = []
            
            for i in range(window, len(prices) - window):
                # Check for swing high
                if all(prices[i] > prices[j] for j in range(i-window, i)) and \
                   all(prices[i] > prices[j] for j in range(i+1, i+window+1)):
                    highs.append((i, prices[i]))
                
                # Check for swing low
                if all(prices[i] < prices[j] for j in range(i-window, i)) and \
                   all(prices[i] < prices[j] for j in range(i+1, i+window+1)):
                    lows.append((i, prices[i]))
            
            return {'highs': highs, 'lows': lows}
        except Exception as e:
            logger.error(f"Error finding swing points: {e}")
            return None

    def identify_trend(self, prices, window=20):
        """Identify the current trend using moving averages."""
        try:
            if len(prices) < window:
                return None
            
            # Calculate short and long-term moving averages
            short_ma = np.mean(prices[-window:])
            long_ma = np.mean(prices[-2*window:])
            
            # Determine trend
            if short_ma > long_ma:
                return 'uptrend'
            elif short_ma < long_ma:
                return 'downtrend'
            else:
                return 'sideways'
        except Exception as e:
            logger.error(f"Error identifying trend: {e}")
            return None

    def get_support_resistance(self, prices, levels):
        """Identify potential support and resistance levels."""
        try:
            support_levels = []
            resistance_levels = []
            current_price = prices[-1]
            
            for level_name, level_price in levels.items():
                if level_price < current_price:
                    support_levels.append((level_name, level_price))
                else:
                    resistance_levels.append((level_name, level_price))
            
            # Sort levels by price
            support_levels.sort(key=lambda x: x[1], reverse=True)
            resistance_levels.sort(key=lambda x: x[1])
            
            return {
                'support': support_levels,
                'resistance': resistance_levels,
                'current_price': current_price
            }
        except Exception as e:
            logger.error(f"Error getting support and resistance levels: {e}")
            return None

    def generate_trading_signals(self, current_price, levels, trend):
        """Generate trading signals based on Fibonacci levels."""
        try:
            signals = []
            
            # Get nearest support and resistance levels
            sr_levels = self.get_support_resistance(
                [current_price], 
                levels
            )
            
            if not sr_levels:
                return signals
            
            # Check for potential buy signals
            if trend == 'uptrend':
                for support_name, support_price in sr_levels['support']:
                    if 0.95 <= current_price/support_price <= 1.05:
                        signals.append({
                            'type': 'BUY',
                            'price': current_price,
                            'level': support_name,
                            'level_price': support_price,
                            'strength': 'Strong' if 'Retracement_0.618' in support_name else 'Moderate'
                        })
            
            # Check for potential sell signals
            elif trend == 'downtrend':
                for resistance_name, resistance_price in sr_levels['resistance']:
                    if 0.95 <= current_price/resistance_price <= 1.05:
                        signals.append({
                            'type': 'SELL',
                            'price': current_price,
                            'level': resistance_name,
                            'level_price': resistance_price,
                            'strength': 'Strong' if 'Retracement_0.618' in resistance_name else 'Moderate'
                        })
            
            return signals
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return [] 