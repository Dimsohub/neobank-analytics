import duckdb

# Connect to the CI test database
con = duckdb.connect("md:neobank_ci?motherduck_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRpbXNvbWFpbEBnbWFpbC5jb20iLCJtZFJlZ2lvbiI6ImF3cy1ldS1jZW50cmFsLTEiLCJzZXNzaW9uIjoiZGltc29fZGltc29tYWlsX2I2NGI5ZjgxLTNmOTQtNDA4Mi04ZDA2LTUxMTAxMDljZjQ3NSIsInBhdCI6IkpFZjdvbktNVmFjdHpzN1JUWmFlUDRNZVJFaGhCa1luU1hRSW9YSkJhSDQiLCJ1c2VySWQiOiJiNjRiOWY4MS0zZjk0LTQwODItOGQwNi01MTEwMTA5Y2Y0NzUiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3OTQ0MDAwMjd9.zXADhkhfdxS-kBefxr2tNM27adL-9HeRVEdOzQryh9w")

# Create raw_users table with test data
con.execute("""
    CREATE OR REPLACE TABLE raw_users AS 
    SELECT 1 as user_id, '2024-01-01'::timestamp as account_created_at, 'Standard' as user_segment, 'USA' as primary_country, 1.0 as avg_spend_tier
    UNION ALL
    SELECT 2 as user_id, '2024-01-02'::timestamp as account_created_at, 'Premium' as user_segment, 'UK' as primary_country, 2.0 as avg_spend_tier
""")

# Create raw_transactions table with test data
con.execute("""
    CREATE OR REPLACE TABLE raw_transactions AS 
    SELECT 1 as transaction_id, 1 as user_id, '2024-01-02'::timestamp as timestamp, 100.0 as amount_usd, 100.0 as converted_amount_usd, 'card_payment' as transaction_type, 'Groceries' as category, 'Walmart' as merchant, 'mobile' as device_type, 'USA' as country, 'Success' as status, 0 as is_fraud
    UNION ALL
    SELECT 2 as transaction_id, 2 as user_id, '2024-01-03'::timestamp as timestamp, 50.0 as amount_usd, 50.0 as converted_amount_usd, 'p2p_transfer' as transaction_type, 'Travel' as category, 'Uber' as merchant, 'desktop' as device_type, 'UK' as country, 'Success' as status, 0 as is_fraud
""")

print("✅ CI test tables created successfully!")