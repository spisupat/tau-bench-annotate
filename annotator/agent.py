from smolagents import CodeAgent

from annotator._logfire_mcp import (  # See _logfire_mcp.py for why we import these directly.
    arbitrary_query,
    get_logfire_records_schema,
)
from annotator.models import _model
from annotator.tools import (
    load_span,
    load_trace,
    save_trace_data,
    span_critique,
    summarize_critiques,
)

agent = CodeAgent(
    model=_model,
    tools=[
        arbitrary_query,
        get_logfire_records_schema,
        load_trace,
        load_span,
        save_trace_data,
        summarize_critiques,
        span_critique,
    ],
    stream_outputs=True,
    additional_authorized_imports=["json"],
    verbosity_level=1,
    planning_interval=12,
    name="agent",
    description="This agent analyzes and annotates agent execution traces.",
)

agent.prompt_templates["system_prompt"] = (
    agent.prompt_templates["system_prompt"]
    + """
    You are an expert in annotating and evaluating agent execution traces.
    The user will provide you with a trace ID or a verbose description of a trace query they want to run.
    You will then use the get_logfire_records_schema, arbitrary_query, and save_trace_data tools to download the trace data and store it in a file.
    You will then use the load_trace tool and load_span tools to iterate through spans fro the trace data.
    You will then use span_critique to critique each span, and then use summarize_critiques to summarize the critiques.
    You will then return a trace analysis report to the user with the given format.

    Format:
        # Trace analysis report
        ## Critique summary
        ## Critique-annotated conversation flow (concise)

    We DO NOT care about the trace metadata, the business impact of this agent run. We also
    do not care about metrics such as duration, number of tokens, etc. We ONLY care about
    the critique of the trace to pin point exactly what went wrong.

    You should only perform the actions that each of the tools allows you to do within each step. For example, do not attempt
    to evaluate or annotate the traces in step 1, or re-download the trace data in step 2.

    You should NOT truncate any of the trace data at all. You should use the entire trace data
    to critique the trace.

    You should take the following steps to evaluate and annotate the trace.
    1. Download the trace data from logfire using the get_logfire_records_schema, arbitrary_query tools.
        1.1 The result of this agent should be a JSON file containing the trace data, save this file using the save_trace_data tool.
    2. Annotate the trace data using the trace_annotator agent.
        2.1 The JSON data should first be loaded from the file we have just created in step 1 using the load_trace tool.
        2.2 The load_trace tool should be used to figure out what the available spans are, and then the load_span tool should be used to iterate through spans, which should be formatted for the span_critique tool.
        2.3 The span_critique tool should be used to critique each span.
        2.4 The list of critiques from all the spans should be summarized using the summarize_critiques tool.
    3. Compile your findings from the above into a trace analysis report - where the Critique summary contains a high level overview, 
    and the Critique-annotated conversation flow contains a concise walkthrough with key spans flagged.
    """
)
