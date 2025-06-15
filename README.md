# Evaluagent

This repo contains a copy of the [`tau-bench`](https://github.com/sierra-research/tau-bench) repository, and extends it with the ability to run an agent to evaluate resulting traces.

## Development Setup

1. Ensure you have Python 3.10+ installed
2. Install [uv](https://github.com/astral-sh/uv) package manager (version >=0.7.2)
3. Activate environment:
   ```bash
   uv venv && source .venv/bin/activate
   cp .env.example .env
   ```
4. Paste in your Anthropic and OpenAI API keys to the `.env` file.
   > Note: We are using Claude to evaluate GPT, thus you will only need the OPENAI_API_KEY if you are running $\tau$-bench.

## Running $\tau$-bench

> Note: You do not need to run this to run the Evaluagent, we have already compiled some examples [spreadsheet](https://docs.google.com/spreadsheets/d/1POO8urTFoK6j9MrtLOAK-nHZBM6MkLLGKD5zgZOpCjs/edit?gid=0#gid=0).

To produce a trace from $\tau$-bench, run:

```bash
./tau_bench/run.sh
```

## Running the Annotator Demo

From the project root, run:

```bash
uv run annotator/demo.py
```

This will start a Gradio web interface where you can interact with the annotation agent.

You may like to paste into the prompt, for example:

```
What went wrong with the trace with ID 0197731a0aea9eb90cda49069173a187?
```

Alternatively, you may choose a trace ID from this [spreadsheet](https://docs.google.com/spreadsheets/d/1POO8urTFoK6j9MrtLOAK-nHZBM6MkLLGKD5zgZOpCjs/edit?gid=0#gid=0) that has human annotations to compare to, the traces get progressively longer and harder as they go down.
