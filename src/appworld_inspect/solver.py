"""Default agent solver for AppWorld."""

from typing import Any

from inspect_ai.model import ChatMessageSystem
from inspect_ai.solver import Generate, Solver, TaskState, basic_agent, chain, solver
from inspect_ai.util import store

from appworld_inspect.prompt import CONTINUE_MESSAGE, SYSTEM_MESSAGE
from appworld_inspect.server import initialize_task, wait_for_server
from appworld_inspect.tools import execute_code


def render_system_message(task_info: dict[str, Any]) -> str:
    """Fill supervisor and datetime details into the system prompt."""
    supervisor = task_info["supervisor"]
    message = SYSTEM_MESSAGE
    for marker, value in {
        "<<supervisor_first_name>>": supervisor["first_name"],
        "<<supervisor_last_name>>": supervisor["last_name"],
        "<<supervisor_email>>": supervisor["email"],
        "<<supervisor_phone_number>>": supervisor["phone_number"],
        "<<datetime>>": task_info["datetime"],
    }.items():
        message = message.replace(marker, str(value))
    return message


@solver
def initialize_appworld(max_interactions: int) -> Solver:
    """Start the task world, set the system prompt, and load the instruction."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        await wait_for_server()
        task_info = await initialize_task(str(state.sample_id), max_interactions)
        store().set("appworld_task_id", str(state.sample_id))
        state.messages.insert(
            0, ChatMessageSystem(content=render_system_message(task_info))
        )
        state.user_prompt.text = f"Using these APIs, now generate code to solve the actual task:\n\nTask: {task_info['instruction']}"
        return state

    return solve


def default_solver(message_limit: int, max_interactions: int) -> Solver:
    """The default AppWorld agent: initialize, then a basic tool-use loop."""
    return chain(
        initialize_appworld(max_interactions),
        basic_agent(
            tools=[execute_code()],
            message_limit=message_limit,
            continue_message=CONTINUE_MESSAGE,
        ),
    )
