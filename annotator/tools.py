import json
import os
from typing import Any

from smolagents import tool

from annotator.constants import DATA_DIR_PATH
from annotator.models import call_llm


@tool
def span_critique(span: str) -> str:
    """
    Critique a single span in agent execution traces.

    Args:
        span (str): The span to critique.

    Returns:
       str: The critique of the span.
    """

    # Call the LLM to critique the span
    response = call_llm(f"Critique the following span: {span}")
    return response


@tool
def load_trace(trace_id: str) -> Any:
    """
    Load a trace from a JSON file in the data/ directory.

    Args:
        trace_id (str): The ID of the trace to load.

    Returns:
        Any: The trace data, which is a list of dicts, each representing a span in the
            trace from Logfire.
    """
    with open(os.path.join(DATA_DIR_PATH, f"{trace_id}.json"), "r") as f:
        return json.load(f)


@tool
def load_span(trace_id: str, span_id: str) -> Any:
    """
    Load a span from a JSON file in the data/ directory.

    Args:
        trace_id (str): The ID of the trace to load.
        span_id (str): The ID of the span to load.

    Returns:
        Any: The span data, which is a dict pulled from Logfire.
    """
    with open(os.path.join(DATA_DIR_PATH, f"{trace_id}.json"), "r") as f:
        trace = json.load(f)
    for span in trace:
        span_id = span.get("span_id")
        if span_id == span_id:
            return span
    raise ValueError(f"Span {span_id} not found in trace {trace_id}")


@tool
def summarize(trace: Any) -> str:
    """
    Summarize a trace.

    Args:
        trace (Any): The trace to summarize.

    Returns:
        str: The summary of the trace.
    """
    prompt = f"""
You are an expert at analyzing and summarizing agent execution traces. You will be given a
flattened output of OpenTelemetry (OTEL) trace and span events that were observed during
an agent's run.

Your task is to extract the essential information and present it in a clear, structured
format that helps understand what the agent did and why.

## Required Output Structure

### 1. Agent Task
**What was the user trying to achieve?**
- State the user's original request or goal in 1-2 clear sentences
- Include any specific constraints or requirements mentioned
- Note if the task evolved or was clarified during execution

### 2. Agent Approach
**How did the agent try to solve it?**

Provide a chronological list of major steps, focusing on:
- Tools or functions called and their purpose
- Key decision points and why certain paths were chosen
- Any retries, fallbacks, or error recovery attempts
- Data transformations or processing steps
- External API calls or resource access

Format as bullet points, with each point being a complete, self-contained explanation.
Group related sub-steps under main bullets when appropriate.

### 3. Agent Output
**What was the final result?**
- Describe the actual output or outcome delivered to the user
- Note if the task was fully completed, partially completed, or failed
- Include any caveats, limitations, or follow-up actions recommended
- Mention performance metrics if relevant (e.g., "processed 1,000 records in 3.2 seconds")

## Additional Guidelines
1. **Clarity over Completeness**: Focus on the logical flow rather than every technical
detail. Skip low-level implementation details unless they're crucial to understanding
the outcome.
2. **Error Handling**: If errors occurred, explain:
   - What went wrong
   - How the agent attempted to recover
   - Whether the recovery was successful
3. **Tool Usage Patterns**: When multiple tools are used:
   - Explain the coordination between tools
   - Highlight any interesting sequencing or parallel execution
   - Note if tools were used in unexpected ways
4. **Conciseness**: Keep the entire summary under 500 words unless the trace is
exceptionally complex.
5. **Technical Accuracy**: Use precise terminology for:
   - API/function names (preserve exact casing)
   - Error types and messages
   - Numerical results or metrics

## Example Patterns to Identify
- **Iterative Refinement**: Agent tries multiple approaches to improve results
- **Data Pipeline**: Sequential processing through multiple transformation steps
- **Fallback Strategies**: Primary approach fails, agent tries alternatives
- **Parallel Execution**: Multiple operations running concurrently
- **Validation Loops**: Agent checks its work and makes corrections

Remember: Your summary should enable someone who didn't observe the run to understand
exactly what happened and why, without needing to read the raw trace data.

Here is the trace:

{trace}
"""
    response = call_llm(prompt)
    return response
