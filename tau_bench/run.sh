# chmod +x tau_bench/run.sh
# tau_bench/run.sh
uv run python tau_bench/run.py \
    --num-trials 1 \
    --env retail \
    --model claude-3-haiku-20240307 \
    --model-provider anthropic \
    --user-model claude-3-7-sonnet-20250219 \
    --user-model-provider anthropic \
    --agent-strategy tool-calling \
    --temperature 0.0 \
    --task-split dev \
    --start-index 0 \
    --end-index -1 \
    --task-ids 0 1 2 \
    --log-dir results \
    --max-concurrency 1 \
    --seed 10 \
    --shuffle 0 \
    --user-strategy llm
