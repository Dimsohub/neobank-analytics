import duckdb
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = "md:neobank?motherduck_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRpbXNvbWFpbEBnbWFpbC5jb20iLCJtZFJlZ2lvbiI6ImF3cy1ldS1jZW50cmFsLTEiLCJzZXNzaW9uIjoiZGltc29fZGltc29tYWlsX2I2NGI5ZjgxLTNmOTQtNDA4Mi04ZDA2LTUxMTAxMDljZjQ3NSIsInBhdCI6IkpFZjdvbktNVmFjdHpzN1JUWmFlUDRNZVJFaGhCa1luU1hRSW9YSkJhSDQiLCJ1c2VySWQiOiJiNjRiOWY4MS0zZjk0LTQwODItOGQwNi01MTEwMTA5Y2Y0NzUiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3OTQ0MDAwMjd9.zXADhkhfdxS-kBefxr2tNM27adL-9HeRVEdOzQryh9w"
USERS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'users.csv')
TRANSACTIONS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'transactions.csv')

def load_data():
    print(f"Connecting to DuckDB at: {DB_PATH}")
    con = duckdb.connect(DB_PATH)
    
    print("Reading users.csv...")
    df_users = pd.read_csv(USERS_CSV_PATH)
    df_users = df_users.astype({'user_id': 'int64', 'avg_spend_tier': 'float64'})
    df_users['account_created_at'] = pd.to_datetime(df_users['account_created_at'])
    for col in df_users.columns:
        if df_users[col].dtype == 'string':
            df_users[col] = df_users[col].astype(object)

    print("Writing to DuckDB table 'raw_users'...")
    con.execute("CREATE OR REPLACE TABLE raw_users AS SELECT * FROM df_users")
    
    print("Reading transactions.csv...")
    df_tx = pd.read_csv(TRANSACTIONS_CSV_PATH)
    df_tx = df_tx.astype({'transaction_id': 'int64', 'user_id': 'int64', 'amount_usd': 'float64', 'converted_amount_usd': 'float64', 'is_fraud': 'int64'})
    df_tx['timestamp'] = pd.to_datetime(df_tx['timestamp'])
    for col in df_tx.columns:
        if df_tx[col].dtype == 'string':
            df_tx[col] = df_tx[col].astype(object)

    print("Writing to DuckDB table 'raw_transactions'...")
    con.execute("CREATE OR REPLACE TABLE raw_transactions AS SELECT * FROM df_tx")
    
    print(f"✅ Successfully loaded {con.execute('SELECT COUNT(*) FROM raw_users').fetchone()[0]} users and {con.execute('SELECT COUNT(*) FROM raw_transactions').fetchone()[0]} transactions.")
    con.close()

if __name__ == "__main__":
    load_data()