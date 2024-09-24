import os
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
FMP_API_KEY = os.environ.get("FMP_API_KEY")

if FINNHUB_API_KEY is None:
    raise ValueError("FINNHUB_API_KEY environment variable is not set")
if FMP_API_KEY is None:
    raise ValueError("FMP_API_KEY environment variable is not set")

CSV_FILE = "transactions.csv"