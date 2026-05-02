import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Mordor Finance Terminal",
    page_icon="🔥",
    layout="wide"
)

# ---------------- MORDOR DARK THEME ----------------
st.markdown(
    """
    <style>
    body {
        background-color: #0b0b0b;
        color: #e6e6e6;
    }

    .stApp {
        background-color: #0b0b0b;
    }

    h1, h2, h3 {
        color: #ff3b30;
    }

    .card {
        background: linear-gradient(135deg, #1a1a1a, #0d0d0d);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2a2a2a;
        box-shadow: 0px 0px 10px rgba(255, 0, 0, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;'>🔥 MORDOR FINANCE TERMINAL</h1>", unsafe_allow_html=True)
st.caption("Dark-mode financial intelligence dashboard (educational)")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Control Panel")

symbols_input = st.sidebar.text_input("Enter symbols", "AAPL, TSLA")
period = st.sidebar.selectbox("Time Period", ["7d", "30d", "3mo", "6mo", "1y"], index=1)
run = st.sidebar.button("⚡ Analyze")

# ---------------- COMPANY INFO ----------------
def get_company_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", "N/A"),
            "country": info.get("country", "N/A"),
            "website": info.get("website", "N/A")
        }
    except:
        return {
            "name": symbol,
            "sector": "Unknown",
            "industry": "Unknown",
            "market_cap": "N/A",
            "country": "N/A",
            "website": "N/A"
        }

# ---------------- NEWS SENTIMENT ----------------
def get_news_sentiment(symbol):
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={symbol}+stock")

    if not feed.entries:
        return "No news data"

    pos = ["rise", "gain", "up", "strong", "profit"]
    neg = ["fall", "drop", "down", "loss", "weak"]

    score = 0
    for e in feed.entries[:5]:
        title = e.title.lower()
        for w in pos:
            if w in title:
                score += 1
        for w in neg:
            if w in title:
                score -= 1

    if score > 0:
        return "🟢 Positive News Sentiment"
    elif score < 0:
        return "🔴 Negative News Sentiment"
    return "🟡 Neutral Sentiment"

# ---------------- MAIN APP ----------------
if run:
    symbols = [s.strip().upper() for s in symbols_input.split(",")]

    for symbol in symbols:
        st.divider()

        data = yf.Ticker(symbol).history(period=period)

        if data.empty:
            st.error(f"No data for {symbol}")
            continue

        # ---------------- COMPANY INFO ----------------
        info = get_company_info(symbol)

        start = data["Close"].iloc[0]
        end = data["Close"].iloc[-1]
        change_pct = ((end - start) / start) * 100

        # ---------------- INFO CARD ----------------
        st.markdown(f"""
        <div class="card">
            <h2>🏢 {info['name']} ({symbol})</h2>
            <p><b>Sector:</b> {info['sector']}</p>
            <p><b>Industry:</b> {info['industry']}</p>
            <p><b>Country:</b> {info['country']}</p>
            <p><b>Market Cap:</b> {info['market_cap']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ---------------- METRICS ----------------
        col1, col2, col3 = st.columns(3)
        col1.metric("Start", round(start, 2))
        col2.metric("End", round(end, 2))
        col3.metric("Change %", round(change_pct, 2))

        # ---------------- CHARTS ----------------
        colA, colB = st.columns(2)

        with colA:
            st.markdown("### 📈 Price Chart")
            st.line_chart(data["Close"])

        with colB:
            st.markdown("### 📊 Volume")
            st.bar_chart(data["Volume"])

        # ---------------- MOVING AVERAGES ----------------
        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()

        st.markdown("### 📉 Trend Analysis (MA20 / MA50)")
        st.line_chart(data[["Close", "MA20", "MA50"]])

        # ---------------- NEWS ----------------
        st.markdown("### 📰 News Sentiment")
        st.write(get_news_sentiment(symbol))

        # ---------------- INFO GRAPHIC SUMMARY ----------------
        st.markdown("### 🔥 Summary Insight")

        if change_pct > 0:
            st.success("Uptrend detected — buyers dominating the market.")
        else:
            st.error("Downtrend detected — selling pressure stronger.")

        st.caption("⚠ Educational analysis only, not financial advice.")
