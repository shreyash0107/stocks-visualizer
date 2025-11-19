import os
import pandas as pd
import streamlit as st
from datetime import datetime
import uuid

from data import fetch_prices, clean_tickers
from analytics import daily_returns, equal_weights, portfolio_daily, cumulative_index, portfolio_metrics
from monte_carlo import simulate_paths, percentiles
from plots import line_portfolio, line_prices, pie_allocation, mc_fan_chart

st.set_page_config(page_title="Stock Portfolio Visualizer", layout="wide")

# --- DATABASE SIMULATION SETUP (Always executes) ---
# This initializes the 'table' in memory.
if "saved_sessions" not in st.session_state:
    st.session_state["saved_sessions"] = {}

# --- UI PERSISTENCE FLAG ---
# This flag tracks if the analysis has successfully completed at least once.
if "analysis_ran_successfully" not in st.session_state:
    st.session_state["analysis_ran_successfully"] = False


# ---------------------------------

def save_session_data(tickers, start_date, end_date, total_invest, rf_rate, mets, name):
    """Saves the current portfolio analysis session to the simulated database."""
    session_id = str(uuid.uuid4())

    # Structure the data exactly as defined in the black book 'portfolio_analyses' table
    st.session_state["saved_sessions"][session_id] = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_name": name,
        # Inputs
        "tickers": tickers,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_invest": total_invest,
        "rf_rate": rf_rate,
        # Outputs/Metrics
        "expected_return": mets["expected_return"],
        "volatility": mets["volatility"],
        "sharpe": mets["sharpe"],
        # Add a placeholder for user ID for demonstration
        "userId": "Current_User_Demo"
    }


st.title("💼 Stock Portfolio Visualizer & Risk Estimator")

# -------- Sidebar inputs --------
st.sidebar.header("Inputs")

# FIX 1: Database record count is now outside the run_btn check (Always executes)
st.sidebar.caption(f"Database Records: {len(st.session_state['saved_sessions'])}")
st.sidebar.caption(f"User ID: Current_User_Demo")

default_tickers = "AAPL, MSFT, TSLA, NVDA"
tickers_text = st.sidebar.text_input("Stock tickers (comma separated)", default_tickers, key="ticker_input")
tickers = clean_tickers(tickers_text.split(","))

start_date = st.sidebar.date_input("Start date", pd.to_datetime("2020-01-01"), key="start_date_input")
end_date = st.sidebar.date_input("End date", pd.to_datetime("today").date(), key="end_date_input")

total_invest = st.sidebar.number_input("Total investment (base for charts)", min_value=1000.0, value=10000.0,
                                       step=500.0, key="invest_input")

rf_rate = st.sidebar.number_input("Risk-free rate (for Sharpe)", min_value=0.0, max_value=0.2, value=0.03, step=0.005,
                                  key="rf_rate_input")

# IMPORTANT: The run_btn is the ONLY trigger for running the expensive data analysis
run_btn = st.sidebar.button("Run Analysis")

# Check if inputs have changed since last run (optional logic to reset flag if needed)
# For simplicity, we will rely purely on the button click logic for now.

# Save tickers in session state so other pages can access
if "selected_tickers" not in st.session_state:
    st.session_state["selected_tickers"] = []

st.session_state["selected_tickers"] = tickers if tickers else []

st.sidebar.markdown(
    """
    **Notes**
    - US: `AAPL, MSFT`
    - India (NSE): add `.NS` → `RELIANCE.NS, TCS.NS`
    - This tool is for learning. Results use historical data and do not guarantee future returns.
    """
)


# -------- Data & analysis (Conditional block) --------
@st.cache_data(show_spinner=False)
def _fetch_cached(tickers, start, end):
    return fetch_prices(tickers, start, end)


# This block now runs ONLY if the button is pressed OR if a previous analysis was successful
if run_btn or st.session_state["analysis_ran_successfully"]:
    # ------------------------------------------------------------------------------------------------
    # --- IF BUTTON IS PRESSED (Primary Run) ---
    # ------------------------------------------------------------------------------------------------

    # Run data fetching and analysis only if the button was clicked
    if run_btn and tickers:
        prices = _fetch_cached(tickers, start_date, end_date)

        if prices.empty:
            st.warning("No price data found for the chosen tickers/dates.")
            st.stop()

        # If data fetch is successful, calculate metrics and store them for persistence
        rets = daily_returns(prices)
        w = equal_weights(len(prices.columns))
        port_daily_series = portfolio_daily(rets, w)
        port_index = cumulative_index(port_daily_series, base=100.0)
        mets = portfolio_metrics(port_daily_series, rf=rf_rate)

        # Store results and data in session_state after successful analysis
        st.session_state["analysis_ran_successfully"] = True
        st.session_state["last_prices"] = prices
        st.session_state["last_port_index"] = port_index
        st.session_state["last_w"] = w
        st.session_state["last_mets"] = mets
        st.session_state["last_rets"] = rets
        st.session_state["last_invest"] = total_invest

        st.success("Analysis completed successfully!")

    # ------------------------------------------------------------------------------------------------
    # --- DISPLAY RESULTS (Runs after successful run AND after st.rerun from Save button) ---
    # ------------------------------------------------------------------------------------------------

    if st.session_state["analysis_ran_successfully"]:
        # Retrieve stored results
        prices = st.session_state["last_prices"]
        port_index = st.session_state["last_port_index"]
        w = st.session_state["last_w"]
        mets = st.session_state["last_mets"]
        rets = st.session_state["last_rets"]
        total_invest = st.session_state["last_invest"]

        # -------- Top metrics --------
        c1, c2, c3 = st.columns(3)
        c1.metric("Expected Annual Return", f"{mets['expected_return']:.2%}")
        c2.metric("Annual Volatility", f"{mets['volatility']:.2%}")
        c3.metric("Sharpe Ratio", f"{mets['sharpe']:.2f}")

        # -------- NEW: Save Session UI (Database Table Feature) --------
        st.markdown("---")
        st.subheader("💾 Save Analysis Session to Database")
        save_col, button_col = st.columns([3, 1])

        default_session_name = f"Analysis for {', '.join(tickers)} ({datetime.now().strftime('%Y-%m-%d')})"

        # Use a consistent session_name_input key for persistence
        if "session_name_input_state" not in st.session_state:
            st.session_state["session_name_input_state"] = default_session_name

        session_name = save_col.text_input("Session Name", st.session_state["session_name_input_state"],
                                           key="session_name_input_key")

        if button_col.button("Save Data"):
            if session_name:
                # Call the saving function with all inputs and outputs
                save_session_data(tickers, start_date, end_date, total_invest, rf_rate, mets, session_name)
                st.success(
                    f"Session '{session_name}' saved successfully to the database (in-memory simulation)! The table below is updated.")
                # Reset the save input field after successful save
                st.session_state[
                    "session_name_input_state"] = f"Analysis for {', '.join(tickers)} ({datetime.now().strftime('%Y-%m-%d')})"
                st.rerun()  # Rerun to update the record count and display table
            else:
                st.warning("Please enter a name for the session.")
        # --------------------------------------------------------------------------

        # -------- Charts row 1 --------
        colA, colB = st.columns([2, 1])
        with colA:
            st.plotly_chart(line_portfolio(port_index, "Portfolio Index (Base = 100)"), use_container_width=True)
        with colB:
            st.plotly_chart(pie_allocation(list(prices.columns), w), use_container_width=True)

        # -------- Charts row 2 --------
        st.subheader("Stock Prices")
        st.plotly_chart(line_prices(prices, "Adjusted Close Prices"), use_container_width=True)

        # -------- Monte Carlo --------
        st.subheader("Monte Carlo Simulation (Next 1 Year)")
        # Use current portfolio mean/vol for GBM
        paths = simulate_paths(initial_value=total_invest,
                               mu=mets["expected_return"],
                               sigma=mets["volatility"],
                               days=252, sims=300, seed=42)
        st.plotly_chart(mc_fan_chart(paths, title="Simulated Portfolio Value Paths"), use_container_width=True)

        # Percentiles table
        end_percentiles = paths.iloc[-1].quantile([0.05, 0.5, 0.95])
        st.write("**End-of-Period Value (Percentiles):**")
        st.write({
            "5th %": f"${end_percentiles.loc[0.05]:,.0f}",
            "50th % (Median)": f"${end_percentiles.loc[0.5]:,.0f}",
            "95th %": f"${end_percentiles.loc[0.95]:,.0f}",
        })

        # -------- Downloads --------
        st.download_button("Download daily returns (CSV)", rets.to_csv().encode("utf-8"), file_name="daily_returns.csv")
        out_df = pd.DataFrame({
            "metric": ["expected_return", "volatility", "sharpe"],
            "value": [mets['expected_return'], mets['volatility'], mets['sharpe']]
        })
        st.download_button("Download metrics (CSV)", out_df.to_csv(index=False).encode("utf-8"),
                           file_name="metrics.csv")

else:
    # This executes if the analysis hasn't run yet
    st.info("Enter tickers, dates, and click **Run Analysis** to see your dashboard.")

# FIX 2: Database Table Display is now OUTSIDE of the main analysis block (Always executes)
if st.session_state["saved_sessions"]:
    st.markdown("---")
    st.subheader("Database Table Contents (Simulated)")
    # Convert the dictionary to a DataFrame for easy display
    saved_df = pd.DataFrame.from_dict(st.session_state["saved_sessions"], orient='index')
    # Reorder columns for better readability
    display_cols = ['timestamp', 'session_name', 'tickers', 'expected_return', 'volatility', 'sharpe', 'start_date',
                    'end_date', 'total_invest', 'rf_rate', 'userId']
    saved_df = saved_df[display_cols]
    st.dataframe(saved_df, use_container_width=True)
