from smolagents import CodeAgent

from annotator.logfire_agent.agent import trace_downloader
from annotator.models import _model
from annotator.tools import load_span, load_trace

trace_annotator = CodeAgent(
    model=_model,
    tools=[
        load_trace,
        load_span,
        # load_trace,
        # summarize,
        # critique,
    ],
    verbosity_level=1,
    stream_outputs=True,
    additional_authorized_imports=["json"],
    name="trace_annotator",
    description="""This agent loads a trace from a JSON file, uses tools to summarize and critique a trace.
    It does so by first breaking the trace into spans (each with their own conversation history).
    For each span, get a summary & critique of that span.
    Then, get a summary of all the summaries & all the critiques.
    Return this summary and critique of the whole trace.
    """,
)

orchestrator = CodeAgent(
    model=_model,
    tools=[],
    managed_agents=[trace_downloader, trace_annotator],
    stream_outputs=True,
    verbosity_level=1,
    name="orchestrator",
    description="This agent analyzes and annotates agent execution traces."
)
