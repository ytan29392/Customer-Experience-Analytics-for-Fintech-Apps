from src.scraper import scrape_reviews
def test_scraper():
    df = scrape_reviews(["com.cbe.mobile"], ["Test Bank"], review_count=1)
    assert not df.empty