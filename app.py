import os
from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Market Indices API is Running!"

@app.route('/market-indices')
def get_market_indices():
    try:
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
            history = stock.history(period="1d")

            if history.empty:
                index_data[name] = {"current_price": "N/A", "percent_change": "N/A"}
            else:
                open_price = history["Open"].iloc[-1]
                close_price = history["Close"].iloc[-1]

                # Calculate percentage change
                percent_change = ((close_price - open_price) / open_price) * 100

                index_data[name] = {
                    "current_price": round(close_price, 2),
                    "percent_change": round(percent_change, 2)
                }

        return jsonify(index_data)

    except Exception as e:
        print("Error fetching market indices:", e)
        return jsonify({"error": "Unable to fetch market indices"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
