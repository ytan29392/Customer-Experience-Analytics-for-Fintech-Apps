import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer 
from collections import defaultdict

def extract_keywords(df: pd.DataFrame, max_features: int = 100) -> pd.DataFrame:
  
    tfidf = TfidfVectorizer(stop_words='english', max_features=max_features)
    tfidf.fit(df['review'].fillna(''))  # Fit on reviews, filling NaNs with empty strings
        
    # Get keywords for each review
    review_keywords = []
    X = tfidf.transform(df['review'].fillna(''))  # Transform reviews, filling NaNs with empty strings
    feature_names = tfidf.get_feature_names_out()
    
    for i in range(len(df)):
        top_indices = X[i].toarray().flatten().argsort()[-3:][::-1]  # Top 3 keywords per review
        review_keywords.append([feature_names[idx] for idx in top_indices])
    
    df['keywords'] = review_keywords
    return df

def map_keywords_to_themes(df: pd.DataFrame) -> dict:
    
    theme_mapping = {
        'login': 'Account Access',
        'password': 'Account Access',
        'slow': 'Performance',
        'fast': 'Performance',
        'crash': 'Stability',
        'update': 'App Updates',
        'transfer': 'Transactions',
        'ui': 'User Interface'
    }
    
    bank_themes = defaultdict(list)
    
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        all_keywords = [kw for sublist in bank_df['keywords'] for kw in sublist]
        
        # Count theme occurrences
        theme_counts = defaultdict(int)
        for kw in all_keywords:
            theme = theme_mapping.get(kw, 'Other')
            theme_counts[theme] += 1
        
        bank_themes[bank] = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    return bank_themes