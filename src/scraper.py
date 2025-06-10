from google_play_scraper import Sort, reviews
from datetime import datetime
import pandas as pd

def scrape_bank(app_ids, app_names, review_count=5000):
    all_reviews = []
    
    for app_id, bank_name in zip(app_ids, app_names):
        try:
            print(f"Fetching {bank_name} reviews...")
            results, _ = reviews(app_id, lang='en', country='et',
                                 sort=Sort.NEWEST, count=5000)
            seen = set()
            for r in results:
                text = r['content'].strip()
                date = r['at'].strftime('%Y-%m-%d')
                key = (text, date, r['score'])
                if key not in seen:
                    seen.add(key)
                    all_reviews.append({
                        'review_text': text,
                        'rating': r['score'],
                        'date': date,
                        'bank_name': bank_name,
                        'source': 'Google Play'
                    })
        except Exception as ex:
            print(f"Failed to fetch {bank_name}: {ex}")
    
    return pd.DataFrame(all_reviews)
