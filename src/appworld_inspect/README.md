# AppWorld

[AppWorld](https://appworld.dev) ([arXiv:2407.18901](https://arxiv.org/abs/2407.18901), ACL 2024 Best Resource Paper) benchmarks interactive coding agents on day-to-day digital tasks: the agent acts for a human supervisor by writing Python against 457 APIs across 9 simulated apps (email, payments, music, file system, shopping, etc.), backed by ~100 database tables. Success is judged by programmatic checks on the resulting database state — robust to valid alternative solutions and requiring no LLM judge.

## Implementation

- The full AppWorld environment (engine, apps, task data) runs inside a Docker sandbox; the container serves AppWorld's environment server on localhost.
- The agent gets a single `execute_code` tool that forwards Python to the task world's stateful IPython shell — the same `world.execute` interface used by the paper's agents.
- Task instructions and supervisor details are loaded from the environment at solve time (the host never decrypts AppWorld's anti-contamination data bundles; only task-id split lists are vendored).
- Scoring calls AppWorld's own evaluation (`world.evaluate()`) inside the sandbox. Metrics: **accuracy** = Task Goal Completion (TGC), plus **scenario_goal_completion** (SGC: a scenario counts only if all its task variations pass), matching the paper.
- The system prompt is adapted near-verbatim from the upstream ReAct agent prompt (`experiments/prompts/react_code_agent/instructions.txt`, Apache-2.0) — the prompt behind the paper's ReAct baselines — converted from its markdown-code-block conversation protocol to the execute_code tool interface. The default `message_limit=100` (~50 assistant turns) matches upstream's `max_steps: 50`.

## Usage

```bash
uv run inspect eval appworld_inspect/appworld --model <model>          # test_normal (168 tasks)
uv run inspect eval appworld_inspect/appworld -T split=dev --limit 10  # cheap shakeout
```

Task parameters: `split` (train | dev | test_normal | test_challenge), `solver`, `message_limit` (default 100), `max_interactions` (default 200).

## Baseline results (paper / leaderboard)

| Agent + Model | test_normal TGC | test_normal SGC |
|---|---|---|
| ReAct + GPT-4o (paper; the comparability anchor for this port) | 48.8 | 32.1 |
| ReAct + GPT-4o, 2 SetBSR demos (2025) | 68.5 | 57.1 |
| IBM CUGA + GPT-4.1 (2025) | 73.2 | 62.5 |

Reference trajectories: `appworld download experiment-outputs` provides the paper agents' per-task evaluations and environment API-call logs (ReAct+GPT-4o on test_normal: median 30 env API calls/task, their step cap 50), enabling per-task comparison against this port's runs.

See [appworld.dev/leaderboard](https://appworld.dev/leaderboard) for current entries.

<!-- Evaluation report to be added after baseline reproduction runs. -->
