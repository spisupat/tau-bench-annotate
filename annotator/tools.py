import json
import os
from typing import Any

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
derived from an OpenTelemetry span.

The important information to critique is the conversation history itself. This information
can generally be found in the attributes of the span with attribute names starting with
"gen_ai".

For example:

"gen_ai.prompt.1.content": "Hey there. I need to update the shipping address for my order and also do an exchange for a keyboard I ordered.",
"gen_ai.prompt.1.role": "user",

These spans show that the 1th (0-indexed) message in the conversation is from the user
and what the content of the message is.

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

Once again, you should only critique the conversation history, including any tool calls.\
Do not critique other information in the span, such as duration and other performance metrics.

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

    Not all spans will have a conversation history. If the conversation history is
    not present, this tool will return "No conversation history found."

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
