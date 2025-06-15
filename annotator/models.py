
"""Shared model wrapper using LiteLLM with Claude."""
from smolagents import LiteLLMModel

# Shared model instance using Claude
_model = LiteLLMModel(model_id="anthropic/claude-4-sonnet-20250514")

# Default generation config
_gen_cfg = dict(temperature=0.2)

# Vanilla LLM call for use with tools
def call_llm(prompt: str, **overrides):
    """Call the LLM with the given prompt and optional overrides.
    
    Args:
        prompt: The prompt to send to the model
        **overrides: Optional generation parameter overrides

    Returns:
        The model's response as a string
    """
    kwargs = _gen_cfg.copy()
    kwargs.update(overrides)

    # Format the prompt as a list of messages for LiteLLM
    messages = [
        {"role": "user", "content": prompt}
    ]

    return _model.generate(messages=messages, **kwargs)
