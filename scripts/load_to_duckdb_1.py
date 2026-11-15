"""
scripts/load_to_duckdb.py
Purpose: Safely load raw CSV data (users and transactions) into DuckDB with explicit data types.
"""
import duckdb
import pandas as pd
import os

# Define absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'neobank.duckdb')
USERS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'users.csv')
TRANSACTIONS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'transactions.csv')

def load_data():
    print(f"Connecting to DuckDB at: {DB_PATH}")
    con = duckdb.connect(DB_PATH)
    
    # --- 1. Load Users ---
    print("Reading users.csv...")
    df_users = pd.read_csv(USERS_CSV_PATH)
    
    # Enforce strict data types
    df_users['user_id'] = df_users['user_id'].astype('int64')
    df_users['account_created_at'] = pd.to_datetime(df_users['account_created_at'])
    df_users['avg_spend_tier'] = df_users['avg_spend_tier'].astype('float64')
    
    print("Writing to DuckDB table 'raw_users'...")
    con.execute("CREATE OR REPLACE TABLE raw_users AS SELECT * FROM df_users")
    
    # --- 2. Load Transactions ---
    print("Reading transactions.csv (this may take a moment)...")
    df_tx = pd.read_csv(TRANSACTIONS_CSV_PATH)
    
    # Enforce strict data types
    df_tx['transaction_id'] = df_tx['transaction_id'].astype('int64')
    df_tx['user_id'] = df_tx['user_id'].astype('int64')
    df_tx['timestamp'] = pd.to_datetime(df_tx['timestamp'])
    df_tx['amount_usd'] = df_tx['amount_usd'].astype('float64')
    df_tx['converted_amount_usd'] = df_tx['converted_amount_usd'].astype('float64')
    df_tx['is_fraud'] = df_tx['is_fraud'].astype('int64')
    
    print("Writing to DuckDB table 'raw_transactions'...")
    con.execute("CREATE OR REPLACE TABLE raw_transactions AS SELECT * FROM df_tx")
    
    # --- 3. Verification ---
    user_count = con.execute("SELECT COUNT(*) FROM raw_users").fetchone()[0]
    tx_count = con.execute("SELECT COUNT(*) FROM raw_transactions").fetchone()[0]
    
    print("\n✅ Loading completed successfully!")
    print(f" - raw_users: {user_count} rows")
    print(f" - raw_transactions: {tx_count} rows")
    
    con.close()

if __name__ == "__main__":
    load_data()