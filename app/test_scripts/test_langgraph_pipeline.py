# app/test_langgraph_pipeline.py

from utils.load_environment import ensure_environment
ensure_environment()

from langgraph.graph import StateGraph, END
from nodes.get_company_overview import get_company_overview
from nodes.get_financials import get_financials
from nodes.get_market_position import get_market_position
from nodes.get_swot_analysis import get_swot_analysis
from nodes.get_latest_news import get_latest_news
from nodes.get_stock_info import get_stock_info
from nodes.generate_final_report import generate_final_report
from nodes.resolve_ticker import resolve_ticker
from logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Building LangGraph pipeline...")

    # Define your state
    from typing import TypedDict

    class ResearchState(TypedDict, total=False):
        company_name: str
        ticker: str
        company_overview: str
        financials: dict
        market_position: str
        swot_analysis: str
        latest_news: str
        stock_info: str
        final_report: str


    # Initialize StateGraph
    graph = StateGraph(ResearchState)

    # Add all nodes
    graph.add_node("overview", get_company_overview)
    graph.add_node("financials", get_financials)
    graph.add_node("market_position", get_market_position)
    graph.add_node("swot", get_swot_analysis)
    graph.add_node("news", get_latest_news)
    graph.add_node("stock", get_stock_info)
    graph.add_node("report", generate_final_report)
    graph.add_node("resolve_ticker", resolve_ticker)

    # Define the flow
    # graph.set_entry_point("overview")
    graph.set_entry_point("resolve_ticker")
    # connect resolve_ticker to overview
    graph.add_edge("resolve_ticker", "overview")

    graph.add_edge("overview", "financials")
    graph.add_edge("financials", "market_position")
    graph.add_edge("market_position", "swot")
    graph.add_edge("swot", "news")
    graph.add_edge("news", "stock")
    graph.add_edge("stock", "report")
    graph.add_edge("report", END)

    logger.info("Compiling LangGraph...")
    pipeline = graph.compile()

    # Initial input
    initial_state = ResearchState({
    "company_name": "Infosys Limited",
    # "ticker": "INFY",
    "region": "IN"
})
    
    

    logger.info("Running LangGraph pipeline...")
    result = pipeline.invoke(initial_state)

    logger.info("Pipeline execution complete.")
    print("\n=== FINAL REPORT ===\n")
    print(result["final_report"])

if __name__ == "__main__":
    main()
