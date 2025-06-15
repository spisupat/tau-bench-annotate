from smolagents import GradioUI

from annotator.agent import agent

if __name__ == "__main__":
    # Launch the Gradio UI
    ui = GradioUI(
        agent,
        file_upload_folder="./data",
    )
    ui.launch()
