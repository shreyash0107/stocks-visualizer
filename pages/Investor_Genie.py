import streamlit as st
import yfinance as yf
from datetime import datetime
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stock Chatbot", layout="wide")
st.title("💹 Stock Chatbot ")

# --- INITIALIZE GEMINI CLIENT ---
# DANGER: Hardcoding the API key is a significant security risk.
# This code is provided as requested, but it is not a recommended practice.
API_KEY ="AIzaSyDehPlhCVx3f7l4J82sVL_JYtD9XTTfBMo"  # <-- Paste your API key here
genai.configure(api_key=API_KEY)

# --- INITIALIZE CHAT HISTORY AND MODEL ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash')
    # Start a new chat session and provide the system instruction here.
    st.session_state.chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [
                "You are Investor Genie, an AI assistant specialized in providing information about public companies and stock market trends. Provide accurate, clear, and helpful responses."]},
            {"role": "model", "parts": ["Understood. I am ready to help with your stock queries."]}
        ]
    )
    # The first message from the bot is added to the display messages
    st.session_state.messages.append(
        {"role": "assistant", "content": "Hello! I am Investor Genie. How can I assist you today?"})


# --- FUNCTION TO FETCH STOCK INFO ---
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            return f"No information found for ticker: {ticker}. Please check if the ticker symbol is correct."
        return f"Company: {info.get('longName', 'N/A')}\nPrice: {info.get('currentPrice', 'N/A')}\nMarket Cap: {info.get('marketCap', 'N/A')}"
    except Exception as e:
        return f"Error fetching stock info: {e}"


# --- MAIN LOGIC ---
st.markdown("---")
st.subheader("💬 Chat History")

# Display messages using Streamlit's built-in chat UI
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])

# User input is handled by Streamlit's chat_input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        if user_input.lower().startswith("stock:"):
            ticker = user_input.split(":")[1].strip()
            response_msg = f"💹 Stock Info for {ticker}:\n{get_stock_info(ticker)}"
        else:
            try:
                response = st.session_state.chat_session.send_message(user_input)
                response_msg = response.text
            except Exception as e:
                response_msg = f"Error communicating with Gemini AI: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response_msg})
    st.rerun()

