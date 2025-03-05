# Sophisticated Options Trading Algorithm

A sophisticated trading algorithm that combines Twitter sentiment analysis, Fibonacci retracement levels, and technical analysis to make trading decisions. The algorithm uses the Alpaca API for executing trades.

## Features

- Twitter sentiment analysis using VADER and TextBlob
- Fibonacci retracement and extension level analysis
- Technical analysis with trend identification
- Risk management with position sizing
- Real-time market data integration
- Automated trading execution via Alpaca API

## Prerequisites

- Python 3.8+
- Alpaca trading account (with API keys)
- Twitter Developer account (with API keys)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/joshrose1991/TradeAlgo.git
cd TradeAlgo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
# Alpaca API Configuration
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Twitter API Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# Trading Configuration
RISK_PER_TRADE=0.02
MAX_POSITIONS=5
DEFAULT_STOP_LOSS_PCT=0.05
DEFAULT_TAKE_PROFIT_PCT=0.15
```

## Project Structure

```
TradeAlgo/
├── src/
│   ├── api/
│   │   └── alpaca_client.py
│   ├── models/
│   ├── strategies/
│   │   └── sentiment_fibonacci_strategy.py
│   ├── utils/
│   │   ├── sentiment_analyzer.py
│   │   └── fibonacci.py
│   └── main.py
├── tests/
├── config/
├── requirements.txt
└── README.md
```

## Usage

1. Start the trading algorithm:
```bash
python src/main.py
```

The algorithm will:
- Run during market hours (9:30 AM - 4:00 PM ET)
- Analyze specified symbols or find trending ones
- Execute trades based on sentiment and technical analysis
- Log all activities to `trading.log`

## Configuration

You can modify the trading parameters in the `.env` file:
- `RISK_PER_TRADE`: Maximum risk per trade (as a decimal)
- `MAX_POSITIONS`: Maximum number of simultaneous positions
- `DEFAULT_STOP_LOSS_PCT`: Default stop loss percentage
- `DEFAULT_TAKE_PROFIT_PCT`: Default take profit percentage

## Strategy Details

The algorithm combines multiple factors to make trading decisions:

1. **Sentiment Analysis**
   - Analyzes Twitter sentiment for trading symbols
   - Uses both VADER and TextBlob for sentiment scoring
   - Considers tweet volume and sentiment strength

2. **Technical Analysis**
   - Calculates Fibonacci retracement levels
   - Identifies support and resistance levels
   - Determines market trends using moving averages

3. **Risk Management**
   - Position sizing based on account equity
   - Stop loss and take profit orders
   - Maximum position limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. 