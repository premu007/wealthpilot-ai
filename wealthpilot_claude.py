import streamlit as st
import plotly.graph_objects as go
import os
import anthropic                          # CHANGED: was "from openai import OpenAI"

# ------------------- CONFIG -------------------
st.set_page_config(page_title="WealthPilot AI", layout="wide")

# ------------------- CLAUDE SETUP -------------------
# CHANGED: was OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# The anthropic client auto-reads ANTHROPIC_API_KEY from environment — no need to pass it manually
client = anthropic.Anthropic()

def generate_ai_insights(age, risk, goal, horizon, equity, debt, gold):
    prompt = f"""
You are a professional wealth advisor.

Analyze the following client portfolio:

Age: {age}
Risk Appetite: {risk}
Goal: {goal}
Investment Horizon: {horizon} years

Allocation:
- Equity: {equity}%
- Debt: {debt}%
- Gold: {gold}%

Provide:
1. Key risk observations
2. Portfolio strengths
3. Actionable recommendations

Keep it concise, professional, and structured in bullet points.
"""

    # CHANGED: was client.chat.completions.create(model="gpt-4o-mini", ...)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",   # fast + cheap (equivalent to gpt-4o-mini)
        max_tokens=1024,                      # CHANGED: required in Claude API, didn't exist in OpenAI call
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # CHANGED: was response.choices[0].message.content
    return response.content[0].text


# ------------------- HEADER -------------------
st.title("💼 WealthPilot AI")
st.subheader("GenAI Copilot for Wealth Advisors — Powered by Claude")  # CHANGED: updated branding

# ------------------- SIDEBAR -------------------
st.sidebar.header("Client Profile")

age     = st.sidebar.slider("Client Age", 25, 70, 40)
risk    = st.sidebar.selectbox("Risk Appetite", ["Low", "Moderate", "High"])
goal    = st.sidebar.selectbox("Investment Goal", ["Retirement", "Wealth Creation", "Child Education"])
horizon = st.sidebar.slider("Investment Horizon (Years)", 1, 30, 10)

st.sidebar.markdown("---")
st.sidebar.markdown("**Allocation (Auto-normalized to 100%)**")

raw_equity = st.sidebar.slider("Equity (%)", 0, 100, 60)
raw_debt   = st.sidebar.slider("Debt (%)",   0, 100, 30)
raw_gold   = st.sidebar.slider("Gold (%)",   0, 100, 10)

raw_total = raw_equity + raw_debt + raw_gold

if raw_total == 0:
    equity, debt, gold = 33, 33, 34
else:
    equity = round((raw_equity / raw_total) * 100)
    debt   = round((raw_debt   / raw_total) * 100)
    gold   = 100 - equity - debt

st.sidebar.info(
    f"Raw: {raw_equity}/{raw_debt}/{raw_gold} = {raw_total}\n"
    f"Normalized: {equity}/{debt}/{gold}"
)

# ------------------- PORTFOLIO SUMMARY -------------------
st.write("### 📊 Portfolio Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Equity", f"{equity}%")
col2.metric("Debt",   f"{debt}%")
col3.metric("Gold",   f"{gold}%")
col4.metric("Total",  f"{equity + debt + gold}%",
            delta="Valid ✅" if (equity + debt + gold) == 100 else "Invalid ❌")

# ------------------- PIE CHART -------------------
fig = go.Figure(data=[go.Pie(
    labels=["Equity", "Debt", "Gold"],
    values=[equity, debt, gold],
    hole=0.45,
    marker_colors=["#4F8EF7", "#F7C948", "#6FCF97"],
    textinfo="label+percent",
    hovertemplate="%{label}: %{value}%<extra></extra>"
)])
fig.update_layout(
    height=300,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig, use_container_width=True)

# ------------------- RULE-BASED INSIGHTS -------------------
st.write("### 🔍 Rule-Based Insights")

insights = []

if equity > 70 and risk != "High":
    insights.append("⚠️ High equity exposure for your risk profile")
if debt < 20:
    insights.append("⚠️ Low debt allocation increases volatility")
if gold > 15:
    insights.append("⚠️ High gold allocation may limit growth")
if horizon < 5 and equity > 60:
    insights.append("⚠️ Short horizon with high equity is risky")
if age > 55 and equity > 50:
    insights.append("⚠️ High equity near retirement increases risk")
if age < 35 and debt > 50:
    insights.append("💡 Young investor can take more equity exposure")
if goal == "Retirement" and horizon > 15 and equity < 50:
    insights.append("💡 Long horizon — consider more equity for compounding")
if goal == "Child Education" and horizon < 8 and equity > 60:
    insights.append("⚠️ Education goal approaching — reduce equity to protect corpus")
if goal == "Wealth Creation" and risk == "Low":
    insights.append("💡 Wealth creation with low risk may not beat inflation")

if not insights:
    insights.append("✅ Portfolio looks well-balanced based on all inputs")

for i in insights:
    st.write(f"• {i}")

# ------------------- AI INSIGHTS (Claude) -------------------
st.write("### 🤖 AI Insights — Powered by Claude")   # CHANGED: was "OpenAI"

if st.button("✨ Generate AI Insights"):
    with st.spinner("Claude is analyzing your portfolio..."):   # CHANGED: updated spinner text
        try:
            ai_output = generate_ai_insights(age, risk, goal, horizon, equity, debt, gold)
            st.success("Analysis complete!")
            st.markdown(ai_output)
        except anthropic.AuthenticationError:                   # CHANGED: specific Claude error
            st.error("❌ Invalid API key. Check your ANTHROPIC_API_KEY environment variable.")
        except anthropic.RateLimitError:                        # CHANGED: specific Claude error
            st.error("❌ Rate limit hit. Wait a moment and try again.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# ------------------- RECOMMENDATIONS -------------------
st.write("### 💡 Suggested Actions")

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
    recommendations.append("✅ Maintain current allocation — no changes needed")

for r in recommendations:
    st.write(f"• {r}")

# ------------------- FOOTER -------------------
st.write("---")
st.caption("Built by Prem | AI Wealth Management Copilot | Powered by Anthropic Claude")  # CHANGED
