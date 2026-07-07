"""Scoring for AppWorld: programmatic state-based evaluation.

Task Goal Completion (TGC) is the per-task pass rate (accuracy). Scenario
Goal Completion (SGC) counts a scenario as passed only if all of its task
variations pass, matching the paper's metrics (arXiv:2407.18901).
"""

from collections import defaultdict

from inspect_ai.scorer import (
    CORRECT,
    INCORRECT,
    Metric,
    SampleScore,
    Score,
    Scorer,
    Target,
    accuracy,
    metric,
    scorer,
    stderr,
    value_to_float,
)
from inspect_ai.solver import TaskState

from appworld_inspect.server import evaluate_task


@metric
def scenario_goal_completion() -> Metric:
    """Fraction of scenarios whose task variations all passed (SGC)."""
    to_float = value_to_float()

    def compute(scores: list[SampleScore]) -> float:
        by_scenario: dict[str, list[float]] = defaultdict(list)
        for sample_score in scores:
            scenario_id = str(sample_score.sample_id).split("_")[0]
            by_scenario[scenario_id].append(to_float(sample_score.score.value))
        if not by_scenario:
            return 0.0
        passed = sum(
            1 for values in by_scenario.values() if all(v == 1.0 for v in values)
        )
        return passed / len(by_scenario)

    return compute


@scorer(metrics=[accuracy(), stderr(), scenario_goal_completion()])
def appworld_scorer() -> Scorer:
    """Score a task by running AppWorld's evaluation tests in the sandbox."""

    async def score(state: TaskState, target: Target) -> Score:
        result = await evaluate_task(str(state.sample_id))
        num_failures = len(result.get("failures", []))
        num_passes = len(result.get("passes", []))
        success = bool(result.get("success", num_failures == 0 and num_passes > 0))
        return Score(
            value=CORRECT if success else INCORRECT,
            explanation=f"{num_passes} test(s) passed, {num_failures} failed.",
            metadata=result,
        )

    return score
