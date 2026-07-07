"""AppWorld: benchmarking interactive coding agents over app APIs.

Port of AppWorld (arXiv:2407.18901, ACL 2024) to Inspect. The agent
accomplishes day-to-day digital tasks for a supervisor by writing Python
against 457 app APIs in a simulated world of 9 apps; success is judged by
programmatic checks of the resulting database state.
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import Solver

from appworld_inspect.dataset import Split, appworld_dataset
from appworld_inspect.scorer import appworld_scorer
from appworld_inspect.solver import default_solver

COMPOSE_FILE = Path(__file__).parent / "compose.yaml"

DEFAULT_MESSAGE_LIMIT = 100
DEFAULT_MAX_INTERACTIONS = 200


@task
def appworld(
    split: Split = "test_normal",
    solver: Solver | None = None,
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
    max_interactions: int = DEFAULT_MAX_INTERACTIONS,
) -> Task:
    """AppWorld interactive coding agent benchmark.

    Args:
        split: Task split to evaluate (train, dev, test_normal, test_challenge).
            Defaults to test_normal, the split reported on the leaderboard.
        solver: Custom solver (defaults to a basic tool-use agent).
        message_limit: Maximum conversation messages before termination.
        max_interactions: AppWorld-side cap on world interactions.
    """
    return Task(
        dataset=appworld_dataset(split),
        solver=solver or default_solver(message_limit, max_interactions),
        scorer=appworld_scorer(),
        sandbox=("docker", str(COMPOSE_FILE)),
        message_limit=message_limit,
    )
