from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import black, lightgrey
import io
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== GLOBAL INIT =====
score_pdf = 0



st.set_page_config(page_title="Financial Health Analyzer", layout="wide")

st.title("📊 Smart Financial Health & Risk Analyzer")

st.subheader("📂 Upload Company Financials")

uploaded_file = st.file_uploader("Upload Company A File", type=["xlsx"])
uploaded_file_2 = st.file_uploader("Upload Company B File (Optional)", type=["xlsx"])

if uploaded_file:

        df = pd.read_excel(uploaded_file)

        # Show Data
        st.subheader("📁 Financial Data")
        st.dataframe(df)

        # Ratios
        df["Current Ratio"] = df["Current_Assets"] / df["Current_Liabilities"]
        df["Debt Ratio"] = df["Total_Liabilities"] / df["Total_Assets"]
        df["Profit Margin"] = df["Net_Profit"] / df["Revenue"]
        
           
        # Valuation (P/E Model)
        

        st.subheader("💰 Company Valuation (P/E Method)")

        market_pe = st.slider(
            "Select Industry P/E Multiple",
            min_value=5,
            max_value=40,
            value=15
        )
                # Calculate EPS (from Net Profit & Shares)
        shares_outstanding = st.number_input(
            "Enter Total Shares (in lakhs)",
            min_value=1,
            value=10
        ) * 1_00_000   # convert lakhs to actual shares

        avg_eps = df["Net_Profit"].mean() / shares_outstanding

        # Fair Value using P/E
        fair_value = avg_eps * market_pe

        # Store for blended valuation
        pe_value = fair_value

        st.metric("Average EPS", round(avg_eps, 2))
        st.metric("Fair Value per Share (P/E)", f"₹ {round(fair_value,2)}")

               
        # DCF VALUATION
        

        st.subheader("💰 Company Valuation (DCF Method)")

        # User Inputs
        growth_rate = st.slider("Expected Annual Growth Rate (%)", 0.0, 30.0, 10.0) / 100
        discount_rate = st.slider("Discount Rate / WACC (%)", 5.0, 25.0, 12.0) / 100
        terminal_growth = st.slider("Terminal Growth Rate (%)", 0.0, 8.0, 4.0) / 100

        projection_years = 5

        # Estimate Free Cash Flow (FCF)
        # Using Net Profit as proxy (simplified model)
        base_fcf = df["Net_Profit"].iloc[-1]

        st.write("Base Free Cash Flow (Latest Profit): ₹", round(base_fcf, 2))


        # Project Future Cash Flows
        fcf_list = []

        for i in range(1, projection_years + 1):
            fcf = base_fcf * (1 + growth_rate) ** i
            fcf_list.append(fcf)


        # Discount Cash Flows
        discounted_fcf = []

        for i in range(projection_years):
            pv = fcf_list[i] / ((1 + discount_rate) ** (i + 1))
            discounted_fcf.append(pv)


        # Terminal Value
        terminal_value = (
            fcf_list[-1] * (1 + terminal_growth)
        ) / (discount_rate - terminal_growth)

        pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)


        # Enterprise Value
        enterprise_value = sum(discounted_fcf) + pv_terminal


        # Shares Outstanding
        shares = st.number_input("Total Shares Outstanding (in lakhs)", min_value=1, value=10) * 100000


        # Intrinsic Value per Share
        dcf_value = enterprise_value / shares


        # Display Results
        st.metric("DCF Enterprise Value", f"₹ {round(enterprise_value,2)}")
        st.metric("DCF Fair Value / Share", f"₹ {round(dcf_value,2)}")


        # ============================
        # DCF Interpretation
        # ============================

        market_price = st.number_input("Enter Current Market Price (₹)", value=float(round(dcf_value,2)))

        upside = ((dcf_value - market_price) / market_price) * 100

        st.metric("DCF Upside / Downside (%)", f"{round(upside,2)}%")


        # Recommendation
        if upside > 20:
            dcf_rec = "🟢 STRONG BUY"
        elif upside > 10:
            dcf_rec = "🟡 BUY"
        elif upside > -10:
            dcf_rec = "🟠 HOLD"
        else:
            dcf_rec = "🔴 SELL"


        st.success(f"DCF Recommendation: {dcf_rec}")
        
                # ============================
        # Blended Target Price
        st.subheader("🎯 Analyst Target Price (Blended Valuation)")

        # Make sure these exist
        pe_value = fair_value  # <-- change if your name is different
        dcf_value_final = dcf_value        # your DCF output
        market_price_val = market_price   # current price input

        # Weights
        pe_weight = 0.4
        dcf_weight = 0.6

        # Blended Price
        target_price = (pe_value * pe_weight) + (dcf_value_final * dcf_weight)

        st.metric("Blended Target Price", f"₹ {round(target_price,2)}")


        # Expected Return
        final_upside = ((target_price - market_price_val) / market_price_val) * 100

        st.metric("Expected Return (%)", f"{round(final_upside,2)}%")


        # Final Call
        if final_upside > 20:
            final_rec = "🚀 STRONG BUY"
        elif final_upside > 10:
            final_rec = "📈 BUY"
        elif final_upside > -10:
            final_rec = "⚖️ HOLD"
        else:
            final_rec = "⚠️ SELL"

        st.success(f"Final Analyst Call: {final_rec}")



        # EPS = Net Profit / Shares (Assume shares if not available)
        if "Shares" in df.columns:
            avg_eps = (df["Net_Profit"] / df["Shares"]).mean()
        else:
            assumed_shares = st.number_input(
                "Enter Total Shares Outstanding (in lakhs)",
                min_value=1,
                value=10
            ) * 1_00_000

            avg_eps = df["Net_Profit"].mean() / assumed_shares


        fair_price = avg_eps * market_pe


        st.metric("Average EPS", round(avg_eps, 2))
        st.metric("Fair Value per Share", f"₹ {round(fair_price,2)}")
                # =========================
        # Investment Recommendation
        # =========================

        st.subheader("📈 Investment Recommendation")

        # Ask user for Market Price
        market_price = st.number_input(
            "Enter Current Market Price (₹)",
            min_value=0.0,
            value=float(round(fair_price, 2))
        )

        upside = ((fair_price - market_price) / market_price) * 100 if market_price > 0 else 0


        if upside > 20:
            decision = "🟢 BUY"
            reason = "Stock appears undervalued with strong upside potential."
        elif upside > -10:
            decision = "🟡 HOLD"
            reason = "Stock is fairly valued. Limited upside at current levels."
        else:
            decision = "🔴 SELL"
            reason = "Stock appears overvalued with downside risk."


        st.metric("Upside / Downside (%)", f"{round(upside,2)}%")
        st.success(f"Recommendation: {decision}")
        st.info(reason)



        col1, col2, col3 = st.columns(3)

        col1.metric("Avg Current Ratio", round(df["Current Ratio"].mean(),2))
        col2.metric("Avg Debt Ratio", round(df["Debt Ratio"].mean(),2))
        col3.metric("Avg Profit Margin", round(df["Profit Margin"].mean(),2))

        # Charts
        fig1 = px.line(df, x="Year", y="Current Ratio", title="Liquidity Trend")
        fig2 = px.line(df, x="Year", y="Debt Ratio", title="Leverage Trend")
        fig3 = px.line(df, x="Year", y="Profit Margin", title="Profitability Trend")

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

        # Health Score
        st.subheader("🏥 Financial Health & Analyst Report")

        avg_current = df["Current Ratio"].mean()
        avg_debt = df["Debt Ratio"].mean()
        avg_profit = df["Profit Margin"].mean()

        score = 100

        if avg_current < 1:
            score -= 25
        elif avg_current < 1.5:
            score -= 15

        if avg_debt > 0.7:
            score -= 25
        elif avg_debt > 0.5:
            score -= 15

        if avg_profit < 0.05:
            score -= 25
        elif avg_profit < 0.1:
            score -= 15

        if score >= 80:
            rating = "🟢 Excellent"
        elif score >= 60:
            rating = "🟡 Good"
        elif score >= 40:
            rating = "🟠 Risky"
        else:
            rating = "🔴 Critical"

        c1, c2 = st.columns(2)

        c1.metric("Health Score", f"{score}/100")
        c2.metric("Rating", rating)

        # Commentary
        st.subheader("📝 Analyst Commentary")

        comment = ""

        if avg_current >= 1.5:
            comment += "The company demonstrates strong liquidity position. "
        elif avg_current >= 1:
            comment += "The company maintains adequate short-term liquidity. "
        else:
            comment += "The company shows weak liquidity which may impact operations. "

        if avg_debt <= 0.4:
            comment += "Leverage levels are conservative, indicating low financial risk. "
        elif avg_debt <= 0.6:
            comment += "The company operates with moderate leverage. "
        else:
            comment += "High leverage levels indicate elevated financial risk. "

        if avg_profit >= 0.12:
            comment += "Profitability is strong and supports sustainable growth. "
        elif avg_profit >= 0.08:
            comment += "Profitability remains stable with moderate margins. "
        else:
            comment += "Low profit margins may impact long-term sustainability. "

        if score >= 80:
            comment += "Overall, the company reflects strong financial stability."
        elif score >= 60:
            comment += "Overall, the company shows satisfactory financial performance."
        elif score >= 40:
            comment += "Overall, financial performance requires improvement."
        else:
            comment += "Overall, the company faces significant financial stress."

        st.info(comment)
    # Peer Comparison
        if uploaded_file_2:

            st.subheader("📊 Peer Comparison (Company A vs Company B)")

            df2 = pd.read_excel(uploaded_file_2)

            # Ratios for Company B
            df2["Current Ratio"] = df2["Current_Assets"] / df2["Current_Liabilities"]
            df2["Debt Ratio"] = df2["Total_Liabilities"] / df2["Total_Assets"]
            df2["Profit Margin"] = df2["Net_Profit"] / df2["Revenue"]

            comp_data = {
                "Metric": ["Current Ratio", "Debt Ratio", "Profit Margin"],
                "Company A": [
                    round(df["Current Ratio"].mean(), 2),
                    round(df["Debt Ratio"].mean(), 2),
                    round(df["Profit Margin"].mean(), 2)
                ],
                "Company B": [
                    round(df2["Current Ratio"].mean(), 2),
                    round(df2["Debt Ratio"].mean(), 2),
                    round(df2["Profit Margin"].mean(), 2)
                ]
            }

            comp_df = pd.DataFrame(comp_data)

            st.dataframe(comp_df)

            fig_comp = px.bar(
                comp_df,
                x="Metric",
                y=["Company A", "Company B"],
                barmode="group",
                title="Peer Comparison"
            )

            st.plotly_chart(fig_comp, use_container_width=True)
            # Download Report (Excel)
            st.subheader("📥 Download Financial Report")

            report_data = {
            "Metric": ["Current Ratio", "Debt Ratio", "Profit Margin", "Health Score", "Rating"],
            "Value": [
                round(df["Current Ratio"].mean(),2),
                round(df["Debt Ratio"].mean(),2),
                round(df["Profit Margin"].mean(),2),
                score,
                rating
            ]
        }

            report_df = pd.DataFrame(report_data)

            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                report_df.to_excel(writer, index=False, sheet_name="Financial Report")

            buffer.seek(0)

            st.download_button(
            label="📄 Download Report (Excel)",
            data=buffer,
            file_name="financial_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
                        # ======================
            # PDF Score Init (GLOBAL)
            # ======================


            # Download Full Report (PDF)

            st.subheader("📥 Download Full Report (PDF)")

            # Recalculate for PDF
            avg_current = df["Current Ratio"].mean()
            avg_debt = df["Debt Ratio"].mean()
            avg_profit = df["Profit Margin"].mean()

            # Health Score
                        
        if avg_current >= 1.5:
            score_pdf += 30
        else:
            score_pdf += 15

        if avg_debt <= 0.5:
            score_pdf += 30
        else:
            score_pdf += 15

        if avg_profit >= 0.1:
            score_pdf += 40
        else:
            score_pdf += 20


        # Rating
        if score_pdf >= 80:
            rating_pdf = "Excellent"
        elif score_pdf >= 60:
            rating_pdf = "Good"
        elif score_pdf >= 40:
            rating_pdf = "Average"
        else:
            rating_pdf = "Poor"
            
            st.success(f"📈 Recommendation: {recommendation}")



        # Commentary
        if score_pdf >= 80:
            comment_pdf = "The company demonstrates strong financial stability and low risk."
        elif score_pdf >= 60:
            comment_pdf = "The company shows satisfactory financial performance."
        elif score_pdf >= 40:
            comment_pdf = "The company needs improvement in key financial areas."
        else:
            comment_pdf = "The company faces high financial risk."
                    
                    # Investment Recommendation
        if score_pdf >= 80:
            recommendation = "✅ Strong Buy"
        elif score_pdf >= 60:
            recommendation = "👍 Buy"
        elif score_pdf >= 40:
            recommendation = "⚠️ Hold"
        else:
            recommendation = "❌ Avoid"



        def generate_pdf(score, rating, comment, df, df2=None):

            buffer = io.BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()
            elements = []


            # Title
            elements.append(Paragraph("Financial Health Analysis Report", styles["Title"]))
            elements.append(Spacer(1, 20))


            # Summary
            elements.append(Paragraph("Executive Summary", styles["Heading2"]))
            elements.append(Spacer(1, 10))

            summary = f"""
            Health Score: {score}/100<br/>
            Rating: {rating}<br/>
            Recommendation: {recommendation}<br/><br/>
            """


            elements.append(Paragraph(summary, styles["Normal"]))
            elements.append(Spacer(1, 20))


            # Key Ratios
            elements.append(Paragraph("Key Financial Ratios", styles["Heading2"]))
            elements.append(Spacer(1, 10))

            ratio_data = [
                ["Metric", "Value"],
                ["Current Ratio", round(df["Current Ratio"].mean(), 2)],
                ["Debt Ratio", round(df["Debt Ratio"].mean(), 2)],
                ["Profit Margin", round(df["Profit Margin"].mean(), 2)]
            ]

            ratio_table = Table(ratio_data, colWidths=[200, 200])

            ratio_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER")
            ]))

            elements.append(ratio_table)
            elements.append(Spacer(1, 20))


            # Commentary
            elements.append(Paragraph("Analyst Commentary", styles["Heading2"]))
            elements.append(Spacer(1, 10))

            elements.append(Paragraph(comment, styles["Normal"]))
            elements.append(Spacer(1, 20))


            # Peer Comparison
            if df2 is not None:

                elements.append(Paragraph("Peer Comparison", styles["Heading2"]))
                elements.append(Spacer(1, 10))

                peer_data = [
                    ["Metric", "Company A", "Company B"],

                    ["Current Ratio",
                    round(df["Current Ratio"].mean(), 2),
                    round(df2["Current Ratio"].mean(), 2)],

                    ["Debt Ratio",
                    round(df["Debt Ratio"].mean(), 2),
                    round(df2["Debt Ratio"].mean(), 2)],

                    ["Profit Margin",
                    round(df["Profit Margin"].mean(), 2),
                    round(df2["Profit Margin"].mean(), 2)]
                ]

                peer_table = Table(peer_data, colWidths=[150, 150, 150])

                peer_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER")
                ]))

                elements.append(peer_table)
                elements.append(Spacer(1, 20))


            # Conclusion
            elements.append(Paragraph("Conclusion", styles["Heading2"]))
            elements.append(Spacer(1, 10))

            conclusion = "This report summarizes the company’s financial health, risk profile, and comparative position."

            elements.append(Paragraph(conclusion, styles["Normal"]))

            doc.build(elements)

            buffer.seek(0)

            return buffer


        # Generate PDF Safely
        if uploaded_file_2:
            pdf_buffer = generate_pdf(score_pdf, rating_pdf, comment_pdf, df, df2)
        else:
             pdf_buffer = generate_pdf(score_pdf, rating_pdf, comment_pdf, df)


        st.download_button(
            label="📄 Download Full Report (PDF)",
            data=pdf_buffer,
            file_name="financial_analysis_report.pdf",
            mime="application/pdf"
        )
        
