import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Finance AI Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align: center;'>📊 Finance AI Dashboard</h1>
    <p style='text-align: center; font-size:18px;'>
    Educational finance analysis using historical data & AI-style insights
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------- INPUTS ----------------
symbols_input = st.text_input(
    "Enter stock or crypto symbols (comma separated)",
    "AAPL, ETH-USD"
)

history_period = st.selectbox(
    "Select historical period",
    ["7d", "30d", "3mo", "6mo", "1y"],
    index=1
)

analyze_btn = st.button("🚀 Analyze")

# ---------------- FUNCTIONS ----------------
def get_news_sentiment(symbol):
    """Simple sentiment using Google News RSS"""
    feed_url = f"https://news.google.com/rss/search?q={symbol}+stock"
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return "No recent news found."

    positive_words = ["rise", "gain", "up", "growth", "profit", "strong"]
    negative_words = ["fall", "drop", "down", "loss", "weak", "decline"]

    score = 0
    for entry in feed.entries[:5]:
        title = entry.title.lower()
        for w in positive_words:
            if w in title:
                score += 1
        for w in negative_words:
            if w in title:
                score -= 1

    if score > 0:
        return "🟢 News sentiment looks POSITIVE"
    elif score < 0:
        return "🔴 News sentiment looks NEGATIVE"
    else:
        return "🟡 News sentiment is NEUTRAL"

# ---------------- MAIN LOGIC ----------------
if analyze_btn:
    symbols = [s.strip().upper() for s in symbols_input.split(",")]

    for symbol in symbols:
        st.divider()
        st.subheader(f"📌 {symbol}")

        asset = yf.Ticker(symbol)
        data = asset.history(period=history_period)

        if data.empty:
            st.error("No data available")
            continue

        # ---------------- CALCULATIONS ----------------
        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()

        start_price = data["Close"].iloc[0]
        end_price = data["Close"].iloc[-1]
        change_pct = ((end_price - start_price) / start_price) * 100

        # ---------------- LAYOUT ----------------
        col1, col2 = st.columns([2, 1])

        # ---------------- PRICE + MA CHART ----------------
        with col1:
            fig, ax = plt.subplots()
            ax.plot(data.index, data["Close"], label="Close Price")
            ax.plot(data.index, data["MA20"], label="MA20")
            ax.plot(data.index, data["MA50"], label="MA50")
            ax.set_title("Price with Moving Averages")
            ax.legend()
            st.pyplot(fig)

        # ---------------- VOLUME CHART ----------------
        with col2:
            fig2, ax2 = plt.subplots()
            ax2.bar(data.index, data["Volume"])
            ax2.set_title("Volume")
            st.pyplot(fig2)

        # ---------------- SUMMARY ----------------
        st.markdown("### 📊 Summary")
        st.write(f"Start Price: **{round(start_price,2)}**")
        st.write(f"End Price: **{round(end_price,2)}**")
        st.write(f"Change: **{round(change_pct,2)}%**")

        # ---------------- AI EXPLANATION ----------------
        st.markdown("### 🤖 AI Explanation (Educational)")
        if change_pct > 0:
            st.success(
                "The price increased over this period, showing an overall upward trend. "
                "This suggests buyers were stronger than sellers."
            )
        elif change_pct < 0:
            st.error(
                "The price decreased over this period, indicating selling pressure. "
                "This suggests weaker market confidence."
            )
        else:
            st.info(
                "The price stayed mostly stable, indicating a balanced market."
            )

        # ---------------- NEWS SENTIMENT ----------------
        st.markdown("### 📰 News Sentiment")
        st.write(get_news_sentiment(symbol))

        # ---------------- DOWNLOAD DATA ----------------
        st.markdown("### ⬇️ Download Data")
        csv = data.to_csv().encode("utf-8")
        st.download_button(
            label="Download historical data as CSV",
            data=csv,
            file_name=f"{symbol}_history.csv",
            mime="text/csv"
        )

# ---------------- FOOTER ----------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; font-size:14px;'>
    ⚠️ This app is for learning purposes only. Not financial advice.
    </p>
    """,
    unsafe_allow_html=True
)