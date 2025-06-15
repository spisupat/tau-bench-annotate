from smolagents import CodeAgent, LiteLLMModel  # type: ignore [import-untyped]

agent = CodeAgent(
    model=LiteLLMModel(model_id="anthropic/claude-3-7-sonnet-20250219"),
    tools=[
    ],
    stream_outputs=True,
    verbosity_level=1,
    planning_interval=3,
    name="trace_annotator",
    description="This agent analyzes and annotates agent execution traces."
)
