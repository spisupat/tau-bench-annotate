from smolagents import GradioUI  # type: ignore [import-untyped]
from annotator.agents import orchestrator

if __name__ == "__main__":
    # Launch the Gradio UI
    ui = GradioUI(
        orchestrator,
        file_upload_folder="./data",
    )
    ui.launch()
