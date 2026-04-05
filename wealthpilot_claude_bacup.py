import streamlit as st
import plotly.graph_objects as go
import requests
import os

st.set_page_config(page_title="WealthPilot AI", layout="wide")

BACKEND_URL = st.secrets.get("BACKEND_URL") or os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("WealthPilot AI")
st.subheader("GenAI Copilot for Wealth Advisors - Powered by Groq + Llama 3")

st.sidebar.header("Client Profile")

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

st.sidebar.info(f"Raw: {raw_equity}/{raw_debt}/{raw_gold} = {raw_total}\nNormalized: {equity}/{debt}/{gold}")

st.write("### Portfolio Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Equity", f"{equity}%")
col2.metric("Debt", f"{debt}%")
col3.metric("Gold", f"{gold}%")
col4.metric("Total", f"{equity + debt + gold}%", delta="Valid" if (equity + debt + gold) == 100 else "Invalid")

fig = go.Figure(data=[go.Pie(
    labels=["Equity", "Debt", "Gold"],
    values=[equity, debt, gold],
    hole=0.45,
    marker_colors=["#4F8EF7", "#F7C948", "#6FCF97"],
    textinfo="label+percent"
)])
fig.update_layout(height=300, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

st.write("### Rule-Based Insights")
insights = []
if equity > 70 and risk != "High":
    insights.append("Warning: High equity exposure for your risk profile")
if debt < 20:
    insights.append("Warning: Low debt allocation increases volatility")
if gold > 15:
    insights.append("Warning: High gold allocation may limit growth")
if horizon < 5 and equity > 60:
    insights.append("Warning: Short horizon with high equity is risky")
if age > 55 and equity > 50:
    insights.append("Warning: High equity near retirement increases risk")
if age < 35 and debt > 50:
    insights.append("Tip: Young investor can take more equity exposure")
if goal == "Retirement" and horizon > 15 and equity < 50:
    insights.append("Tip: Long horizon - consider more equity for compounding")
if goal == "Child Education" and horizon < 8 and equity > 60:
    insights.append("Warning: Education goal approaching - reduce equity to protect corpus")
if goal == "Wealth Creation" and risk == "Low":
    insights.append("Tip: Wealth creation with low risk may not beat inflation")
if not insights:
    insights.append("Portfolio looks well-balanced based on all inputs")
for i in insights:
    st.write(f"- {i}")

st.write("### AI Insights - Powered by Groq + Llama 3")
if st.button("Generate AI Insights"):
    with st.spinner("Llama 3 is analyzing your portfolio..."):
        try:
            res = requests.post(
                f"{BACKEND_URL}/portfolio/insights",
                json={"age": age, "risk": risk, "goal": goal, "horizon": horizon, "equity": equity, "debt": debt, "gold": gold}
            )
            if res.status_code == 200:
                st.success("Analysis complete!")
                st.markdown(res.json()["insights"])
            else:
                st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

st.write("### Suggested Actions")
recommendations = []
if risk == "Low":
    recommendations.append("Increase debt allocation for stability")
if risk == "High":
    recommendations.append("Increase equity exposure for growth")
if horizon > 10:
    recommendations.append("Consider long-term equity mutual funds or index funds")
if goal == "Retirement":
    recommendations.append(f"With {horizon} years to retirement, review allocation every 2-3 years")
if goal == "Child Education":
    recommendations.append("Use goal-based investment planning aligned to education year")
if age > 50:
    recommendations.append("Start gradually shifting to debt-heavy allocation as retirement nears")
if not recommendations:
    recommendations.append("Maintain current allocation - no changes needed")
for r in recommendations:
    st.write(f"- {r}")

st.write("---")
st.caption("Built by Prem | AI Wealth Management Copilot | Powered by Groq + Llama 3")
