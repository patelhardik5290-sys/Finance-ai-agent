import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- LIGHT THEME ----------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
        color: #1a1a1a;
    }

    h1, h2, h3 {
        color: #1f4e79;
    }

    .card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
st.title("📊 Finance Dashboard")
st.caption("Clean educational financial analytics tool")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Controls")

symbols_input = st.sidebar.text_input("Enter symbols", "AAPL, TSLA")

period = st.sidebar.selectbox(
    "Time Period",
    ["7d", "30d", "3mo", "6mo", "1y"],
    index=1
)

run = st.sidebar.button("🚀 Analyze")

# ---------------- COMPANY INFO ----------------
def get_company_info(symbol):
    try:
        info = yf.Ticker(symbol).info

        market_cap = info.get("marketCap", None)

        # Convert to BILLIONS
        if market_cap:
            market_cap = f"${market_cap / 1e9:.2f}B"
        else:
            market_cap = "N/A"

        return {
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": market_cap,
            "country": info.get("country", "Unknown")
        }

    except:
        return {
            "name": symbol,
            "sector": "Unknown",
            "industry": "Unknown",
            "market_cap": "N/A",
            "country": "Unknown"
        }

# ---------------- NEWS SENTIMENT ----------------
def get_news_sentiment(symbol):
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={symbol}+stock")

    if not feed.entries:
        return "No news available"

    positive = ["rise", "gain", "up", "strong", "profit"]
    negative = ["fall", "drop", "down", "loss", "weak"]

    score = 0
    for entry in feed.entries[:5]:
        title = entry.title.lower()
        for w in positive:
            if w in title:
                score += 1
        for w in negative:
            if w in title:
                score -= 1

    if score > 0:
        return "🟢 Positive sentiment"
    elif score < 0:
        return "🔴 Negative sentiment"
    return "🟡 Neutral sentiment"

# ---------------- MAIN APP ----------------
if run:
    symbols = [s.strip().upper() for s in symbols_input.split(",")]

    for symbol in symbols:
        st.divider()

        data = yf.Ticker(symbol).history(period=period)

        if data.empty:
            st.error(f"No data for {symbol}")
            continue

        info = get_company_info(symbol)

        start = data["Close"].iloc[0]
        end = data["Close"].iloc[-1]
        change_pct = ((end - start) / start) * 100

        # ---------------- COMPANY CARD ----------------
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

        col1.metric("Start Price", round(start, 2))
        col2.metric("End Price", round(end, 2))
        col3.metric("Change %", round(change_pct, 2))

        # ---------------- CHARTS ----------------
        st.markdown("### 📈 Price Chart")
        st.line_chart(data["Close"])

        st.markdown("### 📊 Volume")
        st.bar_chart(data["Volume"])

        # ---------------- MOVING AVERAGES ----------------
        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()

        st.markdown("### 📉 Moving Averages")
        st.line_chart(data[["Close", "MA20", "MA50"]])

        # ---------------- NEWS ----------------
        st.markdown("### 📰 News Sentiment")
        st.write(get_news_sentiment(symbol))

        # ---------------- SUMMARY ----------------
        st.markdown("### 📌 Insight")

        if change_pct > 0:
            st.success("Uptrend detected — bullish momentum.")
        else:
            st.error("Downtrend detected — bearish pressure.")

        st.caption("Educational use only — not financial advice.")
