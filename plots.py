import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Sequence

def line_portfolio(series: pd.Series, title: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines", name="Portfolio Index"))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Index")
    return fig

def line_prices(prices: pd.DataFrame, title: str):
    fig = go.Figure()
    for c in prices.columns:
        fig.add_trace(go.Scatter(x=prices.index, y=prices[c], mode="lines", name=c))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
    return fig

def pie_allocation(tickers: Sequence[str], weights):
    df = pd.DataFrame({"Ticker": tickers, "Weight": weights})
    fig = px.pie(df, names="Ticker", values="Weight", title="Allocation (Equal Weights by Default)")
    return fig

def mc_fan_chart(paths: pd.DataFrame, title="Monte Carlo Simulation"):
    # Plot a thin subset of paths to keep it light
    fig = go.Figure()
    subset = paths.iloc[:, : min(150, paths.shape[1])]
    for col in subset.columns:
        fig.add_trace(go.Scatter(y=subset[col], mode="lines", line=dict(width=1), opacity=0.15, showlegend=False))
    fig.update_layout(title=title, xaxis_title="Days", yaxis_title="Portfolio Value")
    return fig
