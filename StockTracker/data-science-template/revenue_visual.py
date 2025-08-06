import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def fetch_realtime_stock_data(symbol: str, period: str = "1d", interval: str = "15m"):
    """
    Fetches real-time stock data for the given symbol.
    """
    data = yf.download(tickers=symbol, period=period, interval=interval)
    return data

def predict_buy_sell(df: pd.DataFrame, short_window: int = 5, long_window: int = 20):
    """
    Simple moving average crossover strategy for buy/sell prediction.
    Returns 'Buy', 'Sell', or 'Hold'.
    """
    df['SMA_short'] = df['Close'].rolling(window=short_window).mean()
    df['SMA_long'] = df['Close'].rolling(window=long_window).mean()
    if df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1]:
        return 'Buy'
    elif df['SMA_short'].iloc[-1] < df['SMA_long'].iloc[-1]:
        return 'Sell'
    else:
        return 'Hold'

if __name__ == "__main__":
    symbol = "RELIANCE.NS"  # Change to your desired NSE/BSE symbol
    df = fetch_realtime_stock_data(symbol)
    if df.empty:
        print(f"No data found for {symbol}.")
    else:
        # Calculate moving averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()

        # Generate buy/sell/hold markers
        markers = []
        for i in range(1, len(df)):
            if pd.isna(df['SMA_5'].iloc[i]) or pd.isna(df['SMA_20'].iloc[i]):
                markers.append('')
            elif df['SMA_5'].iloc[i] > df['SMA_20'].iloc[i] and df['SMA_5'].iloc[i-1] <= df['SMA_20'].iloc[i-1]:
                markers.append('Buy')
            elif df['SMA_5'].iloc[i] < df['SMA_20'].iloc[i] and df['SMA_5'].iloc[i-1] >= df['SMA_20'].iloc[i-1]:
                markers.append('Sell')
            else:
                markers.append('')
        markers.insert(0, '')  # First row has no marker
        df['Marker'] = markers

        # Plot closing price trend
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], label='Close Price')
        plt.plot(df.index, df['SMA_5'], label='SMA 5')
        plt.plot(df.index, df['SMA_20'], label='SMA 20')

        # Plot buy/sell markers
        buy_signals = df[df['Marker'] == 'Buy']
        sell_signals = df[df['Marker'] == 'Sell']
        plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy Signal', s=100, zorder=5)
        plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell Signal', s=100, zorder=5)

        plt.title(f"{symbol} Price Trend (Realtime) with Buy/Sell Markers")
        plt.xlabel("Datetime")
        plt.ylabel("Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Print buy/sell prices
        print("Buy/Sell signals:")
        for idx, row in buy_signals.iterrows():
            price = float(row['Close']) if not isinstance(row['Close'], pd.Series) else float(row['Close'].values[0])
            print(f"Buy at {price:.2f} on {idx}")
        for idx, row in sell_signals.iterrows():
            price = float(row['Close']) if not isinstance(row['Close'], pd.Series) else float(row['Close'].values[0])
            print(f"Sell at {price:.2f} on {idx}")

        # Prediction
        action = predict_buy_sell(df)
        latest_price = df['Close'].iloc[-1]
        if isinstance(latest_price, pd.Series):
            latest_price = float(latest_price.values[0])
        else:
            latest_price = float(latest_price)
        print(f"Prediction for {symbol}: {action} at price {latest_price:.2f}")
