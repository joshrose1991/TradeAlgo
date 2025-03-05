import tweepy
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterSentimentAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Twitter API client
        auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        auth.set_access_token(
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        self.api = tweepy.API(auth)
        self.vader = SentimentIntensityAnalyzer()
        
        logger.info("Twitter sentiment analyzer initialized")

    def get_tweets(self, symbol, count=100):
        """Get recent tweets for a symbol."""
        try:
            # Search for tweets containing the symbol
            search_query = f"${symbol} OR #{symbol} -filter:retweets"
            tweets = self.api.search_tweets(
                q=search_query,
                lang="en",
                count=count,
                tweet_mode="extended"
            )
            return tweets
        except Exception as e:
            logger.error(f"Error fetching tweets for {symbol}: {e}")
            return []

    def analyze_sentiment(self, text):
        """Analyze sentiment of text using both VADER and TextBlob."""
        try:
            # VADER sentiment
            vader_scores = self.vader.polarity_scores(text)
            
            # TextBlob sentiment
            blob = TextBlob(text)
            textblob_sentiment = blob.sentiment.polarity
            
            # Combine both scores (you can adjust the weights)
            combined_sentiment = (vader_scores['compound'] + textblob_sentiment) / 2
            
            return {
                'vader_scores': vader_scores,
                'textblob_score': textblob_sentiment,
                'combined_score': combined_sentiment
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None

    def get_symbol_sentiment(self, symbol, count=100):
        """Get overall sentiment for a symbol based on recent tweets."""
        try:
            tweets = self.get_tweets(symbol, count)
            if not tweets:
                return None
            
            sentiments = []
            for tweet in tweets:
                sentiment = self.analyze_sentiment(tweet.full_text)
                if sentiment:
                    sentiments.append(sentiment['combined_score'])
            
            if not sentiments:
                return None
            
            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Classify sentiment
            if avg_sentiment > 0.1:
                sentiment_label = "POSITIVE"
            elif avg_sentiment < -0.1:
                sentiment_label = "NEGATIVE"
            else:
                sentiment_label = "NEUTRAL"
            
            return {
                'symbol': symbol,
                'sentiment_score': avg_sentiment,
                'sentiment_label': sentiment_label,
                'tweet_count': len(tweets)
            }
        except Exception as e:
            logger.error(f"Error getting symbol sentiment for {symbol}: {e}")
            return None

    def get_trending_symbols(self, market="$SPX"):
        """Get trending stock symbols from Twitter."""
        try:
            # Search for tweets containing stock mentions
            search_query = f"{market} OR #stocks OR #trading -filter:retweets"
            tweets = self.api.search_tweets(
                q=search_query,
                lang="en",
                count=200,
                tweet_mode="extended"
            )
            
            # Extract stock symbols ($XXX)
            symbol_mentions = {}
            for tweet in tweets:
                text = tweet.full_text.upper()
                words = text.split()
                for word in words:
                    if word.startswith('$') and len(word) > 1:
                        symbol = word[1:]  # Remove the $ sign
                        if symbol.isalpha():  # Only consider alphabetic symbols
                            symbol_mentions[symbol] = symbol_mentions.get(symbol, 0) + 1
            
            # Sort by mention count
            trending = sorted(symbol_mentions.items(), key=lambda x: x[1], reverse=True)
            return trending[:10]  # Return top 10 trending symbols
        except Exception as e:
            logger.error(f"Error getting trending symbols: {e}")
            return [] 