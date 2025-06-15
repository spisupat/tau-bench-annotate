from smolagents import CodeAgent, ToolCallingAgent

from annotator.logfire_tools import arbitrary_query, get_logfire_records_schema
from annotator.models import _model
from annotator.tools import span_critique

trace_downloader = CodeAgent(
    model=_model,
    tools=[
        get_logfire_records_schema,
        arbitrary_query,
        # save trace
    ],
    stream_outputs=True,
    verbosity_level=1,
    name="trace_downloader",
    description="This agent queries logfire for a trace with a given traceID, and saves it to a JSON file."

)


trace_annotator = CodeAgent(
    model=_model,
    tools=[
        # load_trace,
        # summarize,
        # critique,
    ],
    verbosity_level=1,
    stream_outputs=True,
    name="trace_annotator",
    description="""This agent loads a trace from a JSON file, uses tools to summarize and critique a trace.
    It does so by first breaking the trace into spans (each with their own conversation history).
    For each span, get a summary & critique of that span.
    Then, get a summary of all the summaries & all the critiques.
    Return this summary and critique of the whole trace.
    """
)

orchestrator = CodeAgent(
    model=_model,
    managed_agents = [
        trace_downloader,
        trace_annotator
    ],
    stream_outputs=True,
    verbosity_level=1,
    planning_interval=12,
    name="trace_annotator",
    description="This agent analyzes and annotates agent execution traces."
)


