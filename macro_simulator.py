import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random

# ==========================================
# Configuration & Setup
# ==========================================
st.set_page_config(
    page_title="Global Macro Trader Simulator",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for a sleek terminal-like look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .news-ticker {
        font-family: 'Fira Code', monospace;
        background-color: #111827;
        color: #10B981;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #10B981;
        margin-bottom: 20px;
    }
    
    .news-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #F87171;
        margin-bottom: 5px;
    }
    
    .score-card {
        background-color: #F3F4F6;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    
    .rank-S { color: #8B5CF6; font-size: 3rem; font-weight: 800; }
    .rank-A { color: #3B82F6; font-size: 3rem; font-weight: 800; }
    .rank-B { color: #10B981; font-size: 3rem; font-weight: 800; }
    .rank-C { color: #F59E0B; font-size: 3rem; font-weight: 800; }
    .rank-D { color: #EF4444; font-size: 3rem; font-weight: 800; }
    
    </style>
""", unsafe_allow_html=True)

# ==========================================
# Base Asset Parameters
# ==========================================
# mu = Expected Annual Return, sigma = Annual Volatility
BASE_ASSETS = {
    "FX": {"mu": 0.02, "sigma": 0.08},
    "BOND_3M": {"mu": 0.04, "sigma": 0.01},
    "BOND_10Y": {"mu": 0.05, "sigma": 0.08},
    "INDEX": {"mu": 0.08, "sigma": 0.15},
    "EQ_HIGH_BETA": {"mu": 0.12, "sigma": 0.25},
    "EQ_NEUTRAL": {"mu": 0.08, "sigma": 0.15},
    "EQ_LOW_BETA": {"mu": 0.05, "sigma": 0.10},
}

# ==========================================
# Dynamic Scenario Generator Engine
# ==========================================
def generate_dynamic_scenario():
    """Generates a unique economic scenario by combining regions, events, and severities."""
    
    regions = ["United States", "Eurozone", "Asia-Pacific", "Global"]
    events = [
        {
            "theme": "Inflation Shock",
            "headlines": [
                "Unexpected CPI Spike in {region} Shocks Markets",
                "{region} Supply Chain Collapse Triggers Hyperinflation Fears",
                "Energy Crisis in {region} Drives Prices to Record Highs"
            ],
            "body": "Recent data from {region} indicates that inflationary pressures are far worse than anticipated. Central banks are likely to abandon any dovish plans and hike rates aggressively to contain the damage.",
            "impact_base": {
                "FX": {"mu_adj": 0.04, "sig_adj": 1.2}, 
                "BOND_3M": {"mu_adj": 0.02, "sig_adj": 1.1},
                "BOND_10Y": {"mu_adj": -0.15, "sig_adj": 1.5},
                "INDEX": {"mu_adj": -0.10, "sig_adj": 1.5},
                "EQ_HIGH_BETA": {"mu_adj": -0.25, "sig_adj": 1.8},
                "EQ_NEUTRAL": {"mu_adj": -0.10, "sig_adj": 1.2},
                "EQ_LOW_BETA": {"mu_adj": 0.02, "sig_adj": 1.0},
            }
        },
        {
            "theme": "Tech & Productivity Boom",
            "headlines": [
                "Breakthrough Tech Announced in {region}, Productivity Surges",
                "{region} Leads Global AI Revolution with New Infrastructure",
                "Massive Automation Adoption in {region} Signals Golden Economic Era"
            ],
            "body": "A major technological milestone has been reached in {region}, leading to massive upgrades in GDP forecasts. Investors are pouring capital into risk assets, completely ignoring traditional valuations.",
            "impact_base": {
                "FX": {"mu_adj": -0.02, "sig_adj": 1.1}, 
                "BOND_3M": {"mu_adj": 0.00, "sig_adj": 1.0},
                "BOND_10Y": {"mu_adj": -0.02, "sig_adj": 1.2},
                "INDEX": {"mu_adj": 0.15, "sig_adj": 1.2},
                "EQ_HIGH_BETA": {"mu_adj": 0.35, "sig_adj": 1.5},
                "EQ_NEUTRAL": {"mu_adj": 0.12, "sig_adj": 1.0},
                "EQ_LOW_BETA": {"mu_adj": -0.05, "sig_adj": 1.0},
            }
        },
        {
            "theme": "Economic Recession",
            "headlines": [
                "{region} Plunges into Unexpected Recession",
                "Severe Demand Destruction Hits {region} Economy",
                "{region} Manufacturing PMI Collapses to Decade Lows"
            ],
            "body": "Consumer spending has frozen across {region} as unemployment begins to tick up. Markets are now pricing in emergency rate cuts, sparking a massive rally in safe-haven assets.",
            "impact_base": {
                "FX": {"mu_adj": -0.05, "sig_adj": 1.3}, 
                "BOND_3M": {"mu_adj": -0.02, "sig_adj": 0.8},
                "BOND_10Y": {"mu_adj": 0.12, "sig_adj": 1.2},
                "INDEX": {"mu_adj": -0.15, "sig_adj": 1.4},
                "EQ_HIGH_BETA": {"mu_adj": -0.20, "sig_adj": 1.6},
                "EQ_NEUTRAL": {"mu_adj": -0.10, "sig_adj": 1.1},
                "EQ_LOW_BETA": {"mu_adj": 0.08, "sig_adj": 0.9},
            }
        }
    ]
    
    region = random.choice(regions)
    event = random.choice(events)
    headline_template = random.choice(event["headlines"])
    
    severity_multiplier = round(random.uniform(0.5, 2.0), 2)
    severity_label = "MILD"
    if severity_multiplier > 1.5:
        severity_label = "SEVERE"
    elif severity_multiplier < 0.8:
        severity_label = "WEAK"
        
    dynamic_impact = {}
    for asset, params in event["impact_base"].items():
        dynamic_impact[asset] = {
            "mu_adj": params["mu_adj"] * severity_multiplier,
            "sig_adj": 1.0 + ((params["sig_adj"] - 1.0) * severity_multiplier)
        }
        
    scenario = {
        "id": "dynamic_generated",
        "headline": headline_template.format(region=region),
        "body": f"[{severity_label} IMPACT DETECTED] " + event["body"].format(region=region),
        "impact": dynamic_impact
    }
    
    return scenario

# ==========================================
# Session State Initialization
# ==========================================
if 'scenario' not in st.session_state:
    st.session_state.scenario = None
if 'phase' not in st.session_state:
    st.session_state.phase = 1

def generate_new_scenario():
    st.session_state.scenario = generate_dynamic_scenario()
    st.session_state.phase = 2

def reset_game():
    st.session_state.scenario = None
    st.session_state.phase = 1

# ==========================================
# UI Layout
# ==========================================
st.title("🌍 Global Macro Trader Simulator")
st.markdown("Navigate economic shocks, allocate your portfolio, and survive the Monte Carlo stress test.")

if st.session_state.phase == 1:
    st.markdown("### Phase 1: Awaiting Market Signal...")
    if st.button("📡 Intercept Latest Macro News", type="primary", use_container_width=True):
        generate_new_scenario()
        st.rerun()

elif st.session_state.phase >= 2:
    # Display News
    scenario = st.session_state.scenario
    st.markdown(f"""
        <div class="news-ticker">
            <div class="news-title">{scenario['headline']}</div>
            <div>{scenario['body']}</div>
            <div style="margin-top:10px; font-size:0.8rem; color:#9CA3AF;">Source: Global Financial Terminal | Timestamp: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    """, unsafe_allow_html=True)

    # Strategy Builder Form
    st.markdown("### Phase 2: Strategy Builder & Allocation")
    st.markdown("Allocate 100% of your capital. Choose your directions (Long/Short) wisely based on the news.")
    
    with st.form("portfolio_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Macro Assets")
            target_region = st.selectbox("Primary Region Focus", ["United States", "Eurozone", "Japan", "United Kingdom"])
            
            fx_pair = st.selectbox("FX Pair Selection", ["EUR/USD", "USD/JPY", "GBP/USD"])
            fx_dir = st.radio("FX Direction", ["Long", "Short"], horizontal=True, key="fx_dir")
            fx_weight = st.slider("FX Allocation (%)", 0, 100, 10)
            
            bond_type = st.selectbox("Fixed Income Maturity", ["3-Month T-Bill (Cash Proxy)", "10-Year Govt Bond"])
            bond_dir = st.radio("Bond Direction", ["Long", "Short"], horizontal=True, key="bond_dir")
            bond_weight = st.slider("Fixed Income Allocation (%)", 0, 100, 40)
            
        with col2:
            st.markdown("#### Equities & Risk Assets")
            idx_dir = st.radio("Equity Index (CFD) Direction", ["Long", "Short"], horizontal=True, key="idx_dir")
            idx_weight = st.slider("Index Allocation (%)", 0, 100, 20)
            
            eq_beta = st.selectbox("Individual Equities Style", ["High Beta (Tech/Growth)", "Neutral Beta (Broad Market)", "Low Beta (Defensives/Utilities)"])
            eq_dir = st.radio("Equities Direction", ["Long", "Short"], horizontal=True, key="eq_dir")
            eq_weight = st.slider("Equities Allocation (%)", 0, 100, 30)

        total_weight = fx_weight + bond_weight + idx_weight + eq_weight
        
        st.markdown(f"**Total Allocation:** {total_weight}% (Will be normalized to 100% upon execution)")
        
        submitted = st.form_submit_button("🚀 Execute Strategy & Run Monte Carlo", type="primary")

    if submitted:
        if total_weight == 0:
            st.error("Total allocation cannot be 0%. Please allocate your capital.")
        else:
            # Normalize weights
            weights = {
                "FX": fx_weight / total_weight,
                "BOND": bond_weight / total_weight,
                "INDEX": idx_weight / total_weight,
                "EQUITY": eq_weight / total_weight
            }
            
            # Map user selections to asset keys
            b_key = "BOND_3M" if "3-Month" in bond_type else "BOND_10Y"
            e_key = "EQ_HIGH_BETA" if "High" in eq_beta else "EQ_NEUTRAL" if "Neutral" in eq_beta else "EQ_LOW_BETA"
            
            dirs = {
                "FX": 1 if fx_dir == "Long" else -1,
                "BOND": 1 if bond_dir == "Long" else -1,
                "INDEX": 1 if idx_dir == "Long" else -1,
                "EQUITY": 1 if eq_dir == "Long" else -1
            }
            
            portfolio_map = {
                "FX": "FX",
                "BOND": b_key,
                "INDEX": "INDEX",
                "EQUITY": e_key
            }
            
            # ==========================================
            # Monte Carlo Simulation Engine (Phase 3)
            # ==========================================
            st.markdown("---")
            st.markdown("### Phase 3: Monte Carlo Stress Test (1 Year, 100 Paths)")
            
            trading_days = 252
            num_paths = 100
            initial_portfolio = 1000000  # $1,000,000 starting capital
            
            # Generate paths for each asset
            dt = 1 / trading_days
            port_paths = np.zeros((trading_days, num_paths))
            port_paths[0] = initial_portfolio
            
            daily_returns = np.zeros((trading_days - 1, num_paths))
            
            for k in ["FX", "BOND", "INDEX", "EQUITY"]:
                asset = portfolio_map[k]
                w = weights[k]
                d = dirs[k]
                
                # Fetch base parameters and apply scenario adjustments
                base_mu = BASE_ASSETS[asset]["mu"]
                base_sig = BASE_ASSETS[asset]["sigma"]
                
                adj_mu = scenario["impact"][asset]["mu_adj"]
                adj_sig = scenario["impact"][asset]["sig_adj"]
                
                # Calculate final expected return and volatility for this asset
                final_mu = (base_mu + adj_mu) * d
                final_sig = base_sig * adj_sig
                
                # Generate Geometric Brownian Motion daily returns for this asset
                asset_dr = np.random.normal((final_mu - 0.5 * final_sig**2) * dt, final_sig * np.sqrt(dt), (trading_days - 1, num_paths))
                
                # Add to portfolio daily returns weighted
                daily_returns += w * asset_dr
                
            # Construct price paths from aggregated daily returns
            for t in range(1, trading_days):
                port_paths[t] = port_paths[t-1] * np.exp(daily_returns[t-1])
                
            # Calculate Risk Metrics
            final_values = port_paths[-1, :]
            mean_final_value = np.mean(final_values)
            expected_return = (mean_final_value / initial_portfolio) - 1
            
            # Portfolio Volatility (Annualized from daily standard deviation of the aggregate returns)
            port_vol = np.std(daily_returns) * np.sqrt(trading_days)
            
            # Sharpe Ratio (Assuming risk-free rate = 2%)
            rf = 0.02
            sharpe_ratio = (expected_return - rf) / port_vol if port_vol > 0 else 0
            
            # Max Drawdown across all paths
            cumulative_max = np.maximum.accumulate(port_paths, axis=0)
            drawdowns = (cumulative_max - port_paths) / cumulative_max
            max_dd = np.max(drawdowns)
            
            # Ranking Logic
            rank = "D"
            if sharpe_ratio > 2.0: rank = "S"
            elif sharpe_ratio > 1.0: rank = "A"
            elif sharpe_ratio > 0.5: rank = "B"
            elif sharpe_ratio > 0.0: rank = "C"
            
            # Visualization
            fig = go.Figure()
            for i in range(num_paths):
                fig.add_trace(go.Scatter(
                    x=np.arange(trading_days),
                    y=port_paths[:, i],
                    mode='lines',
                    line=dict(width=1, color='rgba(59, 130, 246, 0.1)'),
                    showlegend=False
                ))
            
            # Highlight the mean path
            mean_path = np.mean(port_paths, axis=1)
            fig.add_trace(go.Scatter(
                x=np.arange(trading_days),
                y=mean_path,
                mode='lines',
                line=dict(width=3, color='#F87171'),
                name='Mean Path'
            ))
            
            fig.update_layout(
                title="Simulated Portfolio Value (1 Year Horizon)",
                xaxis_title="Trading Days",
                yaxis_title="Portfolio Value ($)",
                template="plotly_white",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display Metrics
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Expected Return", f"{expected_return * 100:.2f}%")
                st.metric("Portfolio Volatility (Ann.)", f"{port_vol * 100:.2f}%")
            with m_col2:
                st.metric("Max Drawdown", f"-{max_dd * 100:.2f}%")
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
            with m_col3:
                st.markdown(f"""
                    <div class="score-card">
                        <div style="font-weight:600; color:#6B7280; text-transform:uppercase;">Trader Rank</div>
                        <div class="rank-{rank}">{rank}</div>
                    </div>
                """, unsafe_allow_html=True)
                
            if st.button("🔄 Play Again", use_container_width=True):
                reset_game()
                st.rerun()