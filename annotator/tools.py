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
        raise ValueError(f"Span index must be between 0 and {len(trace) - 1}")
    if trace[span_index - 1]["role"] != "assistant":
        raise ValueError(f"Span at index {span_index} is not an assistant response.")

    spans = trace[:span_index]
    formatted_interactions = format_interactions(spans)
    agent_response = format_interaction(spans.pop())

    prompt = Template(SPAN_CRITIQUE_PROMPT_TEMPLATE).render(formatted_interactions=formatted_interactions, agent_response=agent_response)
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
