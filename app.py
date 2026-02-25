"""
🇮🇳 Indian Stock Market Dashboard
===================================
A comprehensive stock market analysis dashboard built with Streamlit.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

from config import INDIAN_STOCKS, MA_SHORT, MA_MEDIUM, MA_LONG
from src.data_fetcher import StockDataFetcher
from src.data_processor import StockDataProcessor
from src.csv_handler import CSVHandler
from src.scheduler import StockScheduler
from src.logger import logger

# ─── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="🇮🇳 Indian Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Header Styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .dashboard-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .dashboard-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #2a2a4a 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.25);
    }
    
    .metric-label {
        color: #a0a0c0;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 0.4rem;
    }
    
    .metric-delta-positive {
        color: #00d4aa;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .metric-delta-negative {
        color: #ff6b6b;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Section Headers */
    .section-header {
        color: #e0e0ff;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        letter-spacing: -0.3px;
    }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #252545 100%);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12122a 0%, #1a1a35 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.15);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #c0c0ff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 30, 63, 0.8);
        border-radius: 10px;
        color: #a0a0c0;
        border: 1px solid rgba(102, 126, 234, 0.15);
        padding: 0.5rem 1.2rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-active {
        background: rgba(0, 212, 170, 0.15);
        color: #00d4aa;
        border: 1px solid rgba(0, 212, 170, 0.3);
    }
    
    .status-inactive {
        background: rgba(255, 107, 107, 0.15);
        color: #ff6b6b;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #606080;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid rgba(102, 126, 234, 0.1);
        margin-top: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Initialize Session State ──────────────────────────────────────────────────


@st.cache_resource
def get_fetcher():
    return StockDataFetcher()


@st.cache_resource
def get_processor():
    return StockDataProcessor()


@st.cache_resource
def get_csv_handler():
    return CSVHandler()


@st.cache_resource
def get_scheduler():
    return StockScheduler()


fetcher = get_fetcher()
processor = get_processor()
csv_handler = get_csv_handler()
scheduler = get_scheduler()

if "stock_data" not in st.session_state:
    st.session_state.stock_data = None
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = None
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = None

# ─── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="dashboard-header">
        <h1>📈 Indian Stock Market Dashboard</h1>
        <p>Real-time stock analysis with moving averages, volume trends, and technical indicators — powered by Alpha Vantage</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")
    st.markdown("---")

    # Stock Selection
    st.markdown("### 📊 Select Stock")
    stock_name = st.selectbox(
        "Choose a stock",
        options=list(INDIAN_STOCKS.keys()),
        index=0,
        help="Select an Indian stock to analyze",
    )
    selected_symbol = INDIAN_STOCKS[stock_name]

    st.markdown("---")

    # Data Options
    st.markdown("### ⚙️ Data Settings")
    output_size = st.radio(
        "Data Range",
        options=["compact", "full"],
        index=0,
        help="Compact = last 100 days, Full = 20+ years",
    )

    ma_periods = st.multiselect(
        "Moving Average Periods",
        options=[5, 10, 20, 50, 100, 200],
        default=[MA_SHORT, MA_MEDIUM, MA_LONG],
        help="Select SMA periods to display",
    )

    st.markdown("---")

    # Technical Indicators Toggle
    st.markdown("### 📐 Technical Indicators")
    show_ema = st.checkbox("Show EMA (12, 26)", value=False)
    show_rsi = st.checkbox("Show RSI (14)", value=False)
    show_bollinger = st.checkbox("Show Bollinger Bands", value=False)
    show_daily_returns = st.checkbox("Show Daily Returns", value=False)

    st.markdown("---")

    # Fetch Button
    col_fetch1, col_fetch2 = st.columns(2)
    with col_fetch1:
        fetch_clicked = st.button("🔄 Fetch Data", use_container_width=True)
    with col_fetch2:
        load_csv_clicked = st.button("📂 Load CSV", use_container_width=True)

    st.markdown("---")

    # Scheduler Controls
    st.markdown("### ⏰ Auto-Update Scheduler")
    scheduler_interval = st.slider(
        "Update interval (min)", min_value=5, max_value=120, value=30, step=5
    )

    col_sched1, col_sched2 = st.columns(2)
    with col_sched1:
        start_scheduler = st.button("▶ Start", use_container_width=True)
    with col_sched2:
        stop_scheduler = st.button("⏹ Stop", use_container_width=True)

    if scheduler.is_running:
        st.markdown(
            '<span class="status-badge status-active">● Auto-Update Active</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-inactive">● Scheduler Inactive</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="color: #606080; font-size: 0.8rem;">
            <strong>Current Time:</strong><br>
            {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Handle Scheduler Actions ──────────────────────────────────────────────────

if start_scheduler:
    scheduler.add_stock(selected_symbol)
    scheduler.start(interval_minutes=scheduler_interval)
    st.sidebar.success(f"Scheduler started for {stock_name}!")

if stop_scheduler:
    scheduler.stop()
    st.sidebar.info("Scheduler stopped.")

# ─── Fetch / Load Data ─────────────────────────────────────────────────────────

if fetch_clicked:
    with st.spinner(f"🔄 Fetching data for **{stock_name}** ({selected_symbol})..."):
        logger.info(f"User initiated fetch for {stock_name} ({selected_symbol})")
        df = fetcher.fetch_daily_stock_data(selected_symbol, output_size=output_size)

        if df is not None:
            st.session_state.stock_data = df
            st.session_state.selected_symbol = selected_symbol
            st.session_state.last_fetch_time = datetime.now()

            # Auto-save to CSV
            csv_handler.save_to_csv(df, selected_symbol)
            st.success(
                f"✅ Fetched {len(df)} records for {stock_name}! Data auto-saved."
            )
            logger.info(f"Successfully fetched and saved data for {stock_name}")
        else:
            st.error(
                "❌ Failed to fetch data. Check your API key or try again later. See logs for details."
            )
            logger.error(f"Failed to fetch data for {stock_name}")

if load_csv_clicked:
    with st.spinner(f"📂 Loading cached data for **{stock_name}**..."):
        df = csv_handler.load_from_csv(selected_symbol)

        if df is not None:
            st.session_state.stock_data = df
            st.session_state.selected_symbol = selected_symbol
            st.session_state.last_fetch_time = None
            st.success(f"✅ Loaded {len(df)} records from CSV!")
        else:
            st.warning("⚠️ No cached CSV found. Fetch data first.")

# ─── Main Dashboard Content ────────────────────────────────────────────────────

if st.session_state.stock_data is not None:
    df = st.session_state.stock_data.copy()

    # ─── Summary Metrics ───────────────────────────────────────────────────
    stats = processor.get_summary_statistics(df)

    st.markdown(
        '<div class="section-header">📊 Market Overview — '
        + stock_name
        + "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    delta_color = "metric-delta-positive" if stats["price_change"] >= 0 else "metric-delta-negative"
    delta_symbol = "▲" if stats["price_change"] >= 0 else "▼"

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Latest Close</div>
                <div class="metric-value">₹{stats['latest_close']:,.2f}</div>
                <div class="{delta_color}">{delta_symbol} {stats['price_change_pct']}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Period High</div>
                <div class="metric-value">₹{stats['period_high']:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Period Low</div>
                <div class="metric-value">₹{stats['period_low']:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Avg Volume</div>
                <div class="metric-value">{stats['avg_volume']:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Records</div>
                <div class="metric-value">{stats['total_records']}</div>
                <div style="color: #a0a0c0; font-size: 0.75rem;">{stats['date_range_start']} → {stats['date_range_end']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Charts ────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Closing Price & MAs",
            "📊 Volume Trends",
            "📉 Candlestick",
            "📐 Technical Indicators",
            "📋 Raw Data",
        ]
    )

    # ─── TAB 1: Closing Price & Moving Averages ───────────────────────────
    with tab1:
        st.markdown(
            '<div class="section-header">Closing Price with Moving Averages</div>',
            unsafe_allow_html=True,
        )

        df_ma = processor.calculate_moving_averages(df, periods=ma_periods)

        fig_ma = go.Figure()

        # Closing Price
        fig_ma.add_trace(
            go.Scatter(
                x=df_ma.index,
                y=df_ma["Close"],
                mode="lines",
                name="Close Price",
                line=dict(color="#667eea", width=2),
                fill="tozeroy",
                fillcolor="rgba(102, 126, 234, 0.08)",
            )
        )

        # Moving Averages
        ma_colors = {
            5: "#ff6b6b",
            10: "#ffa726",
            20: "#00d4aa",
            50: "#ff9ff3",
            100: "#54a0ff",
            200: "#ffd93d",
        }

        for period in ma_periods:
            col_name = f"SMA_{period}"
            if col_name in df_ma.columns:
                fig_ma.add_trace(
                    go.Scatter(
                        x=df_ma.index,
                        y=df_ma[col_name],
                        mode="lines",
                        name=f"SMA {period}",
                        line=dict(
                            color=ma_colors.get(period, "#ffffff"),
                            width=1.5,
                            dash="dot",
                        ),
                    )
                )

        # EMA overlay
        if show_ema:
            df_ema = processor.calculate_ema(df)
            fig_ma.add_trace(
                go.Scatter(
                    x=df_ema.index,
                    y=df_ema["EMA_12"],
                    mode="lines",
                    name="EMA 12",
                    line=dict(color="#e056fd", width=1.5),
                )
            )
            fig_ma.add_trace(
                go.Scatter(
                    x=df_ema.index,
                    y=df_ema["EMA_26"],
                    mode="lines",
                    name="EMA 26",
                    line=dict(color="#f9ca24", width=1.5),
                )
            )

        # Bollinger Bands overlay
        if show_bollinger:
            df_bb = processor.calculate_bollinger_bands(df)
            fig_ma.add_trace(
                go.Scatter(
                    x=df_bb.index,
                    y=df_bb["BB_Upper"],
                    mode="lines",
                    name="BB Upper",
                    line=dict(color="rgba(255,107,107,0.4)", width=1, dash="dash"),
                )
            )
            fig_ma.add_trace(
                go.Scatter(
                    x=df_bb.index,
                    y=df_bb["BB_Lower"],
                    mode="lines",
                    name="BB Lower",
                    line=dict(color="rgba(255,107,107,0.4)", width=1, dash="dash"),
                    fill="tonexty",
                    fillcolor="rgba(255, 107, 107, 0.05)",
                )
            )

        fig_ma.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(15,15,26,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=550,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11),
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(102,126,234,0.08)",
                rangeslider=dict(visible=False),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(102,126,234,0.08)",
                title="Price (₹)",
            ),
            hovermode="x unified",
        )

        st.plotly_chart(fig_ma, use_container_width=True)

    # ─── TAB 2: Volume Trends ─────────────────────────────────────────────
    with tab2:
        st.markdown(
            '<div class="section-header">Volume Analysis</div>',
            unsafe_allow_html=True,
        )

        df_vol = processor.calculate_volume_ma(df, period=20)

        # Color bars based on price direction
        colors = [
            "#00d4aa" if df_vol["Close"].iloc[i] >= df_vol["Open"].iloc[i] else "#ff6b6b"
            for i in range(len(df_vol))
        ]

        fig_vol = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.35, 0.65],
            subplot_titles=("Closing Price", "Volume"),
        )

        # Price subplot
        fig_vol.add_trace(
            go.Scatter(
                x=df_vol.index,
                y=df_vol["Close"],
                mode="lines",
                name="Close",
                line=dict(color="#667eea", width=2),
            ),
            row=1,
            col=1,
        )

        # Volume bars
        fig_vol.add_trace(
            go.Bar(
                x=df_vol.index,
                y=df_vol["Volume"],
                name="Volume",
                marker_color=colors,
                opacity=0.7,
            ),
            row=2,
            col=1,
        )

        # Volume MA
        fig_vol.add_trace(
            go.Scatter(
                x=df_vol.index,
                y=df_vol["Volume_MA"],
                mode="lines",
                name="Volume MA (20)",
                line=dict(color="#ffa726", width=2),
            ),
            row=2,
            col=1,
        )

        fig_vol.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(15,15,26,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=600,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            hovermode="x unified",
        )

        fig_vol.update_yaxes(
            showgrid=True,
            gridcolor="rgba(102,126,234,0.08)",
        )
        fig_vol.update_xaxes(
            showgrid=True,
            gridcolor="rgba(102,126,234,0.08)",
        )

        st.plotly_chart(fig_vol, use_container_width=True)

    # ─── TAB 3: Candlestick Chart ─────────────────────────────────────────
    with tab3:
        st.markdown(
            '<div class="section-header">Candlestick Chart</div>',
            unsafe_allow_html=True,
        )

        fig_candle = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    increasing_line_color="#00d4aa",
                    decreasing_line_color="#ff6b6b",
                    increasing_fillcolor="rgba(0,212,170,0.5)",
                    decreasing_fillcolor="rgba(255,107,107,0.5)",
                    name="OHLC",
                )
            ]
        )

        fig_candle.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(15,15,26,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=550,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                rangeslider=dict(visible=False),
                showgrid=True,
                gridcolor="rgba(102,126,234,0.08)",
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(102,126,234,0.08)",
                title="Price (₹)",
            ),
        )

        st.plotly_chart(fig_candle, use_container_width=True)

    # ─── TAB 4: Technical Indicators ───────────────────────────────────────
    with tab4:
        st.markdown(
            '<div class="section-header">Technical Indicators</div>',
            unsafe_allow_html=True,
        )

        if show_rsi or show_daily_returns:
            indicator_rows = sum([show_rsi, show_daily_returns])
            fig_tech = make_subplots(
                rows=indicator_rows,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.12,
                subplot_titles=(
                    *(["RSI (14)"] if show_rsi else []),
                    *(["Daily Returns (%)"] if show_daily_returns else []),
                ),
            )

            current_row = 1

            if show_rsi:
                df_rsi = processor.calculate_rsi(df)
                fig_tech.add_trace(
                    go.Scatter(
                        x=df_rsi.index,
                        y=df_rsi["RSI"],
                        mode="lines",
                        name="RSI",
                        line=dict(color="#e056fd", width=2),
                    ),
                    row=current_row,
                    col=1,
                )
                # Overbought / Oversold lines
                fig_tech.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="rgba(255,107,107,0.5)",
                    annotation_text="Overbought (70)",
                    row=current_row,
                    col=1,
                )
                fig_tech.add_hline(
                    y=30,
                    line_dash="dash",
                    line_color="rgba(0,212,170,0.5)",
                    annotation_text="Oversold (30)",
                    row=current_row,
                    col=1,
                )
                current_row += 1

            if show_daily_returns:
                df_returns = processor.calculate_daily_returns(df)
                colors_ret = [
                    "#00d4aa" if r >= 0 else "#ff6b6b"
                    for r in df_returns["Daily_Return"].fillna(0)
                ]
                fig_tech.add_trace(
                    go.Bar(
                        x=df_returns.index,
                        y=df_returns["Daily_Return"],
                        name="Daily Return",
                        marker_color=colors_ret,
                        opacity=0.8,
                    ),
                    row=current_row,
                    col=1,
                )
                current_row += 1

            fig_tech.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(15,15,26,0.8)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=300 * indicator_rows,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )

            fig_tech.update_yaxes(
                showgrid=True, gridcolor="rgba(102,126,234,0.08)"
            )
            fig_tech.update_xaxes(
                showgrid=True, gridcolor="rgba(102,126,234,0.08)"
            )

            st.plotly_chart(fig_tech, use_container_width=True)
        else:
            st.info(
                "🔧 Enable **RSI** or **Daily Returns** from the sidebar to see technical indicators here."
            )

    # ─── TAB 5: Raw Data Table ─────────────────────────────────────────────
    with tab5:
        st.markdown(
            '<div class="section-header">Raw Stock Data</div>',
            unsafe_allow_html=True,
        )

        # Display summary info
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(
                f"""
                <div class="info-card">
                    <strong style="color:#c0c0ff;">📅 Date Range:</strong>
                    <span style="color:#e0e0ff;">{stats['date_range_start']} → {stats['date_range_end']}</span><br>
                    <strong style="color:#c0c0ff;">📊 Records:</strong>
                    <span style="color:#e0e0ff;">{stats['total_records']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_info2:
            st.markdown(
                f"""
                <div class="info-card">
                    <strong style="color:#c0c0ff;">💰 Price Change:</strong>
                    <span class="{delta_color}">₹{stats['price_change']:+,.2f} ({stats['price_change_pct']:+.2f}%)</span><br>
                    <strong style="color:#c0c0ff;">📈 Latest Close:</strong>
                    <span style="color:#e0e0ff;">₹{stats['latest_close']:,.2f}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.dataframe(
            df.sort_index(ascending=False).style.format(
                {
                    "Open": "₹{:,.2f}",
                    "High": "₹{:,.2f}",
                    "Low": "₹{:,.2f}",
                    "Close": "₹{:,.2f}",
                    "Volume": "{:,.0f}",
                }
            ),
            use_container_width=True,
            height=400,
        )

        # CSV Export Options
        st.markdown("<br>", unsafe_allow_html=True)
        col_export1, col_export2, col_export3 = st.columns(3)

        with col_export1:
            csv_data = df.to_csv()
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{selected_symbol.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_export2:
            if st.button("💾 Save to Disk", use_container_width=True):
                filepath = csv_handler.save_to_csv(df, selected_symbol)
                if filepath:
                    st.success(f"Saved to: `{filepath}`")

        with col_export3:
            if st.button("📁 Archive Copy", use_container_width=True):
                filepath = csv_handler.export_with_timestamp(df, selected_symbol)
                if filepath:
                    st.success(f"Archived: `{filepath}`")

    # ─── Saved Files Section ───────────────────────────────────────────────
    with st.expander("📂 Saved CSV Files", expanded=False):
        saved_files = csv_handler.list_saved_files()
        if saved_files:
            files_df = pd.DataFrame(saved_files)
            st.dataframe(files_df, use_container_width=True)
        else:
            st.info("No saved CSV files yet.")

else:
    # ─── Welcome Screen ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    col_welcome1, col_welcome2, col_welcome3 = st.columns([1, 2, 1])

    with col_welcome2:
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
                <h2 style="color: #c0c0ff; font-weight: 700;">Welcome to the Dashboard</h2>
                <p style="color: #a0a0c0; font-size: 1.1rem; max-width: 500px; margin: 0 auto;">
                    Select a stock from the sidebar and click <strong style="color: #667eea;">Fetch Data</strong> 
                    to get started with your analysis.
                </p>
                <br>
                <div style="background: linear-gradient(135deg, #1e1e3f 0%, #252545 100%); 
                            border: 1px solid rgba(102,126,234,0.2); border-radius: 14px; 
                            padding: 1.5rem; margin-top: 1rem; text-align: left;">
                    <h4 style="color: #c0c0ff; margin-bottom: 1rem;">🚀 Features at a Glance</h4>
                    <ul style="color: #a0a0c0; line-height: 2;">
                        <li>📊 <strong>Moving Averages</strong> — SMA 20, 50, 200 + custom periods</li>
                        <li>📈 <strong>Candlestick Charts</strong> — Interactive OHLC visualization</li>
                        <li>📉 <strong>Volume Analysis</strong> — Volume bars with trend overlay</li>
                        <li>📐 <strong>Technical Indicators</strong> — RSI, EMA, Bollinger Bands</li>
                        <li>💾 <strong>CSV Export</strong> — Download, save, or archive data</li>
                        <li>⏰ <strong>Auto-Update</strong> — Scheduled data refresh</li>
                        <li>📝 <strong>Logging</strong> — Full API failure tracking</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─── Footer ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="footer">
        <strong>NSE/BSE Indian Stock Market Dashboard</strong><br>
        Data provided by <a href="https://www.alphavantage.co/" target="_blank" style="color: #667eea;">Alpha Vantage</a> 
        | © 2024-2026
    </div>
    """,
    unsafe_allow_html=True,
)
