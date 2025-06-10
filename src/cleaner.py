import os

def clean_data(df):
    # Basic cleaning: remove duplicates, drop NAs
    df = df.drop_duplicates()
    df = df.dropna(subset=['review_text', 'rating'])
    return df