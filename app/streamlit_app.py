# app/streamlit_app.py

import os
import streamlit as st
from graph import build_langgraph
from logging_config import setup_logger
from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv()
# Setup logger
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

# Confirm OLLAMA API
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
if not OLLAMA_API_URL:
    st.error("❌ OLLAMA_API_URL is not set in your .env file.")
    st.stop()

# Build the LangGraph pipeline once
pipeline = build_langgraph()

# Streamlit page configuration
st.set_page_config(
    page_title="Company Research Assistant",
    layout="wide",
)

st.title("📈 Company Research Assistant")
st.markdown(
    """
Enter the company name below and click **Generate Report**.
The system will automatically look up the ticker symbol if you don't provide one.
"""
)

# Input form
with st.form("input_form"):
    company_name = st.text_input("Company Name", placeholder="Infosys Limited")
    ticker = st.text_input("Ticker Symbol (optional)", placeholder="INFY (leave blank to auto-detect)")
    region = st.selectbox("Region", options=["IN", "US"], index=0)
    submitted = st.form_submit_button("Generate Report")

if submitted:
    if not company_name.strip():
        st.warning("⚠️ Please enter a company name.")
        st.stop()

    st.info(f"Generating report for **{company_name}**...")
    with st.spinner("Running analysis..."):
        # Prepare initial state
        state = {
            "company_name": company_name.strip(),
            "region": region
        }
        if ticker.strip():
            state["ticker"] = ticker.strip()

        # Run LangGraph pipeline
        try:
            final_output = pipeline.invoke(state)
        except Exception as e:
            logger.exception("Pipeline execution failed.")
            st.error("❌ An unexpected error occurred while generating the report.")
            st.stop()

        report_md = final_output.get("final_report")

    if report_md:
        st.success("✅ Report generated successfully!")

        # Display report
        st.markdown(report_md, unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="📥 Download Markdown Report",
            data=report_md.encode("utf-8"),
            file_name=f"{company_name.replace(' ', '_')}_report.md",
            mime="text/markdown",
        )
    else:
        st.error("❌ No report was generated. Please review logs for details.")
        st.subheader("Debug Output")
        st.json(final_output)
