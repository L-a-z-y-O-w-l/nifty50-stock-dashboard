from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

NIFTY_50 = [
    {"name": "Adani Enterprises", "symbol": "ADANIENT.NS"},
    {"name": "Adani Ports", "symbol": "ADANIPORTS.NS"},
    {"name": "Apollo Hospitals", "symbol": "APOLLOHOSP.NS"},
    {"name": "Asian Paints", "symbol": "ASIANPAINT.NS"},
    {"name": "Axis Bank", "symbol": "AXISBANK.NS"},
    {"name": "Bajaj Auto", "symbol": "BAJAJ-AUTO.NS"},
    {"name": "Bajaj Finance", "symbol": "BAJFINANCE.NS"},
    {"name": "Bajaj Finserv", "symbol": "BAJAJFINSV.NS"},
    {"name": "BEL", "symbol": "BEL.NS"},
    {"name": "Bharti Airtel", "symbol": "BHARTIARTL.NS"},
    {"name": "Cipla", "symbol": "CIPLA.NS"},
    {"name": "Coal India", "symbol": "COALINDIA.NS"},
    {"name": "Dr Reddys", "symbol": "DRREDDY.NS"},
    {"name": "Eicher Motors", "symbol": "EICHERMOT.NS"},
    {"name": "Grasim", "symbol": "GRASIM.NS"},
    {"name": "HCL Tech", "symbol": "HCLTECH.NS"},
    {"name": "HDFC Bank", "symbol": "HDFCBANK.NS"},
    {"name": "HDFC Life", "symbol": "HDFCLIFE.NS"},
    {"name": "Hero MotoCorp", "symbol": "HEROMOTOCO.NS"},
    {"name": "Hindalco", "symbol": "HINDALCO.NS"},
    {"name": "HUL", "symbol": "HINDUNILVR.NS"},
    {"name": "ICICI Bank", "symbol": "ICICIBANK.NS"},
    {"name": "IndusInd Bank", "symbol": "INDUSINDBK.NS"},
    {"name": "Infosys", "symbol": "INFY.NS"},
    {"name": "ITC", "symbol": "ITC.NS"},
    {"name": "Jio Financial", "symbol": "JIOFIN.NS"},
    {"name": "JSW Steel", "symbol": "JSWSTEEL.NS"},
    {"name": "Kotak Bank", "symbol": "KOTAKBANK.NS"},
    {"name": "Larsen and Toubro", "symbol": "LT.NS"},
    {"name": "M and M", "symbol": "M&M.NS"},
    {"name": "Maruti Suzuki", "symbol": "MARUTI.NS"},
    {"name": "Nestle India", "symbol": "NESTLEIND.NS"},
    {"name": "NTPC", "symbol": "NTPC.NS"},
    {"name": "ONGC", "symbol": "ONGC.NS"},
    {"name": "Power Grid", "symbol": "POWERGRID.NS"},
    {"name": "Reliance", "symbol": "RELIANCE.NS"},
    {"name": "SBI Life", "symbol": "SBILIFE.NS"},
    {"name": "Shriram Finance", "symbol": "SHRIRAMFIN.NS"},
    {"name": "SBI", "symbol": "SBIN.NS"},
    {"name": "Sun Pharma", "symbol": "SUNPHARMA.NS"},
    {"name": "TCS", "symbol": "TCS.NS"},
    {"name": "Tata Consumer", "symbol": "TATACONSUM.NS"},
    {"name": "Tata Motors", "symbol": "TATAMOTORS.NS"},
    {"name": "Tata Steel", "symbol": "TATASTEEL.NS"},
    {"name": "Tech Mahindra", "symbol": "TECHM.NS"},
    {"name": "Titan", "symbol": "TITAN.NS"},
    {"name": "Trent", "symbol": "TRENT.NS"},
    {"name": "UltraTech Cement", "symbol": "ULTRACEMCO.NS"},
    {"name": "Wipro", "symbol": "WIPRO.NS"}
]

def convert_df_to_candles(df):
    candles = []
    for index, row in df.iterrows():
        candles.append({
            "date": index.strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0
        })
    return candles

@app.route("/")
def home():
    return jsonify({
        "message": "Nifty 50 stock backend is running",
        "endpoints": ["/api/stocks", "/api/stock-data?symbol=RELIANCE.NS"]
    })

@app.route("/api/stocks")
def get_stocks():
    return jsonify(NIFTY_50)

@app.route("/api/stock-data")
def get_stock_data():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "symbol query parameter is required"}), 400

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            auto_adjust=False
        )

        if df is None or df.empty:
            return jsonify({"error": f"No data found for {symbol}"}), 404

        needed = ["Open", "High", "Low", "Close", "Volume"]
        df = df[needed].dropna()

        if df.empty:
            return jsonify({"error": f"No usable OHLC data found for {symbol}"}), 404

        candles = convert_df_to_candles(df)

        return jsonify({
            "symbol": symbol,
            "count": len(candles),
            "data": candles
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
