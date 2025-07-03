# app/graph.py

from langgraph.graph import StateGraph, END
from nodes.resolve_ticker import resolve_ticker
from nodes.get_company_overview import get_company_overview
from nodes.get_financials import get_financials
from nodes.get_market_position import get_market_position
from nodes.get_swot_analysis import get_swot_analysis
from nodes.get_latest_news import get_latest_news
from nodes.get_stock_info import get_stock_info
from nodes.generate_final_report import generate_final_report
from nodes.get_raw_data_from_multiple_sources import get_raw_data_from_multiple_sources
from nodes.compute_financial_ratios import compute_financial_ratios
from nodes.get_curated_research_data import get_curated_research_data
from nodes.get_structured_extracted_facts import get_structured_extracted_facts

def build_langgraph():
    """
    Builds the full multi-step LangGraph pipeline for company research.
    Returns a compiled runnable pipeline.
    """
    # If you prefer, you can define a TypedDict here for better type checking.
    # For example:
    #
    from typing import TypedDict
    #
    class ResearchState(TypedDict, total=False):
        company_name: str
        ticker: str
        region: str
        company_overview: str
        financials: dict
        market_position: str
        swot_analysis: str
        latest_news: str
        stock_info: str
        final_report: str
    #
    # Then:
    graph = StateGraph(ResearchState)

    # graph = StateGraph(dict)

    graph.add_node("resolve_ticker", resolve_ticker)
    graph.add_node("get_raw_data_from_multiple_sources", get_raw_data_from_multiple_sources)
    graph.add_node("get_financials", get_financials)
    graph.add_node("compute_financial_ratios", compute_financial_ratios)
    graph.add_node("get_latest_news", get_latest_news)
    graph.add_node("get_stock_info", get_stock_info)
    graph.add_node("generate_final_report", generate_final_report)
    graph.add_node("get_curated_research_data", get_curated_research_data)
    graph.add_node("get_structured_extracted_facts", get_structured_extracted_facts)

    # Define the flow
    graph.set_entry_point("resolve_ticker")
    graph.add_edge("resolve_ticker", "get_raw_data_from_multiple_sources")
    graph.add_edge("get_raw_data_from_multiple_sources", "get_curated_research_data")
    graph.add_edge("get_curated_research_data", "get_structured_extracted_facts")
    graph.add_edge("get_structured_extracted_facts", "get_financials")
    graph.add_edge("get_financials", "compute_financial_ratios")
    graph.add_edge("compute_financial_ratios", "get_latest_news")
    graph.add_edge("get_latest_news", "get_stock_info")
    graph.add_edge("get_stock_info", "generate_final_report")

    # Mark the end
    graph.set_finish_point("generate_final_report")

    # Compile pipeline
    return graph.compile()
