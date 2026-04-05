import streamlit as st
import plotly.graph_objects as go
import requests
import os

st.set_page_config(page_title="WealthPilot AI", layout="wide")

BACKEND_URL = st.secrets.get("BACKEND_URL") or os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding: 2rem 3rem; }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4F8EF7, #6FCF97);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ccc;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 2rem 0 1rem;
        border-left: 3px solid #4F8EF7;
        padding-left: 0.75rem;
    }
    .insight-card {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.6rem;
        color: #ddd;
        font-size: 0.9rem;
    }
    .insight-warn {
        border-left: 3px solid #F7C948;
        color: #F7C948;
    }
    .insight-tip {
        border-left: 3px solid #6FCF97;
        color: #6FCF97;
    }
    .insight-ok {
        border-left: 3px solid #4F8EF7;
        color: #4F8EF7;
    }
    .metric-card {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4F8EF7, #6FCF97) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100%;
    }
    .ai-output {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 12px;
        padding: 1.5rem;
        color: #ddd;
        line-height: 1.7;
    }
    div[data-testid="stSidebar"] {
        background: #13151f;
        border-right: 1px solid #2a2d3a;
    }
    .footer {
        text-align: center;
        color: #555;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #2a2d3a;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">WealthPilot AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">GenAI Copilot for Wealth Advisors &mdash; Powered by Groq + Llama 3</div>', unsafe_allow_html=True)

st.sidebar.markdown("## Client Profile")
age = st.sidebar.slider("Client Age", 25, 70, 40)
risk = st.sidebar.selectbox("Risk Appetite", ["Low", "Moderate", "High"])
goal = st.sidebar.selectbox("Investment Goal", ["Retirement", "Wealth Creation", "Child Education"])
horizon = st.sidebar.slider("Investment Horizon (Years)", 1, 30, 10)

st.sidebar.markdown("---")
st.sidebar.markdown("**Allocation (Auto-normalized to 100%)**")
raw_equity = st.sidebar.slider("Equity (%)", 0, 100, 60)
raw_debt = st.sidebar.slider("Debt (%)", 0, 100, 30)
raw_gold = st.sidebar.slider("Gold (%)", 0, 100, 10)

raw_total = raw_equity + raw_debt + raw_gold
if raw_total == 0:
    equity, debt, gold = 33, 33, 34
else:
    equity = round((raw_equity / raw_total) * 100)
    debt = round((raw_debt / raw_total) * 100)
    gold = 100 - equity - debt

st.sidebar.info(f"Normalized: {equity}% / {debt}% / {gold}%")

st.markdown('<div class="section-title">Portfolio Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for col, label, val, color in zip(
    [c1, c2, c3, c4],
    ["Equity", "Debt", "Gold", "Total"],
    [equity, debt, gold, equity + debt + gold],
    ["#4F8EF7", "#F7C948", "#6FCF97", "#a78bfa"]
):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-val" style="color:{color}">{val}%</div>
    </div>""", unsafe_allow_html=True)

fig = go.Figure(data=[go.Pie(
    labels=["Equity", "Debt", "Gold"],
    values=[equity, debt, gold],
    hole=0.55,
    marker_colors=["#4F8EF7", "#F7C948", "#6FCF97"],
    textinfo="label+percent",
    textfont=dict(color="white", size=13),
    hovertemplate="%{label}: %{value}%<extra></extra>"
)])
fig.update_layout(
    height=320,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-title">Rule-Based Insights</div>', unsafe_allow_html=True)

insights = []
if equity > 70 and risk != "High":
    insights.append(("warn", "High equity exposure for your risk profile"))
if debt < 20:
    insights.append(("warn", "Low debt allocation increases volatility"))
if gold > 15:
    insights.append(("warn", "High gold allocation may limit growth"))
if horizon < 5 and equity > 60:
    insights.append(("warn", "Short horizon with high equity is risky"))
if age > 55 and equity > 50:
    insights.append(("warn", "High equity near retirement increases risk"))
if age < 35 and debt > 50:
    insights.append(("tip", "Young investor can take more equity exposure"))
if goal == "Retirement" and horizon > 15 and equity < 50:
    insights.append(("tip", "Long horizon - consider more equity for compounding"))
if goal == "Child Education" and horizon < 8 and equity > 60:
    insights.append(("warn", "Education goal approaching - reduce equity to protect corpus"))
if goal == "Wealth Creation" and risk == "Low":
    insights.append(("tip", "Wealth creation with low risk may not beat inflation"))
if not insights:
    insights.append(("ok", "Portfolio looks well-balanced based on all inputs"))

for kind, text in insights:
    st.markdown(f'<div class="insight-card insight-{kind}">{text}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">AI Insights</div>', unsafe_allow_html=True)

if st.button("Generate AI Insights"):
    with st.spinner("Llama 3 is analyzing your portfolio..."):
        try:
            res = requests.post(
                f"{BACKEND_URL}/portfolio/insights",
                json={"age": age, "risk": risk, "goal": goal,
                      "horizon": horizon, "equity": equity,
                      "debt": debt, "gold": gold}
            )
            if res.status_code == 200:
                st.markdown(f'<div class="ai-output">{res.json()["insights"]}</div>', unsafe_allow_html=True)
            else:
                st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

st.markdown('<div class="section-title">Suggested Actions</div>', unsafe_allow_html=True)
recs = []
if risk == "Low": recs.append("Increase debt allocation for stability")
if risk == "High": recs.append("Increase equity exposure for growth")
if horizon > 10: recs.append("Consider long-term equity mutual funds or index funds")
if goal == "Retirement": recs.append(f"With {horizon} years to retirement, review allocation every 2-3 years")
if goal == "Child Education": recs.append("Use goal-based investment planning aligned to education year")
if age > 50: recs.append("Start gradually shifting to debt-heavy allocation as retirement nears")
if not recs: recs.append("Maintain current allocation - no changes needed")
for r in recs:
    st.markdown(f'<div class="insight-card insight-tip">{r}</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Built by Prem &nbsp;|&nbsp; AI Wealth Management Copilot &nbsp;|&nbsp; Powered by Groq + Llama 3</div>', unsafe_allow_html=True)
