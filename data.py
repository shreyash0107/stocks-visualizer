import pandas as pd
import yfinance as yf

def clean_tickers(raw_list):
    tickers = [t.strip().upper() for t in raw_list if t.strip()]
    # remove duplicates, keep order
    return list(dict.fromkeys(tickers))

def fetch_prices(tickers, start, end):
    """Returns a DataFrame of prices (columns = tickers)."""
    tickers = clean_tickers(tickers)
    if not tickers:
        return pd.DataFrame()

    df = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        # After auto_adjust, 'Close' contains adjusted close
        if 'Close' in df.columns.levels[0]:
            prices = df['Close'].copy()
        else:
            # fallback
            prices = df.xs('Close', axis=1, level=0)
    else:
        # single ticker -> Series
        if 'Close' in df.columns:
            prices = df[['Close']].copy()
        else:
            prices = df.copy()
    if prices.empty:
        return pd.DataFrame()

    # If single ticker, column might be named 'Close'
    if prices.shape[1] == 1 and prices.columns[0] == 'Close':
        prices.columns = [tickers[0]]

    prices = prices.dropna(how='all')
    return prices
