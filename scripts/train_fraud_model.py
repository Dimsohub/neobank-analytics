import duckdb
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Connect to MotherDuck
MOTHERDUCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRpbXNvbWFpbEBnbWFpbC5jb20iLCJtZFJlZ2lvbiI6ImF3cy1ldS1jZW50cmFsLTEiLCJzZXNzaW9uIjoiZGltc29fZGltc29tYWlsX2I2NGI5ZjgxLTNmOTQtNDA4Mi04ZDA2LTUxMTAxMDljZjQ3NSIsInBhdCI6IkpFZjdvbktNVmFjdHpzN1JUWmFlUDRNZVJFaGhCa1luU1hRSW9YSkJhSDQiLCJ1c2VySWQiOiJiNjRiOWY4MS0zZjk0LTQwODItOGQwNi01MTEwMTA5Y2Y0NzUiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3OTQ0MDAwMjd9.zXADhkhfdxS-kBefxr2tNM27adL-9HeRVEdOzQryh9w"
con = duckdb.connect(f"md:neobank?motherduck_token={MOTHERDUCK_TOKEN}")

print("Fetching data for training...")
# Fetch a sample of data to train on
query = """
    SELECT amount_usd, is_fraud_flag
    FROM main.fct_transactions
    WHERE transaction_at <= '2026-03-31'
    LIMIT 200000
"""
df = con.execute(query).fetchdf()

# Features and Target
X = df[['amount_usd']]
y = df['is_fraud_flag']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Random Forest model...")
# We use class_weight='balanced' because fraud is only 2.5% of the data
model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the model
model_path = os.path.join(os.path.dirname(__file__), '..', 'streamlit_app', 'fraud_model.pkl')
joblib.dump(model, model_path)
print(f"✅ Model saved to {model_path}")