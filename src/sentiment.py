from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze sentiment of reviews using VADER.
    Adds columns: 'sentiment_score' (compound score) and 'sentiment_label' (positive/neutral/negative).
    
    Args:
        df: DataFrame with 'review' column.
    
    Returns:
        DataFrame with sentiment columns added.
    """
    analyzer = SentimentIntensityAnalyzer()
    
    # Calculate sentiment scores
    df['sentiment_score'] = df['review'].apply(
        lambda x: analyzer.polarity_scores(x)['compound']
    )
    
    # Classify sentiment labels
    df['sentiment_label'] = df['sentiment_score'].apply(
        lambda score: 'positive' if score >= 0.05 else 'negative' if score <= -0.05 else 'neutral'
    )
    
    return df