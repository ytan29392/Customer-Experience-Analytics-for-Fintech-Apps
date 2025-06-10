import oracledb
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv  # For secure credential management

# Load environment variables (create a .env file)
load_dotenv()

class OracleDB:
    def init(self):
        self.conn = oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )
    
    def create_tables(self):
        with self.conn.cursor() as cursor:
            # Create BANKS table
            cursor.execute("""
                CREATE TABLE banks (
                    bank_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    bank_name VARCHAR2(100) NOT NULL
                )
            """)
            
            # Create REVIEWS table
            cursor.execute("""
                CREATE TABLE reviews (
                    review_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    bank_id NUMBER REFERENCES banks(bank_id),
                    review_text CLOB,
                    rating NUMBER,
                    review_date DATE,
                    sentiment_score FLOAT,
                    sentiment_label VARCHAR2(20),
                    keywords VARCHAR2(200)
                )
            """)
            self.conn.commit()
    
    def insert_data(self, df: pd.DataFrame):
        with self.conn.cursor() as cursor:
            # Insert banks and get their IDs
            bank_ids = {}
            for bank in df['bank'].unique():
                cursor.execute(
                    "INSERT INTO banks (bank_name) VALUES (:1) RETURNING bank_id INTO :2",
                    [bank, cursor.var(int)]
                )
                bank_ids[bank] = cursor.fetchone()[0]
            
            # Insert reviews
            for _, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO reviews (
                        bank_id, review_text, rating, review_date,
                        sentiment_score, sentiment_label, keywords
                    ) VALUES (
                        :1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), :5, :6, :7
                    )
                    """,
                    [
                        bank_ids[row['bank']],
                        row['review'],
                        row['rating'],
                        row['date'],
                        row['sentiment_score'],
                        row['sentiment_label'],
                        ', '.join(row['keywords']) if isinstance(row['keywords'], list) else row['keywords']
                    ]
                )
            self.conn.commit()
    
    def close(self):
        self.conn.close()

if name == "main":
    # Load analyzed data from Task 2
    df = pd.read_csv(Path("../data/processed/reviews_final.csv"))
    
    # Initialize and populate database
    db = OracleDB()
    try:
        db.create_tables()
        db.insert_data(df)
        print("Data successfully loaded into Oracle!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()