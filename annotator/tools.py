import json
import os
from typing import Any

from smolagents import tool

from annotator.constants import DATA_DIR_PATH
from annotator.models import call_llm


@tool
def span_critique(span: str) -> str:
    """
    Critique a single span in agent execution traces.
    
    Args:
        span (str): The span to critique.
        
    Returns:
       str: The critique of the span.
    """


    # Call the LLM to critique the span
    response = call_llm(f"Critique the following span: {span}")
    return response

@tool
def load_trace(trace_id: str) -> Any:
    """
    Load a trace from a JSON file in the data/ directory.

    Args:
        trace_id (str): The ID of the trace to load.

    Returns:
        Any: The trace data, which is a list of dicts, each representing a span in the
            trace from Logfire.
    """
    with open(os.path.join(DATA_DIR_PATH, f"{trace_id}.json"), "r") as f:
        return json.load(f)

@tool
def load_span(trace_id: str, span_id: str) -> Any:
    """
    Load a span from a JSON file in the data/ directory.

    Args:
        trace_id (str): The ID of the trace to load.
        span_id (str): The ID of the span to load.

    Returns:
        Any: The span data, which is a dict pulled from Logfire.
    """
    with open(os.path.join(DATA_DIR_PATH, f"{trace_id}.json"), "r") as f:
        trace = json.load(f)
    for span in trace:
        span_id = span.get("span_id")
        if span_id == span_id:
            return span
    raise ValueError(f"Span {span_id} not found in trace {trace_id}")
