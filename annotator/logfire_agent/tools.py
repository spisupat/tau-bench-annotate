
import json
import os
from typing import Any

from logfire.experimental.query_client import LogfireQueryClient
from smolagents import tool

from annotator.constants import DATA_DIR_PATH

logfire_client = LogfireQueryClient(
    os.getenv("LOGFIRE_READ_TOKEN"),
    os.getenv("LOGFIRE_BASE_URL"),
)

@tool
def save_trace_data(trace_id: str, trace_data: list[dict[str, Any]]) -> str:
    """Save trace data to a JSON file in the data/ directory.

    The trace data is saved to a JSON file in the data/ directory with path:
    `data/<trace_id>.json`.

    Trace data can be obtained via the `arbitrary_query` tool.

    Args:
        trace_id: The trace ID to save the data for.
        trace_data: The trace data to save.

    Returns:
        The path to the file where the trace data is saved.
    """
    os.makedirs(os.path.join(DATA_DIR_PATH), exist_ok=True)
    file_path = os.path.join(DATA_DIR_PATH, f"{trace_id}.json")
    with open(file_path, "w") as f:
        json.dump(trace_data, f)
    return file_path
