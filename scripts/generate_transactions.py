"""
scripts/generate_transactions.py
Purpose: Generate 1.5 million synthetic transactions with realistic patterns and fraud logic.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

# --- CONFIGURATION ---
NUM_TRANSACTIONS = 1500000

# Define absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'users.csv')
TRANSACTIONS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'transactions.csv')

# Transaction properties
TRANSACTION_TYPES = ['card_payment', 'p2p_transfer', 'atm_withdrawal', 'subscription']
TYPE_PROBS = [0.65, 0.20, 0.10, 0.05]

CATEGORIES = ['Groceries', 'Travel', 'Entertainment', 'FinTech/Crypto', 'Utilities', 'Health', 'Education', 'Retail']
CATEGORY_PROBS = [0.30, 0.15, 0.15, 0.08, 0.12, 0.10, 0.05, 0.05]

MERCHANTS = {
    'Groceries': ['Walmart', 'Tesco', 'Whole Foods', 'Local Market'],
    'Travel': ['Uber', 'Booking.com', 'Lufthansa', 'Airbnb'],
    'Entertainment': ['Netflix', 'Spotify', 'Steam', 'Cinema'],
    'FinTech/Crypto': ['Binance', 'Coinbase', 'Revolut', 'PayPal'],
    'Utilities': ['Electric Co', 'Water Supply', 'Internet Provider'],
    'Health': ['Pharmacy', 'Gym', 'Clinic'],
    'Education': ['Coursera', 'Udemy', 'University'],
    'Retail': ['Amazon', 'eBay', 'Zara', 'H&M']
}

DEVICES = ['mobile', 'desktop', 'tablet']
DEVICE_PROBS = [0.70, 0.20, 0.10]

CURRENCIES = ['USD', 'EUR', 'GBP', 'PLN', 'UAH']
CURRENCY_PROBS = [0.40, 0.25, 0.15, 0.10, 0.10]

def generate_transactions():
    print(f"Loading users from {USERS_CSV_PATH}...")
    df_users = pd.read_csv(USERS_CSV_PATH)
    df_users['account_created_at'] = pd.to_datetime(df_users['account_created_at'])
    
    print(f"Generating {NUM_TRANSACTIONS} transactions (this may take a few seconds)...")
    
    # 1. Assign a random user to each transaction
    # We use np.random.choice to pick user indices
    user_indices = np.random.randint(0, len(df_users), NUM_TRANSACTIONS)
    
    # Create the base DataFrame
    df = pd.DataFrame({
        'transaction_id': range(1, NUM_TRANSACTIONS + 1),
        'user_id': df_users.iloc[user_indices]['user_id'].values,
        'user_created_at': df_users.iloc[user_indices]['account_created_at'].values,
        'user_country': df_users.iloc[user_indices]['primary_country'].values,
        'user_spend_tier': df_users.iloc[user_indices]['avg_spend_tier'].values
    })
    
    # 2. Generate Timestamps with realistic user churn (Exponential Decay)
    end_ts = datetime(2026, 3, 31).timestamp()
    start_ts_array = pd.to_datetime(df['user_created_at']).apply(lambda x: x.timestamp()).values
    
    # Exponential distribution simulates realistic churn (Revolut benchmarks)
    lifespans = np.random.exponential(scale=5.0, size=len(df_users)) + 1
    lifespans = np.clip(lifespans, 1, 18)
    user_lifespans = lifespans.astype(int)
    
    lifespan_map = dict(zip(df_users['user_id'], user_lifespans))
    df['user_lifespan_months'] = df['user_id'].map(lifespan_map)
    
    user_end_ts = start_ts_array + (df['user_lifespan_months'] * 2629743)
    
    random_ts = np.random.uniform(start_ts_array, user_end_ts)
    df['timestamp'] = pd.to_datetime(random_ts, unit='s')
    
    df = df.drop(columns=['user_lifespan_months'])
    
    # 3. Assign Transaction Types, Categories, Merchants, Devices, Currencies
    df['transaction_type'] = np.random.choice(TRANSACTION_TYPES, NUM_TRANSACTIONS, p=TYPE_PROBS)
    df['category'] = np.random.choice(CATEGORIES, NUM_TRANSACTIONS, p=CATEGORY_PROBS)
    df['device_type'] = np.random.choice(DEVICES, NUM_TRANSACTIONS, p=DEVICE_PROBS)
    df['currency'] = np.random.choice(CURRENCIES, NUM_TRANSACTIONS, p=CURRENCY_PROBS)
    
    # Assign merchant based on category
    df['merchant'] = df.apply(lambda row: np.random.choice(MERCHANTS[row['category']]), axis=1)
    
    # 4. Generate Amounts
    # Base amount follows a log-normal distribution (realistic for spending)
    base_amounts = np.random.lognormal(mean=3.5, sigma=1.0, size=NUM_TRANSACTIONS)
    # Multiply by user's spend tier
    df['amount_usd'] = np.round(base_amounts * df['user_spend_tier'], 2)
    # Add small random noise
    df['amount_usd'] = df['amount_usd'].clip(lower=1.0) # Minimum 1 USD
    
    # 5. Fraud Logic (Anomaly Detection)
    # 2.5% of transactions are fraudulent
    is_fraud = np.random.random(NUM_TRANSACTIONS) < 0.025
    
    # For fraud transactions:
    # - Amount is 3x to 5x higher
    # - Country is different from user's primary country
    # - Category is more likely to be FinTech/Crypto or Travel
    
    fraud_multiplier = np.random.uniform(3.0, 5.0, size=is_fraud.sum())
    df.loc[is_fraud, 'amount_usd'] = np.round(df.loc[is_fraud, 'amount_usd'] * fraud_multiplier, 2)
    
    # Assign random country to fraud transactions (simulating cross-border fraud)
    all_countries = ['USA', 'UK', 'Germany', 'Poland', 'Ukraine', 'France', 'Spain', 'Canada', 'Russia', 'Nigeria', 'Brazil']
    df.loc[is_fraud, 'country'] = np.random.choice(all_countries, size=is_fraud.sum())
    
    # For non-fraud, country matches user's primary country
    df.loc[~is_fraud, 'country'] = df.loc[~is_fraud, 'user_country']
    
    # Save the fraud flag
    df['is_fraud'] = is_fraud.astype(int)
    
    # 6. Status Logic
    # Default status is Success
    df['status'] = 'Success'
    
    # Fraud transactions are mostly blocked, but sometimes succeed (20%)
    fraud_blocked = is_fraud & (np.random.random(NUM_TRANSACTIONS) < 0.80)
    df.loc[fraud_blocked, 'status'] = 'Blocked_Fraud'
    
    # Non-fraud transactions can fail due to insufficient funds (3% chance)
    non_fraud_failed = ~is_fraud & (np.random.random(NUM_TRANSACTIONS) < 0.03)
    df.loc[non_fraud_failed, 'status'] = 'Failed_Insufficient_Funds'
    
    # 7. Converted Amount (for simplicity, 1:1 with USD for non-USD, real logic could use exchange rates)
    df['converted_amount_usd'] = df['amount_usd']
    
    # Clean up temporary columns
    df = df.drop(columns=['user_created_at', 'user_country', 'user_spend_tier'])
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    df_transactions = generate_transactions()
    
    print(f"Saving to {TRANSACTIONS_CSV_PATH}...")
    df_transactions.to_csv(TRANSACTIONS_CSV_PATH, index=False, encoding='utf-8', date_format='%Y-%m-%d %H:%M:%S')
    
    print(f"✅ Successfully generated {len(df_transactions)} transactions.")
    print("\n--- Fraud & Status Summary ---")
    print(df_transactions['status'].value_counts())
    print(f"Fraud rate: {df_transactions['is_fraud'].mean() * 100:.2f}%")
    print("\n--- First 3 rows ---")
    print(df_transactions.head(3))