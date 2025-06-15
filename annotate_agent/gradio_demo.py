from smolagents import GradioUI  # type: ignore [import-untyped]

from annotate_agent.planner import agent

if __name__ == "__main__":
    # Launch the Gradio UI
    ui = GradioUI(
        agent,
        file_upload_folder="./data",
    )
    ui.launch()
