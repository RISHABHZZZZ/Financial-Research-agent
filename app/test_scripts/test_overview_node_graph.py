# app/test_overview_node_graph.py

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, add_messages
from nodes.get_company_overview import get_company_overview
from app.logging_config import setup_logger

logger = setup_logger(__name__)

# Define minimal state
class State(TypedDict):
    company_name: str
    company_overview: str

def main():
    logger.info("Building LangGraph with get_company_overview node...")

    # Initialize the graph builder
    graph_builder = StateGraph(State)

    # Add the node
    graph_builder.add_node("get_overview", get_company_overview)

    # Set entry point
    graph_builder.set_entry_point("get_overview")

    # End the graph after this node
    graph_builder.add_edge("get_overview", END)

    # Compile the graph
    graph = graph_builder.compile()

    logger.info("LangGraph compiled successfully.")

    # Prepare input state
    initial_state = {
        "company_name": "Apple Inc."
    }

    # Run the graph
    logger.info("Running the graph with initial state...")
    result = graph.invoke(initial_state)

    logger.info("Graph execution completed.")
    print("\n=== FINAL STATE ===")
    print(result)

if __name__ == "__main__":
    main()
