from smolagents import CodeAgent

from annotator.logfire_agent._logfire_mcp import (
    arbitrary_query,
    get_logfire_records_schema,
)
from annotator.logfire_agent.tools import save_trace_data
from annotator.models import _model

trace_downloader = CodeAgent(
    model=_model,
    tools=[
        # ---
        # See _logfire_mcp.py -- this is essentially a MCP server for Logfire.
        get_logfire_records_schema,
        arbitrary_query,
        # ---
        save_trace_data,
    ],
    stream_outputs=True,
    additional_authorized_imports=["json"],
    verbosity_level=1,
    name="trace_downloader",
    description="""\
This agent is responsible for downloading trace data from Logfire and saving it to a JSON
file, which can then be used by the trace_annotator agent.
"""
)
