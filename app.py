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
            hist = stock.history(period="1d", interval="5m")  # Fetch intraday data for real-time updates
            
            if hist.empty:
                index_data[name] = {"error": "Data not available"}
                continue

            latest_price = hist["Close"].iloc[-1]  # Latest price
            open_price = hist["Open"].iloc[0]  # Market open price
            high_price = hist["High"].max()  # High of the day
            low_price = hist["Low"].min()  # Low of the day
            close_price = hist["Close"].iloc[-1]  # Last closing price
            
            percent_change = ((latest_price - open_price) / open_price) * 100
            
            color = "same"
            if latest_price > open_price:
                color = "green"
            elif latest_price < open_price:
                color = "red"

            index_data[name] = {
                "current_price": round(latest_price, 2),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "percent_change": round(percent_change, 2),
                "color": color
            }

        return jsonify(index_data)

    except Exception as e:
        print("Error fetching market indices:", e)
        return jsonify({"error": "Unable to fetch market indices"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
