# import oracledb
# import pandas as pd
# from pathlib import Path
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class OracleDB:
#     def init(self):
#         self.conn = oracledb.connect(
#             user=os.getenv("ORACLE_USER"),
#             password=os.getenv("ORACLE_PASSWORD"),
#             dsn=os.getenv("ORACLE_DSN")
#         )
    
#     def create_tables(self):
#         with self.conn.cursor() as cursor:
#             # Create BANKS table
#             cursor.execute("""
#                 CREATE TABLE banks (
#                     bank_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
#                     bank_name VARCHAR2(100) NOT NULL
#                 )
#             """)
            
#             # Create REVIEWS table
#             cursor.execute("""
#                 CREATE TABLE reviews (
#                     review_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
#                     bank_id NUMBER REFERENCES banks(bank_id),
#                     review_text CLOB,
#                     rating NUMBER,
#                     review_date DATE,
#                     sentiment_score FLOAT,
#                     sentiment_label VARCHAR2(20),
#                     keywords VARCHAR2(200)
#                 )
#             """)
#             self.conn.commit()
    
#     def insert_data(self, df: pd.DataFrame):
#         with self.conn.cursor() as cursor:
#             # Insert banks and get their IDs
#             bank_ids = {}
#             for bank in df['bank'].unique():
#                 cursor.execute(
#                     "INSERT INTO banks (bank_name) VALUES (:1) RETURNING bank_id INTO :2",
#                     [bank, cursor.var(int)]
#                 )
#                 bank_ids[bank] = cursor.fetchone()[0]
            
#             # Insert reviews
#             for _, row in df.iterrows():
#                 cursor.execute(
#                     """
#                     INSERT INTO reviews (
#                         bank_id, review_text, rating, review_date,
#                         sentiment_score, sentiment_label, keywords
#                     ) VALUES (
#                         :1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), :5, :6, :7
#                     )
#                     """,
#                     [
#                         bank_ids[row['bank']],
#                         row['review'],
#                         row['rating'],
#                         row['date'],
#                         row['sentiment_score'],
#                         row['sentiment_label'],
#                         ', '.join(row['keywords']) if isinstance(row['keywords'], list) else row['keywords']
#                     ]
#                 )
#             self.conn.commit()
    
#     def close(self):
#         self.conn.close()

# if __name__ == "__main__":
#     # Load analyzed data
#     df = pd.read_csv(Path("../data/processed/reviews_final.csv"))
    
#     # Initialize and populate database
#     db = OracleDB()
#     try:
#         db.create_tables()
#         db.insert_data(df)
#         print("Data successfully loaded into Oracle!")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         db.close()






# src/db_handler.py

import oracledb
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class OracleDB:
    def __init__(self):
        self.conn = oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )

    def create_tables(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE banks (
                        bank_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        bank_name VARCHAR2(100) NOT NULL UNIQUE
                    )
                """)
            except oracledb.DatabaseError as e:
                if "ORA-00955" in str(e):
                    print("Table 'banks' already exists.")
                else:
                    raise

            try:
                cursor.execute("""
                    CREATE TABLE reviews (
                        review_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        bank_id NUMBER REFERENCES banks(bank_id),
                        review_text CLOB,
                        rating NUMBER,
                        review_date DATE,
                        sentiment_score FLOAT,
                        sentiment_label VARCHAR2(20),
                        keywords VARCHAR2(1000)
                    )
                """)
            except oracledb.DatabaseError as e:
                if "ORA-00955" in str(e):
                    print("Table 'reviews' already exists.")
                else:
                    raise

        self.conn.commit()

    def insert_data(self, df: pd.DataFrame):
        with self.conn.cursor() as cursor:
            bank_ids = {}

            for bank in df['bank'].unique():
                try:
                    id_var = cursor.var(oracledb.NUMBER)
                    cursor.execute(
                        "INSERT INTO banks (bank_name) VALUES (:1) RETURNING bank_id INTO :2",
                        [bank, id_var]
                    )
                    bank_ids[bank] = int(id_var.getvalue()[0])
                except oracledb.IntegrityError:
                    cursor.execute("SELECT bank_id FROM banks WHERE bank_name = :1", [bank])
                    bank_ids[bank] = cursor.fetchone()[0]

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