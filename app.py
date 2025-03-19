import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

# ✅ Cache storage
cache = {"data": None, "last_update": 0}  # Stores fetched data + last update timestamp
CACHE_DURATION = 15  # Update every 15 seconds

@app.route('/')
def home():
    return "Market Indices API with Caching is Running!"

@app.route('/market-indices')
def get_market_indices():
    try:
        current_time = time.time()

        # ✅ **Return Cached Data if Less Than 15 Seconds Old**
        if cache["data"] and (current_time - cache["last_update"] < CACHE_DURATION):
            return jsonify(cache["data"])  # Serve cached data immediately 🚀

        # ✅ **Otherwise, Fetch Fresh Data**
        indices = {
            "Dow Jones": "^DJI",
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "NIFTY 50": "^NSEI",
            "SENSEX": "^BSESN",
            "BANK NIFTY": "^NSEBANK"
        }

        index_data = {}

        for name, symbol in indices.items():
            stock = yf.Ticker(symbol)
            history = stock.history(period="2d")  # Fetch last 2 days of data

            if history.empty or len(history) < 2:
                print(f"⚠ No sufficient data for {name} ({symbol})")
                index_data[name] = {"current_price": "N/A", "percent_change": "N/A"}
                continue

            prev_close = history["Close"].iloc[-2]  # Previous Close
            current_price = history["Close"].iloc[-1]  # Latest Close

            if prev_close is None or current_price is None:
                print(f"⚠ Missing Close data for {name}")
                index_data[name] = {"current_price": "N/A", "percent_change": "N/A"}
                continue

            percent_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

            index_data[name] = {
                "current_price": round(current_price, 2),
                "percent_change": round(percent_change, 2),
                "previous_close": round(prev_close, 2)
            }

        # ✅ **Store New Data in Cache**
        cache["data"] = index_data
        cache["last_update"] = current_time

        return jsonify(index_data)

    except Exception as e:
        print("🚨 Error fetching market indices:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
