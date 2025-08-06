import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import time
import pytz
import sys
## Removed options chain logic; focusing on intraday stock analysis

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
    # Read symbols from symbols.txt so you can add/remove stocks without stopping the program
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    symbols_file = os.path.join(script_dir, "symbols.txt")
    # Create symbols.txt with default symbol if it doesn't exist
    if not os.path.exists(symbols_file):
        with open(symbols_file, "w") as f:
            f.write("^NSEI\n")
    import csv
    signals_file = os.path.join(script_dir, "signals.csv")
    # Write header if file does not exist
    if not os.path.exists(signals_file):
        with open(signals_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["symbol", "timestamp_IST", "action", "price"])

    while True:
        with open(symbols_file, "r") as f:
            symbols = [line.strip() for line in f if line.strip()]
        latest_signals = []
        ist = pytz.timezone('Asia/Kolkata')
        for symbol in symbols:
            print(f"\n--- Intraday Analysis for {symbol} ---")
            df = fetch_realtime_stock_data(symbol)
            if df.empty:
                print(f"No data found for {symbol}.")
                continue
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

            plt.title(f"{symbol} Intraday Price Trend with Buy/Sell Markers")
            plt.xlabel("Datetime")
            plt.ylabel("Price")
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(2)
            plt.close()

            # Find latest signal
            action = predict_buy_sell(df)
            latest_price = df['Close'].iloc[-1]
            ts_ist = pd.Timestamp(df.index[-1]).tz_convert(ist) if pd.Timestamp(df.index[-1]).tzinfo else pd.Timestamp(df.index[-1]).tz_localize('UTC').tz_convert(ist)
            if isinstance(latest_price, pd.Series):
                latest_price = float(latest_price.values[0])
            else:
                latest_price = float(latest_price)
            latest_signals.append([symbol, str(ts_ist), action, latest_price])
            print(f"Latest signal for {symbol}: {action} at {ts_ist} price {latest_price:.2f}")
            sys.stdout.flush()
        # Overwrite signals.csv with only the latest signals
        with open(signals_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["symbol", "timestamp_IST", "action", "price"])
            writer.writerows(latest_signals)
        print("\nWaiting 5 minutes before next update...")
        time.sleep(300)
