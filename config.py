import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
if API_KEY is None:
    raise ValueError("API_KEY environment variable is not set")

CSV_FILE = "transactions.csv"