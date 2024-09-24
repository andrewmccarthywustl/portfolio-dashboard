import finnhub
from datetime import datetime
import pytz
import requests
from config import FINNHUB_API_KEY, FMP_API_KEY

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


def fetch_stock_data(symbol, last_updated):
    ny_tz = pytz.timezone('America/New_York')
    today = datetime.now(ny_tz).strftime("%Y-%m-%d")
    if last_updated == today:
        print(f"Debug: {symbol} data is up to date")
        return None, last_updated

    try:
        quote = finnhub_client.quote(symbol)
        price = quote['c']  # Current price

        if price:
            print(f"Debug: Fetched data for {symbol}: price={price}, date={today}")
            return price, today
        else:
            print(f"Debug: No data received for {symbol}")
            return None, last_updated
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, last_updated


def get_stock_sector(symbol):
    url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0].get('sector', 'Unknown')
        print(f"Error fetching sector for {symbol}: HTTP {response.status_code}")
        return 'Unknown'
    except Exception as e:
        print(f"Error fetching sector for {symbol}: {str(e)}")
        return 'Unknown'