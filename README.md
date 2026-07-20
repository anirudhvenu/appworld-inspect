# appworld-inspect

An [Inspect AI](https://inspect.aisi.org.uk/) implementation of **[AppWorld](https://appworld.dev)** ([arXiv:2407.18901](https://arxiv.org/abs/2407.18901), ACL 2024 Best Resource Paper) — a benchmark of 750 day-to-day digital tasks where an agent acts for a human supervisor by writing Python against 457 APIs across 9 simulated apps, scored by programmatic checks on the resulting database state.

Built for the [inspect_evals register](https://github.com/UKGovernmentBEIS/inspect_evals).

## Quick start

```bash
uv sync
uv run inspect eval appworld_inspect/appworld --model <model>          # test_normal (168 tasks)
uv run inspect eval appworld_inspect/appworld -T split=dev --limit 10  # small dev-split run
```

Requires Docker: the AppWorld environment (engine, apps, task data) is built into a sandbox image on first run; task data is downloaded from AppWorld's versioned storage at image build time, verified against a pinned SHA-256, and never redistributed by this repository.

See **[src/appworld_inspect/README.md](src/appworld_inspect/README.md)** for the eval's design, task parameters, scoring (TGC/SGC), and baseline results.

## Repository layout

- `src/appworld_inspect/` — the eval (task, solver, scorer, tools, sandbox definition)
- `tests/appworld_inspect/` — unit tests plus Docker-gated end-to-end tests (`RUN_SLOW_TESTS=1`)
- `src/examples/`, `src/utils/`, `tools/`, `.github/workflows/checks.yml` — retained from the [inspect-evals-template](https://github.com/ArcadiaImpact/inspect-evals-template) (reference examples and the CI check suite)

## License

MIT. AppWorld itself (benchmark, data, engine) is by [Trivedi et al.](https://arxiv.org/abs/2407.18901), Apache-2.0.
