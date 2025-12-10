# frontend.py
from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime

# ---- Import Your Agents ----
from agents.data_loader import DataLoaderAgent
from agents.store_aggregation import StoreAggregationAgent
from agents.trend_detector import TrendDetectorAgent
from agents.demand_insight import DemandInsightAgent
from agents.report_generator import ReportGeneratorAgent


# ---- Streamlit Page Config ----
st.set_page_config(
    page_title="Pharmacy Demand Signal System",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Pharmacy Demand Signal Agentic System")
st.markdown(
    """
Upload your **store-wise daily sales CSV** and generate a **Daily Demand Summary Report**  
using a fully **rule-based multi-agent pipeline**.

**Pipeline:**
Data Loader → Store Aggregation → Trend Detection → Demand Insight → Report Generator
"""
)

# ---- File Upload ----
uploaded_file = st.file_uploader(
    "Upload Store-Wise Sales CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# ---- Save Uploaded File Temporarily ----
temp_path = f"/tmp/{uploaded_file.name}"
with open(temp_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

# ---- Run Agentic Pipeline Button ----
if st.button("🚀 Run Demand Signal Agents"):

    with st.spinner("Running agentic pipeline..."):

        # 1️⃣ Data Loader Agent
        loader = DataLoaderAgent(temp_path)
        df, issues = loader.load_and_validate()

        if issues:
            st.warning("⚠️ Data Validation Issues:")
            for issue in issues:
                st.write(f"- **{issue.level.upper()}**: {issue.message}")

        st.success("✅ Data Loaded Successfully")
        st.write("Preview of uploaded data:")
        st.dataframe(df.head(20), use_container_width=True)

        # 2️⃣ Store Aggregation Agent
        aggregation_agent = StoreAggregationAgent()
        aggregated_df, agg_summary = aggregation_agent.aggregate(df)

        st.success("✅ Store Aggregation Completed")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Stores", agg_summary.num_stores)
        col2.metric("Products", agg_summary.num_products)
        col3.metric("Days", agg_summary.num_days)
        col4.metric("Input Rows", agg_summary.total_rows_input)
        col5.metric("Output Rows", agg_summary.total_rows_output)

        # Rename column for compatibility with TrendDetectorAgent
        aggregated_df = aggregated_df.rename(
            columns={"total_quantity_sold": "quantity_sold"}
        )

        # 3️⃣ Trend Detector Agent
        trend_agent = TrendDetectorAgent()
        trends = trend_agent.detect_trends(aggregated_df)

        st.success("✅ Trend Detection Completed")

        # 4️⃣ Demand Insight Agent
        insight_agent = DemandInsightAgent()
        signals = insight_agent.generate_signals(trends)

        st.success("✅ Demand Insights Generated")

        # 5️⃣ Report Generator Agent
        report_agent = ReportGeneratorAgent(report_date=datetime.today())
        report_text = report_agent.generate_text_report(signals)

        st.success("✅ Daily Demand Summary Report Generated")

    # ---- Display Report ----
    st.subheader("📄 Daily Demand Summary Report")
    st.text_area(
        label="Generated Report",
        value=report_text,
        height=500
    )

    # ---- Download Button ----
    report_filename = f"demand_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    st.download_button(
        label="⬇️ Download Report",
        data=report_text,
        file_name=report_filename,
        mime="text/plain"
    )

