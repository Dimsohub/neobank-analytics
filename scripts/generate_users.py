"""
scripts/generate_users.py
Purpose: Generate a synthetic user base for a neobank.
Includes user segments, creation dates, and primary country.
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime
import random
import os

# Initialize Faker and set random seeds for reproducibility
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# --- CONFIGURATION ---
NUM_USERS = 50000 
START_DATE = datetime(2024, 10, 1)
END_DATE = datetime(2026, 3, 31)

COUNTRIES = ['USA', 'UK', 'Germany', 'Poland', 'Ukraine', 'France', 'Spain', 'Canada']
COUNTRY_PROBS = [0.25, 0.15, 0.15, 0.10, 0.10, 0.10, 0.08, 0.07]

SEGMENTS = ['Standard', 'Premium', 'VIP']
SEGMENT_PROBS = [0.70, 0.25, 0.05]

def generate_users(num_users):
    """Generate a DataFrame of synthetic users."""
    
    print(f"Generating {num_users} users...")
    user_ids = list(range(1, num_users + 1))
    
    # Generate random registration dates (vectorized for speed)
    start_ts = START_DATE.timestamp()
    end_ts = END_DATE.timestamp()
    random_tss = np.random.uniform(start_ts, end_ts, num_users)
    created_dates = pd.to_datetime(random_tss, unit='s')
    
    # Assign segments and countries
    segments = np.random.choice(SEGMENTS, size=num_users, p=SEGMENT_PROBS)
    countries = np.random.choice(COUNTRIES, size=num_users, p=COUNTRY_PROBS)
    
    # Assign spend tier based on segment
    spend_tiers = np.zeros(num_users)
    std_mask = segments == 'Standard'
    prem_mask = segments == 'Premium'
    vip_mask = segments == 'VIP'
    
    spend_tiers[std_mask] = np.random.uniform(0.5, 1.2, std_mask.sum())
    spend_tiers[prem_mask] = np.random.uniform(1.2, 2.5, prem_mask.sum())
    spend_tiers[vip_mask] = np.random.uniform(2.5, 4.0, vip_mask.sum())
    
    # Create DataFrame
    df = pd.DataFrame({
        'user_id': user_ids,
        'account_created_at': created_dates,
        'user_segment': segments,
        'primary_country': countries,
        'avg_spend_tier': np.round(spend_tiers, 2)
    })
    
    # Sort by creation date and reassign IDs
    df = df.sort_values('account_created_at').reset_index(drop=True)
    df['user_id'] = range(1, num_users + 1)
    
    return df

if __name__ == "__main__":
    users_df = generate_users(NUM_USERS)
    
        # Get absolute path to the project root to avoid path errors
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(BASE_DIR, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'users.csv')
    # Save with utf-8 encoding and explicit date format
    users_df.to_csv(output_path, index=False, encoding='utf-8', date_format='%Y-%m-%d %H:%M:%S')
    
    print(f"✅ Generated {len(users_df)} users. Saved to {output_path}")
    print("\n--- First 3 rows ---")
    print(users_df.head(3))