import pandas as pd
from google_play_scraper import reviews, Sort
import os
from pathlib import Path  # Better path handling for Windows

def scrape_reviews(app_ids: list, app_names: list, review_count: int = 100) -> pd.DataFrame:
    all_reviews = []
    for app_id, app_name in zip(app_ids, app_names):
        try:
            result, _ = reviews(
                app_id,
                lang='en',
                country='et',
                sort=Sort.NEWEST,
                count=review_count,
                timeout=10  # Prevents hanging on Windows
            )
            for review in result:
                review['app_name'] = app_name
            all_reviews.extend(result)
        except Exception as e:
            print(f"Failed to scrape {app_name}: {str(e)}")
            continue  # Skip failed apps
    
    return pd.DataFrame(all_reviews)

def save_raw_data(df: pd.DataFrame, output_dir: str = 'data/raw'):
    """Windows-friendly path handling"""
    output_path = Path(output_dir) / 'reviews_raw.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Create dirs if missing
    df.to_csv(output_path, index=False, encoding='utf-8-sig')  # UTF-8 for Windows Excel
    print(f"Data saved to {output_path}")