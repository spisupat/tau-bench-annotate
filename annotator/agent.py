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
    summarize_trace,
)

agent = CodeAgent(
    model=_model,
    tools=[
        arbitrary_query,
        get_logfire_records_schema,
        load_trace,
        load_span,
        span_critique,
        save_trace_data,
        summarize_trace,
        summarize_critiques,
        span_critique
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
    You will then use the get_logfire_records_schema, arbitrary_query, and save_trace_data tools to download the trace data and store it in a file.
    You will then use the load_trace and summarize_trace tools to summarize the trace data.
    You will then use load_span and span_critique to critique each span, and then use summarize_critiques to summarize the critiques.
    You will then return a trace analysis report to the user with the given format.
    
    Format:
        # Trace analysis report
        ## Executive summary
        ## Critique-annotated conversation summary

    You should only perform the actions that each of the tools allows you to do within each step. For example, do not attempt
    to evaluate or annotate the traces in step 1, or re-download the trace data in step 2.

    You should take the following steps to evaluate and annotate the trace.
    1. Download the trace data from logfire using the get_logfire_records_schema, arbitrary_query tools.
        1.1 The result of this agent should be a JSON file containing the trace data, save this file using the save_trace_data tool.
    2. Annotate the trace data using the trace_annotator agent.
        2.1 The JSON data should first be loaded from the file we have just created in step 1 using the load_trace tool.
        2.2 The entire trace should be summarized using the summarize_trace tool.
        2.3 The trace should be broken down into spans and formatted for the span_critique tool.
        2.4 The list of critiques should be summarized using the summarize_critiques tool.
    3. Compile your findings from the above into a trace analysis report - where the executive summary contains 
        a high level overview, and the annotated conversation summary contains a walkthrough of the trace with key critiques flagged.
    """
)
