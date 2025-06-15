# chmod +x tau_bench/run.sh
# tau_bench/run.sh
uv run python tau_bench/run.py \
    --num-trials 1 \
    --env retail \
    --model gpt-4o-mini \
    --model-provider openai \
    --user-model claude-3-7-sonnet-20250219 \
    --user-model-provider anthropic \
    --agent-strategy tool-calling \
    --temperature 0.0 \
    --task-split dev \
    --start-index 0 \
    --end-index -1 \
    --task-ids 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 \
    --log-dir results \
    --max-concurrency 2 \
    --seed 10 \
    --shuffle 0 \
    --user-strategy llm
