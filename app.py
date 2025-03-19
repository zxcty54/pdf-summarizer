import os
import threading
import time
from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

# ✅ Store Cached Data
cached_data = {}
last_updated = 0

# ✅ Indices to fetch
indices = {
    "Dow Jones": "^DJI",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK"
}

# ✅ Function to Fetch & Store Data Every 15 Sec
def fetch_market_data():
    global cached_data, last_updated
    while True:
        try:
            index_data = {}
            for name, symbol in indices.items():
                stock = yf.Ticker(symbol)
                history = stock.history(period="2d")

                if history.empty or len(history) < 2:
                    print(f"⚠ No sufficient data for {name} ({symbol})")
                    index_data[name] = cached_data.get(name, {"current_price": "N/A", "percent_change": "N/A"})
                    continue

                prev_close = history["Close"].iloc[-2]
                current_price = history["Close"].iloc[-1]

                if prev_close is None or current_price is None:
                    print(f"⚠ Missing Close data for {name}")
                    index_data[name] = cached_data.get(name, {"current_price": "N/A", "percent_change": "N/A"})
                    continue

                percent_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

                index_data[name] = {
                    "current_price": round(current_price, 2),
                    "percent_change": round(percent_change, 2),
                    "previous_close": round(prev_close, 2)
                }

            cached_data = index_data  # ✅ Save latest data
            last_updated = time.time()
            print("✅ Market data updated!")

        except Exception as e:
            print("🚨 Error fetching market indices:", e)

        time.sleep(15)  # ✅ Fetch data every 15 sec in the background

# ✅ Start Background Thread for Auto-Updating
thread = threading.Thread(target=fetch_market_data)
thread.daemon = True
thread.start()

@app.route('/')
def home():
    return "Market Indices API is Running!"

@app.route('/market-indices')
def get_market_indices():
    if not cached_data:
        return jsonify({"message": "Fetching data, please wait..."}), 200  # ✅ No error, just message

    return jsonify(cached_data)  # ✅ Serve the last available data instantly

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
