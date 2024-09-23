from polygon import RESTClient
from datetime import datetime, timedelta
import pytz
from config import API_KEY

def fetch_stock_data(symbol, last_updated):
    ny_tz = pytz.timezone('America/New_York')
    today = datetime.now(ny_tz).strftime("%Y-%m-%d")
    if last_updated == today:
        print(f"Debug: {symbol} data is up to date")
        return None, last_updated

    try:
        client = RESTClient(API_KEY)
        end_date = datetime.now(ny_tz).date() - timedelta(days=1)
        start_date = end_date - timedelta(days=5)

        resp = client.get_aggs(ticker=symbol,
                               multiplier=1,
                               timespan="day",
                               from_=start_date.strftime('%Y-%m-%d'),
                               to=end_date.strftime('%Y-%m-%d'))

        if resp and len(resp) > 0:
            price = resp[-1].close
            print(f"Debug: Fetched data for {symbol}: price={price}, date={today}")
            return price, today
        else:
            print(f"Debug: No data received for {symbol}")
            return None, last_updated
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, last_updated