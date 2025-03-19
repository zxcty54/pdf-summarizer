import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import threading

app = Flask(__name__)
CORS(app)

# ✅ Cache storage for market data
market_cache = {"data": None, "last_updated": 0}

indices = {
    "Dow Jones": "^DJI",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK"
}

def fetch_market_data():
    """Background function to fetch market prices every 15 seconds."""
    global market_cache
    while True:
        try:
            index_data = {}
            for name, symbol in indices.items():
                stock = yf.Ticker(symbol)
                history = stock.history(period="2d")

                if history.empty or len(history) < 2:
                    print(f"⚠ No sufficient data for {name} ({symbol})")
                    index_data[name] = {"current_price": "N/A", "percent_change": "N/A"}
                    continue

                prev_close = history["Close"].iloc[-2]
                current_price = history["Close"].iloc[-1]

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

            # ✅ Store in cache
            market_cache["data"] = index_data
            market_cache["last_updated"] = time.time()
            print("✅ Market data updated!")

        except Exception as e:
            print("🚨 Error fetching market indices:", e)

        time.sleep(15)  # ✅ Fetch every 15 seconds


@app.route('/')
def home():
    return "Market Indices API is Running!"

@app.route('/market-indices')
def get_market_indices():
    """Return cached data instantly to visitors."""
    return jsonify(market_cache["data"] or {"error": "Data not available yet"})


# ✅ Start background thread to fetch market data
threading.Thread(target=fetch_market_data, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
