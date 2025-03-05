import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class MarketSentimentAnalyzer:
    # Key sector ETFs and their components
    SECTOR_ETFS = {
        'Technology': {
            'etf': 'XLK',
            'leaders': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'CSCO']
        },
        'Finance': {
            'etf': 'XLF',
            'leaders': ['JPM', 'BAC', 'WFC', 'GS', 'MS']
        },
        'Healthcare': {
            'etf': 'XLV',
            'leaders': ['UNH', 'JNJ', 'LLY', 'PFE', 'ABT']
        },
        'Consumer': {
            'etf': 'XLY',
            'leaders': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE']
        },
        'Energy': {
            'etf': 'XLE',
            'leaders': ['XOM', 'CVX', 'COP', 'SLB', 'EOG']
        },
        'Industrial': {
            'etf': 'XLI',
            'leaders': ['CAT', 'UPS', 'HON', 'GE', 'BA']
        }
    }

    def __init__(self, alpaca_client):
        """Initialize with Alpaca client for market data."""
        self.alpaca = alpaca_client
        
    def get_sector_for_symbol(self, symbol: str) -> str:
        """Determine which sector a symbol belongs to."""
        for sector, data in self.SECTOR_ETFS.items():
            if symbol in data['leaders']:
                return sector
            
        # If not found in leaders, need to query sector classification
        try:
            # This would typically use a proper sector classification API
            # For now, return None if not in our known leaders
            return None
        except Exception as e:
            logger.error(f"Error getting sector for {symbol}: {e}")
            return None

    def analyze_sector_strength(self, sector: str, timeframe: str = '1D') -> Dict:
        """Analyze the strength of a sector based on its ETF and leaders."""
        try:
            if sector not in self.SECTOR_ETFS:
                return None

            sector_data = self.SECTOR_ETFS[sector]
            etf = sector_data['etf']
            leaders = sector_data['leaders']
            
            # Get ETF performance
            etf_bars = self.alpaca.get_bars(etf, timeframe=timeframe, limit=20)
            if not etf_bars:
                return None
            
            etf_prices = [bar.close for bar in etf_bars]
            etf_volumes = [bar.volume for bar in etf_bars]
            
            # Calculate ETF metrics
            etf_return = (etf_prices[-1] / etf_prices[0] - 1) * 100
            etf_vol_change = (etf_volumes[-1] / np.mean(etf_volumes) - 1) * 100
            
            # Analyze sector leaders
            leaders_data = []
            for symbol in leaders:
                bars = self.alpaca.get_bars(symbol, timeframe=timeframe, limit=20)
                if bars:
                    prices = [bar.close for bar in bars]
                    volumes = [bar.volume for bar in bars]
                    
                    leaders_data.append({
                        'symbol': symbol,
                        'return': (prices[-1] / prices[0] - 1) * 100,
                        'vol_change': (volumes[-1] / np.mean(volumes) - 1) * 100
                    })
            
            # Calculate sector metrics
            leaders_returns = [d['return'] for d in leaders_data]
            leaders_vol_changes = [d['vol_change'] for d in leaders_data]
            
            # Calculate breadth
            advancing = sum(1 for ret in leaders_returns if ret > 0)
            declining = sum(1 for ret in leaders_returns if ret < 0)
            
            # Calculate sector sentiment score
            sentiment_score = self._calculate_sector_sentiment(
                etf_return, etf_vol_change,
                leaders_returns, leaders_vol_changes,
                advancing, declining
            )
            
            return {
                'sector': sector,
                'etf_symbol': etf,
                'etf_return': etf_return,
                'etf_volume_change': etf_vol_change,
                'breadth': {
                    'advancing': advancing,
                    'declining': declining,
                    'ratio': advancing / (advancing + declining)
                },
                'leaders_performance': leaders_data,
                'sentiment_score': sentiment_score,
                'strength': self._classify_strength(sentiment_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector {sector}: {e}")
            return None

    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze sentiment for a specific symbol based on its sector context."""
        try:
            # Get symbol's sector
            sector = self.get_sector_for_symbol(symbol)
            if not sector:
                logger.warning(f"Could not determine sector for {symbol}")
                return self._get_default_sentiment()
            
            # Get sector analysis
            sector_analysis = self.analyze_sector_strength(sector)
            if not sector_analysis:
                return self._get_default_sentiment()
            
            # Get symbol's own performance
            bars = self.alpaca.get_bars(symbol, timeframe='1D', limit=20)
            if not bars:
                return self._get_default_sentiment()
            
            prices = [bar.close for bar in bars]
            volumes = [bar.volume for bar in bars]
            
            symbol_return = (prices[-1] / prices[0] - 1) * 100
            symbol_vol_change = (volumes[-1] / np.mean(volumes) - 1) * 100
            
            # Calculate relative strength to sector
            relative_strength = symbol_return - sector_analysis['etf_return']
            
            # Calculate final sentiment score
            sentiment_score = self._calculate_symbol_sentiment(
                symbol_return,
                symbol_vol_change,
                relative_strength,
                sector_analysis['sentiment_score']
            )
            
            return {
                'symbol': symbol,
                'sector': sector,
                'score': sentiment_score,
                'strength': self._classify_strength(sentiment_score),
                'metrics': {
                    'return': symbol_return,
                    'volume_change': symbol_vol_change,
                    'relative_strength': relative_strength,
                    'sector_score': sector_analysis['sentiment_score']
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return self._get_default_sentiment()

    def _calculate_sector_sentiment(self, etf_return, etf_vol_change,
                                 leaders_returns, leaders_vol_changes,
                                 advancing, declining) -> float:
        """Calculate sector sentiment score."""
        try:
            # Weight components
            etf_score = np.tanh(etf_return / 10) * 0.3  # ETF performance (30%)
            vol_score = np.tanh(etf_vol_change / 50) * 0.2  # Volume change (20%)
            leaders_score = np.tanh(np.mean(leaders_returns) / 10) * 0.3  # Leaders performance (30%)
            breadth_score = (advancing / (advancing + declining) - 0.5) * 2 * 0.2  # Market breadth (20%)
            
            # Combine scores
            total_score = etf_score + vol_score + leaders_score + breadth_score
            
            # Normalize to [-1, 1]
            return np.clip(total_score, -1, 1)
            
        except Exception as e:
            logger.error(f"Error calculating sector sentiment: {e}")
            return 0.0

    def _calculate_symbol_sentiment(self, symbol_return, symbol_vol_change,
                                 relative_strength, sector_score) -> float:
        """Calculate symbol-specific sentiment score."""
        try:
            # Weight components
            return_score = np.tanh(symbol_return / 10) * 0.3  # Symbol performance (30%)
            vol_score = np.tanh(symbol_vol_change / 50) * 0.2  # Volume change (20%)
            rel_strength_score = np.tanh(relative_strength / 5) * 0.3  # Relative strength (30%)
            sector_influence = sector_score * 0.2  # Sector influence (20%)
            
            # Combine scores
            total_score = return_score + vol_score + rel_strength_score + sector_influence
            
            # Normalize to [-1, 1]
            return np.clip(total_score, -1, 1)
            
        except Exception as e:
            logger.error(f"Error calculating symbol sentiment: {e}")
            return 0.0

    def _classify_strength(self, score: float) -> str:
        """Classify sentiment strength based on score."""
        if score > 0.7:
            return 'Very Bullish'
        elif score > 0.3:
            return 'Bullish'
        elif score > -0.3:
            return 'Neutral'
        elif score > -0.7:
            return 'Bearish'
        else:
            return 'Very Bearish'

    def _get_default_sentiment(self) -> Dict:
        """Return default neutral sentiment when analysis fails."""
        return {
            'score': 0,
            'strength': 'Neutral',
            'metrics': {
                'return': 0,
                'volume_change': 0,
                'relative_strength': 0,
                'sector_score': 0
            }
        } 