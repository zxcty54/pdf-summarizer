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
            history = stock.history(period="2d")  # Fetch last 2 days for previous close
            fast_info = stock.fast_info  # Fast lookup for prices

            if history.empty:
                index_data[name] = {"current_price": "N/A", "percent_change": "N/A"}
            else:
                # Fetch close price
                close_price = fast_info["last_price"] if "last_price" in fast_info else history["Close"].iloc[-1]
                
                # Fetch previous close price
                previous_close = fast_info["previous_close"] if "previous_close" in fast_info else history["Close"].iloc[-2]

                # Calculate percentage change
                percent_change = ((close_price - previous_close) / previous_close) * 100

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
