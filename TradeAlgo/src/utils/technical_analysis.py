import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class TechnicalAnalyzer:
    @staticmethod
    def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
        """Calculate MACD (Moving Average Convergence Divergence)."""
        # Convert prices to numpy array
        prices = np.array(prices)
        
        # Calculate EMAs
        fast_ema = pd.Series(prices).ewm(span=fast_period, adjust=False).mean()
        slow_ema = pd.Series(prices).ewm(span=slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = fast_ema - slow_ema
        
        # Calculate signal line
        signal_line = pd.Series(macd_line).ewm(span=signal_period, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line.tolist(),
            'signal_line': signal_line.tolist(),
            'histogram': histogram.tolist()
        }
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI (Relative Strength Index)."""
        # Convert prices to numpy array
        prices = np.array(prices)
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Calculate gains (positive changes) and losses (negative changes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gains = pd.Series(gains).rolling(window=period).mean()
        avg_losses = pd.Series(losses).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # Fill NaN values with 50 (neutral)
        rsi = rsi.fillna(50)
        
        return rsi.tolist()
    
    @staticmethod
    def calculate_bollinger_bands(prices, volumes, period=20, num_std=2):
        """Calculate Bollinger Bands with volume weighting."""
        df = pd.DataFrame({'price': prices, 'volume': volumes})
        
        # Calculate volume-weighted moving average
        vwma = (df['price'] * df['volume']).rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
        
        # Calculate standard deviation
        std = df['price'].rolling(window=period).std()
        
        return {
            'middle': vwma.tolist(),
            'upper': (vwma + num_std * std).tolist(),
            'lower': (vwma - num_std * std).tolist(),
            'bandwidth': ((vwma + num_std * std) - (vwma - num_std * std)).tolist()
        }

    @staticmethod
    def calculate_obv(prices, volumes):
        """Calculate On-Balance Volume (OBV)."""
        obv = [volumes[0]]
        
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif prices[i] < prices[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        # Calculate OBV moving average for signal line
        obv_ma = pd.Series(obv).rolling(window=20).mean()
        
        return {
            'obv': obv,
            'obv_ma': obv_ma.tolist()
        }

    @staticmethod
    def calculate_ichimoku(prices, volumes):
        """Calculate Ichimoku Cloud components."""
        highs = pd.Series(prices).rolling(window=9).max()
        lows = pd.Series(prices).rolling(window=9).min()
        
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (highs + lows) / 2
        
        # Kijun-sen (Base Line)
        highs_26 = pd.Series(prices).rolling(window=26).max()
        lows_26 = pd.Series(prices).rolling(window=26).min()
        kijun_sen = (highs_26 + lows_26) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B)
        highs_52 = pd.Series(prices).rolling(window=52).max()
        lows_52 = pd.Series(prices).rolling(window=52).min()
        senkou_span_b = ((highs_52 + lows_52) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        chikou_span = pd.Series(prices).shift(-26)
        
        return {
            'tenkan_sen': tenkan_sen.tolist(),
            'kijun_sen': kijun_sen.tolist(),
            'senkou_span_a': senkou_span_a.tolist(),
            'senkou_span_b': senkou_span_b.tolist(),
            'chikou_span': chikou_span.tolist()
        }

    @staticmethod
    def calculate_atr(prices, period=14):
        """Calculate Average True Range for volatility."""
        high = pd.Series(prices).rolling(window=2).max()
        low = pd.Series(prices).rolling(window=2).min()
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - prices)
        tr3 = abs(low - prices)
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = true_range.rolling(window=period).mean()
        
        return atr.tolist()

    @staticmethod
    def calculate_volume_profile(prices, volumes, num_bins=10):
        """Calculate Volume Profile."""
        # Create price bins
        price_bins = np.linspace(min(prices), max(prices), num_bins+1)
        
        # Calculate volume for each price level
        volume_profile = []
        for i in range(len(price_bins)-1):
            mask = (np.array(prices) >= price_bins[i]) & (np.array(prices) < price_bins[i+1])
            volume_profile.append({
                'price_level': (price_bins[i] + price_bins[i+1]) / 2,
                'volume': sum(np.array(volumes)[mask])
            })
        
        # Find Point of Control (price level with highest volume)
        poc = max(volume_profile, key=lambda x: x['volume'])
        
        return {
            'profile': volume_profile,
            'poc': poc
        }

    @staticmethod
    def calculate_linear_regression(prices, period=20):
        """Calculate linear regression channel and related statistics."""
        df = pd.DataFrame({'price': prices, 'time': range(len(prices))})
        results = []
        
        for i in range(len(prices) - period + 1):
            window = df.iloc[i:i+period]
            X = window['time'].values.reshape(-1, 1)
            y = window['price'].values
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate predicted values
            y_pred = model.predict(X)
            
            # Calculate standard error
            std_err = np.sqrt(np.sum((y - y_pred) ** 2) / (len(y) - 2))
            
            # Calculate R-squared
            r_squared = model.score(X, y)
            
            results.append({
                'slope': model.coef_[0],
                'intercept': model.intercept_,
                'r_squared': r_squared,
                'std_err': std_err,
                'upper_band': y_pred + 2 * std_err,
                'lower_band': y_pred - 2 * std_err,
                'predicted': y_pred
            })
        
        # Combine results
        combined = {key: [] for key in results[0].keys()}
        for r in results:
            for key, value in r.items():
                if isinstance(value, np.ndarray):
                    combined[key].extend(value.tolist())
                else:
                    combined[key].append(value)
        
        return combined

    @staticmethod
    def calculate_zscore(prices, period=20):
        """Calculate Z-score for mean reversion analysis."""
        rolling_mean = pd.Series(prices).rolling(window=period).mean()
        rolling_std = pd.Series(prices).rolling(window=period).std()
        zscore = (prices - rolling_mean) / rolling_std
        
        return {
            'zscore': zscore.tolist(),
            'mean': rolling_mean.tolist(),
            'upper_band': (rolling_mean + 2 * rolling_std).tolist(),
            'lower_band': (rolling_mean - 2 * rolling_std).tolist()
        }

    @staticmethod
    def calculate_hurst_exponent(prices, lags=20):
        """Calculate Hurst Exponent to determine trend strength and mean reversion."""
        lags = min(lags, len(prices) // 2)
        tau = []
        lagvec = []
        
        # Step through the different lags
        for lag in range(2, lags):
            # Calculate price difference
            pp = np.subtract(prices[lag:], prices[:-lag])
            # Calculate variance
            lagvec.append(lag)
            tau.append(np.sqrt(np.std(pp)))
        
        # Calculate Hurst as slope of log-log plot
        m = np.polyfit(np.log10(lagvec), np.log10(tau), 1)
        hurst = m[0]
        
        return {
            'hurst': hurst,
            'interpretation': 'trend' if hurst > 0.5 else 'mean_reverting'
        }

    @staticmethod
    def calculate_momentum_factors(prices, volumes, period=14):
        """Calculate various momentum factors."""
        returns = pd.Series(prices).pct_change()
        
        # Calculate Rate of Change (ROC)
        roc = (prices[-1] / prices[-period] - 1) * 100
        
        # Calculate Money Flow Index (MFI)
        typical_price = pd.Series(prices)
        money_flow = typical_price * volumes
        
        positive_flow = []
        negative_flow = []
        
        for i in range(1, len(typical_price)):
            if typical_price[i] > typical_price[i-1]:
                positive_flow.append(money_flow[i])
                negative_flow.append(0)
            elif typical_price[i] < typical_price[i-1]:
                negative_flow.append(money_flow[i])
                positive_flow.append(0)
            else:
                positive_flow.append(0)
                negative_flow.append(0)
        
        positive_mf = pd.Series(positive_flow).rolling(window=period).sum()
        negative_mf = pd.Series(negative_flow).rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        
        return {
            'roc': roc,
            'mfi': mfi.iloc[-1] if not pd.isna(mfi.iloc[-1]) else 50
        }

    @staticmethod
    def generate_signals(macd_data, rsi_data, bb_data, obv_data, ichimoku_data, atr_data, 
                        volume_profile, regression_data, zscore_data, hurst_data, 
                        momentum_data, current_price):
        """Generate trading signals based on all technical indicators."""
        signals = []
        
        # Get latest values
        latest_macd = macd_data['macd_line'][-1]
        latest_signal = macd_data['signal_line'][-1]
        latest_histogram = macd_data['histogram'][-1]
        latest_rsi = rsi_data[-1]
        
        # MACD signals
        if latest_macd > latest_signal:
            if latest_histogram > 0 and latest_histogram > macd_data['histogram'][-2]:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Strong',
                    'indicator': 'MACD',
                    'reason': 'MACD line above signal line with increasing histogram'
                })
            else:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Weak',
                    'indicator': 'MACD',
                    'reason': 'MACD line above signal line'
                })
        elif latest_macd < latest_signal:
            if latest_histogram < 0 and latest_histogram < macd_data['histogram'][-2]:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Strong',
                    'indicator': 'MACD',
                    'reason': 'MACD line below signal line with decreasing histogram'
                })
            else:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Weak',
                    'indicator': 'MACD',
                    'reason': 'MACD line below signal line'
                })
        
        # RSI signals
        if latest_rsi < 30:
            signals.append({
                'type': 'BUY',
                'strength': 'Strong' if latest_rsi < 20 else 'Weak',
                'indicator': 'RSI',
                'reason': f'Oversold RSI at {latest_rsi:.2f}'
            })
        elif latest_rsi > 70:
            signals.append({
                'type': 'SELL',
                'strength': 'Strong' if latest_rsi > 80 else 'Weak',
                'indicator': 'RSI',
                'reason': f'Overbought RSI at {latest_rsi:.2f}'
            })
        
        # Bollinger Bands signals
        if current_price < bb_data['lower'][-1]:
            signals.append({
                'type': 'BUY',
                'strength': 'Strong',
                'indicator': 'BB',
                'reason': 'Price below lower Bollinger Band'
            })
        elif current_price > bb_data['upper'][-1]:
            signals.append({
                'type': 'SELL',
                'strength': 'Strong',
                'indicator': 'BB',
                'reason': 'Price above upper Bollinger Band'
            })
        
        # OBV signals
        if obv_data['obv'][-1] > obv_data['obv_ma'][-1] and obv_data['obv'][-1] > obv_data['obv'][-2]:
            signals.append({
                'type': 'BUY',
                'strength': 'Strong',
                'indicator': 'OBV',
                'reason': 'Rising OBV above MA with increasing volume'
            })
        elif obv_data['obv'][-1] < obv_data['obv_ma'][-1] and obv_data['obv'][-1] < obv_data['obv'][-2]:
            signals.append({
                'type': 'SELL',
                'strength': 'Strong',
                'indicator': 'OBV',
                'reason': 'Falling OBV below MA with decreasing volume'
            })
        
        # Ichimoku Cloud signals
        current_price_above_cloud = (
            current_price > ichimoku_data['senkou_span_a'][-1] and 
            current_price > ichimoku_data['senkou_span_b'][-1]
        )
        current_price_below_cloud = (
            current_price < ichimoku_data['senkou_span_a'][-1] and 
            current_price < ichimoku_data['senkou_span_b'][-1]
        )
        
        if current_price_above_cloud and ichimoku_data['tenkan_sen'][-1] > ichimoku_data['kijun_sen'][-1]:
            signals.append({
                'type': 'BUY',
                'strength': 'Strong',
                'indicator': 'Ichimoku',
                'reason': 'Price above cloud with bullish TK cross'
            })
        elif current_price_below_cloud and ichimoku_data['tenkan_sen'][-1] < ichimoku_data['kijun_sen'][-1]:
            signals.append({
                'type': 'SELL',
                'strength': 'Strong',
                'indicator': 'Ichimoku',
                'reason': 'Price below cloud with bearish TK cross'
            })
        
        # Volume Profile signals
        if abs(current_price - volume_profile['poc']['price_level']) < atr_data[-1]:
            signals.append({
                'type': 'BUY' if current_price < volume_profile['poc']['price_level'] else 'SELL',
                'strength': 'Moderate',
                'indicator': 'Volume Profile',
                'reason': f'Price near high-volume node at {volume_profile["poc"]["price_level"]:.2f}'
            })
        
        # Linear Regression signals
        current_slope = regression_data['slope'][-1]
        current_r_squared = regression_data['r_squared'][-1]
        
        if current_slope > 0 and current_r_squared > 0.7:
            if current_price < regression_data['predicted'][-1]:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Strong' if current_r_squared > 0.85 else 'Moderate',
                    'indicator': 'Linear Regression',
                    'reason': f'Strong uptrend (R² = {current_r_squared:.2f}) with price below regression line'
                })
        elif current_slope < 0 and current_r_squared > 0.7:
            if current_price > regression_data['predicted'][-1]:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Strong' if current_r_squared > 0.85 else 'Moderate',
                    'indicator': 'Linear Regression',
                    'reason': f'Strong downtrend (R² = {current_r_squared:.2f}) with price above regression line'
                })
        
        # Z-Score signals
        current_zscore = zscore_data['zscore'][-1]
        if abs(current_zscore) > 2:
            signals.append({
                'type': 'BUY' if current_zscore < -2 else 'SELL',
                'strength': 'Strong' if abs(current_zscore) > 3 else 'Moderate',
                'indicator': 'Z-Score',
                'reason': f'Price deviation of {current_zscore:.2f} standard deviations'
            })
        
        # Hurst Exponent signals
        if hurst_data['hurst'] > 0.6:  # Strong trend
            signals.append({
                'type': 'BUY' if current_slope > 0 else 'SELL',
                'strength': 'Strong' if hurst_data['hurst'] > 0.7 else 'Moderate',
                'indicator': 'Hurst',
                'reason': f'Strong trending market (H = {hurst_data["hurst"]:.2f})'
            })
        elif hurst_data['hurst'] < 0.4:  # Strong mean reversion
            current_zscore = zscore_data['zscore'][-1]
            if abs(current_zscore) > 2:
                signals.append({
                    'type': 'BUY' if current_zscore < -2 else 'SELL',
                    'strength': 'Strong',
                    'indicator': 'Hurst',
                    'reason': f'Strong mean reversion potential (H = {hurst_data["hurst"]:.2f})'
                })
        
        # Momentum signals
        if momentum_data['roc'] > 5:  # Strong positive momentum
            signals.append({
                'type': 'BUY',
                'strength': 'Strong' if momentum_data['roc'] > 10 else 'Moderate',
                'indicator': 'Momentum',
                'reason': f'Strong positive momentum (ROC = {momentum_data["roc"]:.2f}%)'
            })
        elif momentum_data['roc'] < -5:  # Strong negative momentum
            signals.append({
                'type': 'SELL',
                'strength': 'Strong' if momentum_data['roc'] < -10 else 'Moderate',
                'indicator': 'Momentum',
                'reason': f'Strong negative momentum (ROC = {momentum_data["roc"]:.2f}%)'
            })
        
        # Money Flow Index signals
        mfi = momentum_data['mfi']
        if mfi < 20:
            signals.append({
                'type': 'BUY',
                'strength': 'Strong' if mfi < 10 else 'Moderate',
                'indicator': 'MFI',
                'reason': f'Oversold MFI at {mfi:.2f}'
            })
        elif mfi > 80:
            signals.append({
                'type': 'SELL',
                'strength': 'Strong' if mfi > 90 else 'Moderate',
                'indicator': 'MFI',
                'reason': f'Overbought MFI at {mfi:.2f}'
            })
        
        return signals 