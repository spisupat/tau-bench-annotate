import json
import os
from typing import Any

from smolagents import tool

from annotator.constants import DATA_DIR_PATH
from annotator.models import call_llm
import json
from typing import Any
from ast import literal_eval
from jinja2 import Template


@tool
def save_trace_data(trace_id: str, trace_data: list[dict[str, Any]]) -> str:
    """Save trace data to a JSON file in the data/ directory.

    The trace data is saved to a JSON file in the data/ directory with path:
    `data/<trace_id>.json`.

    Trace data can be obtained via the `arbitrary_query` tool.

    Args:
        trace_id: The trace ID to save the data for.
        trace_data: The trace data to save.

    Returns:
        The path to the file where the trace data is saved.
    """
    os.makedirs(os.path.join(DATA_DIR_PATH), exist_ok=True)
    file_path = os.path.join(DATA_DIR_PATH, f"{trace_id}.json")
    with open(file_path, "w") as f:
        json.dump(trace_data, f)
    return file_path


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


SPAN_CRITIQUE_PROMPT_TEMPLATE = """\
You are a helpful assistant that critiques the response of an agent. You will receive a list of interactions between the agent, the user, and the tools called by the agent.

Rules of the critique:
- English only.
- Be specific, referring to specific parts of the conversation history and the agent's response.
- Be as concise as possible.
- Do not output any other text than the critique.

## Conversation history:
{{ formatted_interactions }}

## Agent response:
{{ agent_response }}"""


@tool
def span_critique(trace: list[dict], span_index: int) -> str:
    """
    Critique a single span within an agent trace.

    Args:
        trace (list[dict]): The list of spans that make up the trace.
        span_index (int): The index of the span within the lists of spans to critique.

    Example:
        Critique the 9th span in the trace.
        >>> span_critique(trace, 9)
        "The agent uses the incorrect order ID. It should have used ID #1234567890."

    Raises:
        ValueError: If the span index is not between 1 and the length of the trace.
        ValueError: If the span is not an assistant response.

    Returns:
       str: The critique of the span.
    """
    if span_index <= 0 or span_index > len(trace):
        raise ValueError(f"Span index must be between 1 and {len(trace)}")
    if trace[span_index - 1]["role"] != "assistant":
        raise ValueError(f"Span at index {span_index} is not an assistant response.")

    spans = trace[:span_index]
    agent_response = format_interaction(spans.pop())
    formatted_interactions = format_interactions(spans)

    prompt = Template(SPAN_CRITIQUE_PROMPT_TEMPLATE).render(
        formatted_interactions=formatted_interactions, agent_response=agent_response
    )
    response = call_llm(prompt)
    return response.content.strip()


def format_interactions(interactions: list[dict[str, Any]]) -> str:
    """
    Format a list of interactions into a string.

    Args:
        interactions: A list of interactions.

    Returns:
        A string of the interactions.

    Example output:
        ```
        [user]
        What's the weather in Tokyo?

        [assistant: agent]
        Tool call: get_weather(
            city="Tokyo",
        )

        [assistant: agent]
        Sunny.
        ```
    """
    return "\n\n".join([format_interaction(interaction) for interaction in interactions])


def format_interaction(interaction: dict[str, Any]) -> str:
    role = interaction['role']
    content = format_content(interaction)
    name = interaction.get('name', "agent" if role == "assistant" else "")
    name_str = f": {name}" if name else ""
    if role == "system":
        return content
    return f"[{role}{name_str}]\n{content}"


def format_content(interaction: dict[str, Any]) -> str:
    if interaction.get("tool_calls") is None:
        if interaction.get("role") == "tool":
            try:
                content = json.loads(interaction["content"])
                if isinstance(content, (str, int, float, bool)):
                    return interaction["content"]
                return yaml.dump(content, default_flow_style=False)
            except Exception as _:
                return interaction["content"]
        return interaction["content"]

    function_name = interaction["tool_calls"][0]["function"]["name"]
    function_kwargs = interaction["tool_calls"][0]["function"]["arguments"]
    function_kwargs = json.dumps(literal_eval(function_kwargs), indent=4)
    function_kwargs = ",\n    ".join([f"{k}={v}" for k, v in literal_eval(function_kwargs).items()])
    function_str = f"{function_name}(\n    {function_kwargs},\n)"
    return f"[Tool call]\n{function_str}"
@tool
def summarize_critiques(critiques: list[str]) -> str:
    """
    Summarize a list of critiques.

    Args:
        critiques (list[str]): The list of critiques to summarize.

    Returns:
        str: The summary of the critiques.
    """
    prompt = f"""You are a helpful assistant that summarizes critiques of agent responses.
    You will receive a list of critiques that were generated by analyzing interactions
    between an agent, the user, and the tools called by the agent.

Your task is to provide a concise summary that:
- Identifies common themes and patterns across the critiques
- Highlights the most important points and recommendations
- Maintains the specific, actionable nature of the original critiques
- Presents the information in a clear, structured format

Here is the list of critiques to summarize:
{critiques}

Please provide a concise summary that captures the key insights and recommendations
from these critiques."""
    response = call_llm(prompt)
    return response


@tool
def summarize_trace(trace: Any) -> str:
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
