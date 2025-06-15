from smolagents import CodeAgent

from annotator._logfire_mcp import (
    arbitrary_query,
    get_logfire_records_schema,
)
from annotator.models import _model
from annotator.tools import load_span, load_trace, save_trace_data

agent = CodeAgent(
    model=_model,
    tools=[
        load_trace,
        load_span,
        save_trace_data,
        arbitrary_query,
        get_logfire_records_schema,
    ],
    stream_outputs=True,
    additional_authorized_imports=["json"],
    verbosity_level=1,
    planning_interval=12,
    name="agent",
    description="This agent analyzes and annotates agent execution traces."
)

agent.prompt_templates["system_prompt"] = (
    agent.prompt_templates["system_prompt"]
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
