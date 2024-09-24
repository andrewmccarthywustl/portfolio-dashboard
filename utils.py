import pandas as pd
import os

def load_transactions(csv_file):
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            return df.values.tolist()
        except Exception as e:
            print(f"Error loading transactions: {str(e)}")
    return []

def save_transactions_to_csv(csv_file, data):
    df = pd.DataFrame(data, columns=["Date", "Symbol", "Quantity", "Buy Price", "Current Price", "Last Updated", "Sector"])
    df.to_csv(csv_file, index=False)