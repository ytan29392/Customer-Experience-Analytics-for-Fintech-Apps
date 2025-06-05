import pandas as pd
from pathlib import Path
import os

def clean_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    clean_df = raw_df[['content', 'score', 'at', 'app_name']].copy()
    clean_df.columns = ['review', 'rating', 'date', 'bank']
    
    # Windows-friendly datetime parsing
    clean_df['date'] = pd.to_datetime(clean_df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    clean_df = clean_df.dropna(subset=['date', 'review'])  # Drop rows with invalid dates
    
    # Text cleaning optimized for Windows
    clean_df['review'] = (
        clean_df['review']
        .str.encode('utf-8', errors='ignore')  # Handle encoding issues
        .str.decode('utf-8')
        .str.lower()
        .str.replace(r'[^\w\s]', '', regex=True)
    )
    
    return clean_df

def save_clean_data(clean_df: pd.DataFrame, output_dir: str = 'data/processed'):
    output_path = Path(output_dir) / 'reviews_clean.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(output_path, index=False, encoding='utf-8-sig')  # Excel-compatible
    print(f"Cleaned data saved to {output_path}")

if __name__ == '__main__':
    raw_path = Path('data/raw/reviews_raw.csv')
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data not found at {raw_path}")
    
    raw_df = pd.read_csv(raw_path)
    cleaned_df = clean_data(raw_df)
    save_clean_data(cleaned_df)