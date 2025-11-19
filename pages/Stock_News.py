import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock News", layout="wide")
st.title("📰 Stock-Specific News")

# --- CONFIG ---
API_KEY = '0fa5dbb96bc14cd8b575ffa8ea8b6322'  # Replace with your NewsAPI key
NEWS_LIMIT = 5  # Number of news articles per ticker

# --- FUNCTION TO FETCH NEWS ---
@st.cache_data(ttl=3600)
def fetch_news(ticker):
    """
    Fetch latest news for a given stock ticker using NewsAPI.
    Returns a list of articles with title, description, url, and publishedAt.
    """
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    url = (
        f'https://newsapi.org/v2/everything?'
        f'q={ticker}&'
        f'from={from_date}&'
        f'sortBy=publishedAt&'
        f'language=en&'
        f'apiKey={API_KEY}'
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        articles = []
        for article in data.get('articles', [])[:NEWS_LIMIT]:
            articles.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'publishedAt': article.get('publishedAt')
            })

        if not articles:
            return [{'title': 'No news found', 'description': '', 'url': '', 'publishedAt': ''}]
        return articles

    except requests.exceptions.RequestException as e:
        return [{'title': 'Error fetching news', 'description': str(e), 'url': '', 'publishedAt': ''}]

# --- MAIN CODE ---
if "selected_tickers" in st.session_state and st.session_state["selected_tickers"]:
    tickers = st.session_state["selected_tickers"]
    st.write(f"Showing latest stock news for: **{', '.join(tickers)}**")

    for ticker in tickers:
        st.subheader(f"🔹 {ticker} News")
        articles = fetch_news(ticker)

        for i, article in enumerate(articles):
            st.write(f"**{i+1}. {article['title']}**")
            if article['publishedAt']:
                st.caption(article['publishedAt'])
            st.write(article['description'])
            if article['url']:
                st.markdown(f"[Read more]({article['url']})")
            st.markdown("---")

else:
    st.warning("⚠️ No tickers selected in Home page. Please go back and add some.")
