import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import os

# Import the ML Engine directly (No FastAPI needed)
from backend.playground_engine import QuantPlaygroundEngine
engine = QuantPlaygroundEngine()

# Must be the first command
st.set_page_config(page_title="Fin-OS Enterprise | Quant AI", layout="wide", page_icon="🏦")

# ==========================================
# INVESTOR-GRADE UI POLISH (CSS INJECTION)
# ==========================================
st.markdown("""
    <style>
    /* Global Background and Fonts */
    .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stMetricValue"] {
        color: #00FF41 !important;
        font-weight: 700 !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00FF41 0%, #008F11 100%);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #008F11 0%, #00FF41 100%);
        box-shadow: 0 0 15px #00FF41;
        border-color: #00FF41;
        color: #FFFFFF;
    }
    div[data-testid="stCodeBlock"] {
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)


st.title("🏦 Fin-OS Enterprise")
st.markdown("### The Autonomous AI Operating System for Quantitative Finance")
st.caption("Powered by Llama-3.3-70b & Machine Learning Ensembles | Confidential Investor Demo")
st.divider()

st.header("Generative AI Strategy Builder")
st.markdown("Natural Language to Python Execution. Describe any financial thesis, and the Llama-3 AI will instantly translate it into vectorized pandas code and backtest it.")

col3, col4 = st.columns([1, 2])
with col3:
    ticker_play = st.text_input("Asset Ticker", value="^NSEI", key="ticker_play")
    strategy = st.text_area("Investment Thesis (Natural Language)", 
                            value="Buy when the 50-day moving average crosses above the 200-day moving average, and sell when it crosses below.",
                            height=150)
    
    if st.button("Execute AI Vectorized Backtest", type="primary"):
        with st.spinner("Llama-3 is architecting your Python code..."):
            try:
                # DIRECT FUNCTION CALLS INSTEAD OF HTTP API
                generated_code = engine.nlp_to_code(strategy)
                data = engine.run_vectorized_backtest(ticker_play, generated_code)
                
                if "error" in data:
                    st.error(f"Execution Error: {data['error']}")
                else:
                    st.success("✅ Backtest Simulation Complete")
                    
                    st.markdown("### 📊 Performance Analytics")
                    m1, m2 = st.columns(2)
                    m1.metric("Total Return", f"{data['total_return']}%")
                    m2.metric("Sharpe Ratio", f"{data['sharpe_ratio']}")
                    m3, m4 = st.columns(2)
                    m3.metric("Max Drawdown", f"{data['max_drawdown']}%")
                    m4.metric("Win Rate", f"{data['win_rate']}%")
                    
                    st.markdown("### ⚙️ Llama-3 Generated Source Code")
                    st.code(data['generated_code'], language='python')
                    
                    st.session_state['equity_curve'] = data['equity_curve']
            except Exception as e:
                st.error(f"Internal Error: {e}")

with col4:
    st.subheader("5-Year Equity Curve Simulation")
    if 'equity_curve' in st.session_state:
        eq = st.session_state['equity_curve']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=eq['dates'], y=eq['strategy'], mode='lines', name='AI Strategy', line=dict(color='#00FF41', width=2)))
        fig.add_trace(go.Scatter(x=eq['dates'], y=eq['market'], mode='lines', name='Buy & Hold Benchmark', line=dict(color='#555555', width=2)))
        
        # Institutional Chart Styling
        fig.update_layout(
            title="AI Strategy vs Benchmark Alpha",
            xaxis_title="Timeline",
            yaxis_title="Cumulative Portfolio Multiplier",
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF'),
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        fig.update_xaxes(showgrid=False, gridcolor='#333333')
        fig.update_yaxes(showgrid=True, gridcolor='#333333')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Awaiting strategy execution...")
