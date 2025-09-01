import pandas as pd
from alpha_vantage.timeseries import TimeSeries

def fetch_coca_cola_timeseries(API_KEY: str):
    """
    Pobiera dane z ostatnich 5 lat dla akcji Coca-Cola (KO) z Alpha Vantage.
    Zwraca DataFrame z kolumną 'adj_close' (adjusted close).
    """
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    
    # get_daily_adjusted daje pełne dane dzienne
    data, meta_data = ts.get_weekly_adjusted(symbol='KO')
    
    # Uporządkuj dane
    df = data.rename(columns={
        '5. adjusted close': 'adj_close'
    })[['adj_close']]  # zostawiamy tylko adjusted close
    
    # Alpha Vantage zwraca dane od najstarszych do najnowszych, odfiltruj ostatnie 5 lat
    df.index = df.index.astype("datetime64[ns]")  # upewniamy się że index to datetime
    df = df.sort_index()
    
    last_5y = df[df.index >= (df.index.max() - pd.DateOffset(years=5))]
    
    return last_5y