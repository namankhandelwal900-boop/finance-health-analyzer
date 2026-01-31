import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Health Analyzer", layout="wide")

st.title("📊 Smart Financial Health & Risk Analyzer")

uploaded_file = st.file_uploader("Upload Financial Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("📁 Financial Data")
    st.dataframe(df)

    st.subheader("📈 Key Financial Ratios")

    df["Current Ratio"] = df["Current_Assets"] / df["Current_Liabilities"]
    df["Debt Ratio"] = df["Total_Liabilities"] / df["Total_Assets"]
    df["Profit Margin"] = df["Net_Profit"] / df["Revenue"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Avg Current Ratio", round(df["Current Ratio"].mean(),2))
    col2.metric("Avg Debt Ratio", round(df["Debt Ratio"].mean(),2))
    col3.metric("Avg Profit Margin", round(df["Profit Margin"].mean(),2))

    st.subheader("📊 Trends")

    fig1 = px.line(df, x="Year", y="Current Ratio", title="Liquidity Trend")
    fig2 = px.line(df, x="Year", y="Debt Ratio", title="Leverage Trend")
    fig3 = px.line(df, x="Year", y="Profit Margin", title="Profitability Trend")

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("⚠️ Risk Assessment")

    risk_score = 0

    if df["Current Ratio"].mean() < 1.5:
        risk_score += 1
    if df["Debt Ratio"].mean() > 0.6:
        risk_score += 1
    if df["Profit Margin"].mean() < 0.1:
        risk_score += 1

    if risk_score == 0:
        st.success("Low Risk Company ✅")
    elif risk_score == 1:
        st.warning("Moderate Risk ⚠️")
    else:
        st.error("High Risk ⚠️❌")
