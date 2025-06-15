from smolagents import ToolCallingAgent, CodeAgent
from annotator.models import _model
from annotator.tools import span_critique

span_critic = ToolCallingAgent(
    model=_model,
    tools=[
        span_critique
    ],
    verbosity_level=1,
    max_tool_threads=10,
    name="span_critic",
    description="This agent critiques individual spans in parallel in an agent execution trace."
)

orchestrator = CodeAgent(
    model=_model,
    tools = [],
    managed_agents = [
        span_critic
    ],
    stream_outputs=True,
    verbosity_level=1,
    planning_interval=1,
    name="trace_annotator",
    description="This agent analyzes and annotates agent execution traces."
)