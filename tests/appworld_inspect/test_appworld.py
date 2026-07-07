"""Tests for the AppWorld evaluation."""

import os

import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.scorer import SampleScore, Score

from appworld_inspect.dataset import appworld_dataset, load_task_ids, task_id_to_sample
from appworld_inspect.scorer import scenario_goal_completion


def test_task_id_to_sample() -> None:
    sample = task_id_to_sample("50e1ac9_1")
    assert sample.id == "50e1ac9_1"
    assert sample.metadata is not None
    assert sample.metadata["scenario_id"] == "50e1ac9"


def test_split_lists_are_vendored() -> None:
    assert len(load_task_ids("dev")) == 57
    assert len(load_task_ids("test_normal")) == 168
    assert len(appworld_dataset("test_challenge")) == 417


def test_scenario_goal_completion_groups_variations() -> None:
    def sample_score(sample_id: str, value: str) -> SampleScore:
        return SampleScore(sample_id=sample_id, score=Score(value=value))

    from typing import Callable, cast

    compute = cast(Callable[[list[SampleScore]], float], scenario_goal_completion())
    scores = [
        sample_score("aaa_1", "C"),
        sample_score("aaa_2", "C"),
        sample_score("bbb_1", "C"),
        sample_score("bbb_2", "I"),
    ]
    assert compute(scores) == 0.5


@pytest.mark.skipif(
    not os.environ.get("RUN_SLOW_TESTS"),
    reason="Requires Docker and AppWorld data; set RUN_SLOW_TESTS=1 to run.",
)
def test_end_to_end_with_mock_model() -> None:
    from appworld_inspect import appworld

    logs = inspect_eval(
        appworld(split="dev", message_limit=6),
        model="mockllm/model",
        limit=1,
    )
    assert logs[0].status == "success"
    assert logs[0].results is not None
    assert logs[0].results.scores[0].metrics["accuracy"].value == 0.0


@pytest.mark.skipif(
    not os.environ.get("RUN_SLOW_TESTS"),
    reason="Requires Docker and AppWorld data; set RUN_SLOW_TESTS=1 to run.",
)
def test_execute_code_round_trip_with_scripted_model() -> None:
    from inspect_ai.model import ModelOutput, get_model

    from appworld_inspect import appworld

    model = get_model(
        "mockllm/model",
        custom_outputs=[
            ModelOutput.for_tool_call(
                model="mockllm/model",
                tool_name="execute_code",
                tool_arguments={"code": "print(apis.api_docs.show_app_descriptions())"},
            ),
            ModelOutput.for_tool_call(
                model="mockllm/model",
                tool_name="submit",
                tool_arguments={"answer": "done"},
            ),
        ],
    )
    logs = inspect_eval(
        appworld(split="dev", message_limit=8),
        model=model,
        limit=1,
    )
    assert logs[0].status == "success"
    assert logs[0].samples is not None
    tool_messages = [
        message
        for message in logs[0].samples[0].messages
        if message.role == "tool" and message.function == "execute_code"
    ]
    assert tool_messages, "execute_code tool was never called"
    assert "api_docs" in tool_messages[0].text


def test_render_system_message_fills_all_markers() -> None:
    from appworld_inspect.solver import render_system_message

    rendered = render_system_message(
        {
            "supervisor": {
                "first_name": "Glenn",
                "last_name": "Burton",
                "email": "glenn.burton@gmail.com",
                "phone_number": "8638518861",
            },
            "datetime": "2023-05-18T12:00:00",
        }
    )
    assert "<<" not in rendered
    assert "Glenn Burton" in rendered
    assert "2023-05-18T12:00:00" in rendered


def test_initialize_appworld_is_a_solver() -> None:
    from inspect_ai.solver import Solver

    from appworld_inspect.solver import initialize_appworld

    assert isinstance(initialize_appworld(max_interactions=200), Solver)


def test_appworld_scorer_is_a_scorer() -> None:
    from appworld_inspect.scorer import appworld_scorer

    assert callable(appworld_scorer())
