from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")

NIFTY_50 = [
    {"name": "Adani Enterprises", "symbol": "ADANIENT.BSE"},
    {"name": "Adani Ports", "symbol": "ADANIPORTS.BSE"},
    {"name": "Apollo Hospitals", "symbol": "APOLLOHOSP.BSE"},
    {"name": "Asian Paints", "symbol": "ASIANPAINT.BSE"},
    {"name": "Axis Bank", "symbol": "AXISBANK.BSE"},
    {"name": "Bajaj Auto", "symbol": "BAJAJ-AUTO.BSE"},
    {"name": "Bajaj Finance", "symbol": "BAJFINANCE.BSE"},
    {"name": "Bajaj Finserv", "symbol": "BAJAJFINSV.BSE"},
    {"name": "BEL", "symbol": "BEL.BSE"},
    {"name": "Bharti Airtel", "symbol": "BHARTIARTL.BSE"},
    {"name": "Cipla", "symbol": "CIPLA.BSE"},
    {"name": "Coal India", "symbol": "COALINDIA.BSE"},
    {"name": "Dr Reddys", "symbol": "DRREDDY.BSE"},
    {"name": "Eicher Motors", "symbol": "EICHERMOT.BSE"},
    {"name": "Grasim", "symbol": "GRASIM.BSE"},
    {"name": "HCL Tech", "symbol": "HCLTECH.BSE"},
    {"name": "HDFC Bank", "symbol": "HDFCBANK.BSE"},
    {"name": "HDFC Life", "symbol": "HDFCLIFE.BSE"},
    {"name": "Hero MotoCorp", "symbol": "HEROMOTOCO.BSE"},
    {"name": "Hindalco", "symbol": "HINDALCO.BSE"},
    {"name": "HUL", "symbol": "HINDUNILVR.BSE"},
    {"name": "ICICI Bank", "symbol": "ICICIBANK.BSE"},
    {"name": "IndusInd Bank", "symbol": "INDUSINDBK.BSE"},
    {"name": "Infosys", "symbol": "INFY.BSE"},
    {"name": "ITC", "symbol": "ITC.BSE"},
    {"name": "Jio Financial", "symbol": "JIOFIN.BSE"},
    {"name": "JSW Steel", "symbol": "JSWSTEEL.BSE"},
    {"name": "Kotak Bank", "symbol": "KOTAKBANK.BSE"},
    {"name": "Larsen and Toubro", "symbol": "LT.BSE"},
    {"name": "M and M", "symbol": "M&M.BSE"},
    {"name": "Maruti Suzuki", "symbol": "MARUTI.BSE"},
    {"name": "Nestle India", "symbol": "NESTLEIND.BSE"},
    {"name": "NTPC", "symbol": "NTPC.BSE"},
    {"name": "ONGC", "symbol": "ONGC.BSE"},
    {"name": "Power Grid", "symbol": "POWERGRID.BSE"},
    {"name": "Reliance", "symbol": "RELIANCE.BSE"},
    {"name": "SBI Life", "symbol": "SBILIFE.BSE"},
    {"name": "Shriram Finance", "symbol": "SHRIRAMFIN.BSE"},
    {"name": "SBI", "symbol": "SBIN.BSE"},
    {"name": "Sun Pharma", "symbol": "SUNPHARMA.BSE"},
    {"name": "TCS", "symbol": "TCS.BSE"},
    {"name": "Tata Consumer", "symbol": "TATACONSUM.BSE"},
    {"name": "Tata Motors", "symbol": "TATAMOTORS.BSE"},
    {"name": "Tata Steel", "symbol": "TATASTEEL.BSE"},
    {"name": "Tech Mahindra", "symbol": "TECHM.BSE"},
    {"name": "Titan", "symbol": "TITAN.BSE"},
    {"name": "Trent", "symbol": "TRENT.BSE"},
    {"name": "UltraTech Cement", "symbol": "ULTRACEMCO.BSE"},
    {"name": "Wipro", "symbol": "WIPRO.BSE"}
]

@app.route("/")
def home():
    return jsonify({
        "message": "Nifty 50 stock backend is running",
        "endpoints": ["/api/stocks", "/api/stock-data?symbol=RELIANCE.BSE"]
    })

@app.route("/api/stocks")
def get_stocks():
    return jsonify(NIFTY_50)

@app.route("/api/stock-data")
def get_stock_data():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "symbol query parameter is required"}), 400

    if not API_KEY:
        return jsonify({"error": "ALPHAVANTAGE_API_KEY is not set on Render"}), 500

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "Error Message" in result:
            return jsonify({"error": result["Error Message"], "raw": result}), 404

        if "Note" in result:
            return jsonify({"error": result["Note"], "raw": result}), 429

        series = result.get("Time Series (Daily)")
        if not series:
            return jsonify({"error": "No daily time series found", "raw": result}), 404

        dates = sorted(series.keys())[-365:]
        data = []

        for d in dates:
            row = series[d]
            data.append({
                "date": d,
                "open": float(row["1. open"]),
                "high": float(row["2. high"]),
                "low": float(row["3. low"]),
                "close": float(row["4. close"]),
                "volume": int(float(row["5. volume"]))
            })

        return jsonify({
            "symbol": symbol,
            "count": len(data),
            "data": data
        })

    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
