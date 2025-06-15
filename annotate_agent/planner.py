import os

from mcp import StdioServerParameters
from smolagents import LiteLLMModel, ToolCallingAgent, ToolCollection

server_parameters = StdioServerParameters(
    command="uvx",
    args=["--quiet", "logfire-mcp"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection: # noqa: E501
    agent = ToolCallingAgent(
        model=LiteLLMModel(model_id="anthropic/claude-3-7-sonnet-20250219"),
        tools=tool_collection.tools,
        verbosity_level=1,
        planning_interval=3,
        name="trace_annotator",
        description="This agent analyzes and annotates agent execution traces.",
    )
