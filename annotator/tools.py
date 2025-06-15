import json
import os
from ast import literal_eval
from typing import Any

import yaml
from jinja2 import Template
from smolagents import tool

from annotator.constants import DATA_DIR_PATH
from annotator.models import call_llm


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
You are a helpful assistant that critiques the response of an agent. You will receive data
derived from an OpenTelemetry span which may contain a
list of interactions between an AI agent and a user, and the tools called by the agent.

Not all spans will have this conversation history. If the conversation history is
not present, you can return "No conversation history found."

Rules of the critique:
- English only.
- Be specific, referring to specific parts of the conversation history and the agent's
response.
- Be as concise as possible.
- Do not output any other text than the critique.
- Whether the assistant's response or tool call addresses the user's problem or request.
- If a tool is called, whether the arguments (including IDs, names, or other parameters)
are correct and sufficient to solve the user's problem.
- Whether the assistant misuses a tool, omits necessary tool calls, or provides incorrect
or incomplete information.
- Any logical errors, hallucinations, or misunderstandings of the user's intent.
- The appropriateness and clarity of the assistant's response.

## Span data:
{{ span_data }}"""


@tool
def span_critique(span: dict) -> str:
    """
    Critique a single assistant span to detect potential failure modes.

    This tool is intended to be used by an agent to analyze assistant responses and tool
    usage for correctness and alignment with the user's intent. The critique should focus
    on the following aspects:
      - Whether the assistant's response or tool call addresses the user's problem or request.
      - If a tool is called, whether the arguments (including IDs, names, or other parameters)
        are correct and sufficient to solve the user's problem.
      - Whether the assistant misuses a tool, omits necessary tool calls, or provides incorrect
        or incomplete information.
      - Any logical errors, hallucinations, or misunderstandings of the user's intent.
      - The appropriateness and clarity of the assistant's response.

    Example:
        Critique an assistant response with its context:
        >>> span_critique({
        ...     "span_data": {"role": "assistant", "content": "The order status is 'shipped'."},
        ...     "context": [
        ...         {"role": "user", "content": "What's the status of order #12345?"},
        ...         {"role": "assistant", "tool_calls": [{"function": {"name": "get_order_status", "arguments": '{"order_id": "12345"}'}}]},
        ...         {"role": "tool", "content": '{"status": "shipped", "tracking_number": "ABC123"}'}
        ...     ]
        ... })
        "The assistant correctly reports the order status using the tool result."

    Args:
        span (dict): A dict containing span data.

    Returns:
        str: The critique of the assistant span, focusing on tool usage, argument correctness, and alignment with the user's intent.
    """
    prompt = Template(SPAN_CRITIQUE_PROMPT_TEMPLATE).render(span_data=str(span))
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
    role = interaction["role"]
    content = format_content(interaction)
    name = interaction.get("name", "agent" if role == "assistant" else "")
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
    function_kwargs = ",\n    ".join(
        [f"{k}={v}" for k, v in literal_eval(function_kwargs).items()]
    )
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
