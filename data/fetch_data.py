import requests
import pandas as pd

def fetch_interbank_liquidity_data():
    url = "https://api.hkma.gov.hk/public/market-data-and-statistics/daily-monetary-statistics/daily-figures-interbank-liquidity"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['result']['records']
        df = pd.DataFrame(data)
        df['end_of_date'] = pd.to_datetime(df['end_of_date'])
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()