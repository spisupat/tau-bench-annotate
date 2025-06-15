
from smolagents import CodeAgent, LiteLLMModel

from annotate_agent.logfire_tools import (
    arbitrary_query_tool,
    get_logfire_records_schema_tool,
)

agent = CodeAgent(
    model=LiteLLMModel(model_id="anthropic/claude-3-7-sonnet-20250219"),
    tools=[
        arbitrary_query_tool,
        get_logfire_records_schema_tool,
    ],
    verbosity_level=1,
    planning_interval=3,
    stream_outputs=True,
    name="trace_annotator",
    description="This agent analyzes and annotates agent execution traces.",
)
