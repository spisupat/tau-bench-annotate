from smolagents import CodeAgent

from annotator.logfire_agent.agent import trace_downloader
from annotator.models import _model
from annotator.tools import load_span, load_trace, summarize_trace

trace_annotator = CodeAgent(
    model=_model,
    tools=[
        load_trace,
        load_span,
        summarize_trace,
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
    description="This agent analyzes and annotates agent execution traces.",
)

orchestrator.prompt_templates["system_prompt"] = (
    orchestrator.prompt_templates["system_prompt"]
    + """
    You are an expert in annotating and evaluating agent execution traces.
    The user will provide you with a trace ID or a verbose description of a trace query they want to run.
    You will then use the trace_downloader agent to download the trace data and store it in a file.
    You will then use the trace_annotator agent to annotate the trace data.
    You will then return a summary and critique of the trace to the user.

    You should only perform the actions that each of the tools allows you to do. For example,
    do not start to evaluate or annotate the traces outside of the trace annotator tool and vice versa.

    You should take the following steps to evaluate and annotate the trace.
    1. Download the trace data from logfire using the trace_downloader agent.
        1.1 The result of this agent should be a pickle file containing the trace data.
    2. Annotate the trace data using the trace_annotator agent.
        2.1 The pickle file should first be loaded from the file we have just created in step 1.
        2.2 The entire trace should be broken down into spans, and each span summarized and critiqued.
        2.3 Finally, span level summaries and critiques should be summarized into trace level summaries and critiques
    3. Return the final summary and critique to the user.
    """
)
