from fastapi.responses import HTMLResponse
import requests
import numpy as np
from scipy.stats import norm
import sqlite3
from fastapi import FastAPI
import yfinance as yf
import pandas_ta as ta

tool_schemas = {
    "get_live_price": {"params": ["symbol"]},
    "generate_signal": {"params": ["symbol"]},
    "get_options_chain": {"params": ["symbol"]},
    "place_virtual_trade": {"params": ["symbol", "qty", "side"]},
    "get_portfolio_pnl": {"params": []},
    "calculate_greeks": {"params": ["S", "K", "T", "r", "sigma"]},
    "scan_market": {"params": []},
    "detect_unusual_activity": {"params": ["symbol"]},
    "analyze_sentiment": {"params": ["symbol"]},
    "get_sector_heatmap": {"params": []}
}

app = FastAPI()
conn = sqlite3.connect("portfolio.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS trades(
id INTEGER PRIMARY KEY AUTOINCREMENT,
symbol TEXT,
qty INTEGER,
price REAL,
side TEXT
)
""")


from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html") as f:
        return f.read()


@app.get("/get_live_price")
def get_live_price(symbol: str):

    ticker = yf.Ticker(symbol + ".NS")
    data = ticker.history(period="1d")

    if data.empty:
        return {"error": "No data found"}

    price = float(data["Close"].iloc[-1])
    volume = int(data["Volume"].iloc[-1])

    return {
        "symbol": symbol,
        "price": price,
        "volume": volume
    }


@app.get("/generate_signal")
def generate_signal(symbol: str):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.history(period="3mo")

    if df.empty:
        return {"error": "No data"}

    # RSI
    df["RSI"] = ta.rsi(df["Close"], length=14)

    # MACD
    macd = ta.macd(df["Close"])
    df["MACD"] = macd.iloc[:,0]
    df["MACD_SIGNAL"] = macd.iloc[:,1]

    # Bollinger Bands
    bb = ta.bbands(df["Close"])
    df["BB_UPPER"] = bb.iloc[:,0]
    df["BB_MIDDLE"] = bb.iloc[:,1]
    df["BB_LOWER"] = bb.iloc[:,2]

    rsi = df["RSI"].iloc[-1]
    macd_value = df["MACD"].iloc[-1]
    macd_signal = df["MACD_SIGNAL"].iloc[-1]
    close_price = df["Close"].iloc[-1]
    bb_upper = df["BB_UPPER"].iloc[-1]
    bb_lower = df["BB_LOWER"].iloc[-1]

    signal = "HOLD"
    confidence = 50

    if rsi < 30 and macd_value > macd_signal and close_price < bb_lower:
        signal = "BUY"
        confidence = 85

    elif rsi > 70 and macd_value < macd_signal and close_price > bb_upper:
        signal = "SELL"
        confidence = 85

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": confidence,
        "rsi": float(rsi),
        "macd": float(macd_value)
    }

@app.get("/get_options_chain")
def get_options_chain():
    import yfinance as yf

    ticker = yf.Ticker("AAPL")

    try:
        expiry = ticker.options[0]
        chain = ticker.option_chain(expiry)

        calls = chain.calls.head(5).to_dict(orient="records")
        puts = chain.puts.head(5).to_dict(orient="records")

        return {
            "symbol": "AAPL",
            "expiry": expiry,
            "calls": calls,
            "puts": puts
        }

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/place_virtual_trade")
def place_virtual_trade(symbol: str, qty: int, side: str):

    ticker = yf.Ticker(symbol + ".NS")
    data = ticker.history(period="1d")

    if data.empty:
        return {"error": "No price data"}

    price = float(data["Close"].iloc[-1])

    conn.execute(
        "INSERT INTO trades(symbol, qty, price, side) VALUES (?, ?, ?, ?)",
        (symbol, qty, price, side)
    )

    conn.commit()

    return {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "price": price,
        "status": "trade placed"
    }

@app.get("/get_portfolio_pnl")
def get_portfolio_pnl():

    cursor = conn.execute("SELECT symbol, qty, price, side FROM trades")

    trades = cursor.fetchall()

    portfolio = []
    total_pnl = 0

    for symbol, qty, price, side in trades:

        ticker = yf.Ticker(symbol + ".NS")
        data = ticker.history(period="1d")

        if data.empty:
            continue

        live_price = float(data["Close"].iloc[-1])

        pnl = (live_price - price) * qty

        if side == "SELL":
            pnl = -pnl

        total_pnl += pnl

        portfolio.append({
            "symbol": symbol,
            "qty": qty,
            "buy_price": price,
            "live_price": live_price,
            "pnl": pnl
        })

    return {
        "positions": portfolio,
        "total_pnl": total_pnl
    }
    
@app.get("/calculate_greeks")
def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float):

    d1 = (np.log(S/K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)

    return {
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega
    }
    
@app.get("/scan_market")
def scan_market():

    stocks = [
        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "ICICIBANK",
        "ITC",
        "LT",
        "SBIN"
    ]

    results = []

    for symbol in stocks:

        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.history(period="3mo")

        if df.empty:
            continue

        df["RSI"] = ta.rsi(df["Close"], length=14)
        rsi = df["RSI"].iloc[-1]

        if rsi < 30:
            results.append({
                "symbol": symbol,
                "rsi": float(rsi),
                "signal": "OVERSOLD"
            })

    return {
        "oversold_stocks": results
    }
    
@app.get("/analyze_sentiment")
def analyze_sentiment(symbol: str):

    API_KEY = "76cc94ec734e49078e6e3a887fe640cc"

    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={API_KEY}"

    response = requests.get(url).json()

    articles = response.get("articles", [])[:5]

    headlines = [a["title"] for a in articles]

    score = 0

    for h in headlines:
        if "gain" in h.lower() or "rise" in h.lower() or "profit" in h.lower():
            score += 1
        elif "loss" in h.lower() or "fall" in h.lower() or "drop" in h.lower():
            score -= 1

    signal = "NEUTRAL"

    if score > 0:
        signal = "POSITIVE"
    elif score < 0:
        signal = "NEGATIVE"

    return {
        "symbol": symbol,
        "sentiment_score": score,
        "signal": signal,
        "headlines": headlines
    }
    
@app.get("/detect_unusual_activity")
def detect_unusual_activity(symbol: str = "AAPL"):

    ticker = yf.Ticker(symbol)

    try:
        expiry = ticker.options[0]
        chain = ticker.option_chain(expiry)

        unusual = []

        for _, row in chain.calls.iterrows():

            if row["volume"] > row["openInterest"] * 2:
                unusual.append({
                    "strike": row["strike"],
                    "volume": int(row["volume"]),
                    "open_interest": int(row["openInterest"]),
                    "type": "CALL"
                })

        for _, row in chain.puts.iterrows():

            if row["volume"] > row["openInterest"] * 2:
                unusual.append({
                    "strike": row["strike"],
                    "volume": int(row["volume"]),
                    "open_interest": int(row["openInterest"]),
                    "type": "PUT"
                })

        return {
            "symbol": symbol,
            "expiry": expiry,
            "unusual_activity": unusual[:10]
        }

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/get_sector_heatmap")
def get_sector_heatmap():

    sectors = {
        "IT": ["TCS", "INFY"],
        "BANKING": ["HDFCBANK", "ICICIBANK", "SBIN"],
        "ENERGY": ["RELIANCE"],
        "FMCG": ["ITC"]
    }

    heatmap = []

    for sector, stocks in sectors.items():

        total_change = 0
        count = 0

        for s in stocks:

            ticker = yf.Ticker(s + ".NS")
            data = ticker.history(period="1d")

            if data.empty:
                continue

            open_price = float(data["Open"].iloc[-1])
            close_price = float(data["Close"].iloc[-1])

            change = ((close_price - open_price) / open_price) * 100

            total_change += change
            count += 1

        if count > 0:
            heatmap.append({
                "sector": sector,
                "change_percent": total_change / count
            })

    return {"sector_heatmap": heatmap}

@app.get("/mcp_tools")
def mcp_tools():

    tools = [
        {"name": "get_live_price", "description": "Get live stock price", "params": ["symbol"]},
        {"name": "get_options_chain", "description": "Fetch options chain data", "params": ["symbol"]},
        {"name": "analyze_sentiment", "description": "Analyze news sentiment for a stock", "params": ["symbol"]},
        {"name": "generate_signal", "description": "Generate trading signal using technical indicators", "params": ["symbol"]},
        {"name": "get_portfolio_pnl", "description": "Get portfolio profit and loss", "params": []},
        {"name": "place_virtual_trade", "description": "Place a virtual trade in portfolio", "params": ["symbol","qty","side"]},
        {"name": "calculate_greeks", "description": "Calculate Black-Scholes option greeks", "params": ["S","K","T","r","sigma"]},
        {"name": "detect_unusual_activity", "description": "Detect unusual options activity", "params": ["symbol"]},
        {"name": "scan_market", "description": "Scan market for oversold stocks", "params": []},
        {"name": "get_sector_heatmap", "description": "Get sector performance heatmap", "params": []}
    ]

    return {"tools": tools}

@app.get("/get_ohlc")
def get_ohlc(symbol: str):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.history(period="1mo")

    return df.tail(10).to_dict()

@app.get("/max_pain")
def max_pain(symbol: str = "AAPL"):

    ticker = yf.Ticker(symbol)
    expiry = ticker.options[0]
    chain = ticker.option_chain(expiry)

    calls = chain.calls
    puts = chain.puts

    strikes = calls["strike"].values
    pain = {}

    for strike in strikes:

        call_pain = sum((strike - s) * oi for s, oi in zip(calls["strike"], calls["openInterest"]) if strike > s)
        put_pain = sum((s - strike) * oi for s, oi in zip(puts["strike"], puts["openInterest"]) if strike < s)

        pain[strike] = call_pain + put_pain

    max_pain_strike = min(pain, key=pain.get)

    return {
        "symbol": symbol,
        "expiry": expiry,
        "max_pain": max_pain_strike
    }
    
@app.post("/rpc")
async def rpc_handler(request: dict):

    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    try:

        if method == "get_live_price":
            result = get_live_price(**params)

        elif method == "generate_signal":
            result = generate_signal(**params)

        elif method == "get_options_chain":
            result = get_options_chain(**params)

        elif method == "place_virtual_trade":
            result = place_virtual_trade(**params)

        elif method == "get_portfolio_pnl":
            result = get_portfolio_pnl()

        elif method == "calculate_greeks":
            result = calculate_greeks(**params)

        elif method == "scan_market":
            result = scan_market()

        elif method == "detect_unusual_activity":
            result = detect_unusual_activity(**params)

        elif method == "analyze_sentiment":
            result = analyze_sentiment(**params)

        elif method == "get_sector_heatmap":
            result = get_sector_heatmap()

        else:
            raise Exception("Method not found")

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    except Exception as e:

        return {
            "jsonrpc": "2.0",
            "error": str(e),
            "id": request_id
        }
        
@app.get("/", response_class=HTMLResponse)
def homepage():

    with open("index.html") as f:
        return f.read()