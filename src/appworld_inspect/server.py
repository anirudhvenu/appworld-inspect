"""Host-side helpers to talk to the AppWorld environment server in the sandbox."""

import asyncio
import json
from typing import Any

from inspect_ai.util import sandbox

CLIENT_PATH = "/opt/aw_client.py"

SERVER_STARTUP_TIMEOUT_SECONDS = 120


class AppWorldServerError(RuntimeError):
    """The environment server returned an error or was unreachable."""


async def server_request(
    path: str, payload: dict[str, Any] | None = None, method: str = "POST"
) -> Any:
    """Send one request to the environment server via the in-sandbox client."""
    request = json.dumps({"path": path, "method": method, "payload": payload or {}})
    result = await sandbox().exec(["python3", CLIENT_PATH], input=request)
    if not result.success:
        raise AppWorldServerError(
            f"client failed for {path}: {result.stderr or result.stdout}"
        )
    response = json.loads(result.stdout)
    if isinstance(response, dict) and "error" in response:
        raise AppWorldServerError(
            f"{path}: {response['error']}: {response.get('detail', '')}"
        )
    return response.get("output") if isinstance(response, dict) else response


async def wait_for_server() -> None:
    """Poll the environment server root endpoint until it responds."""
    deadline = asyncio.get_event_loop().time() + SERVER_STARTUP_TIMEOUT_SECONDS
    last_error: Exception | None = None
    while asyncio.get_event_loop().time() < deadline:
        try:
            await server_request("/", method="GET")
            return
        except (AppWorldServerError, json.JSONDecodeError) as error:
            last_error = error
            await asyncio.sleep(2)
    raise AppWorldServerError(f"environment server did not start: {last_error}")


async def initialize_task(task_id: str, max_interactions: int) -> dict[str, Any]:
    """Initialize the AppWorld world for a task and return its metadata."""
    return await server_request(
        "/initialize",
        {
            "task_id": task_id,
            "experiment_name": "inspect",
            "max_interactions": max_interactions,
        },
    )


async def execute_in_world(task_id: str, code: str) -> str:
    """Execute agent code in the task world and return the shell output."""
    output = await server_request("/execute", {"task_id": task_id, "code": code})
    return output if isinstance(output, str) else json.dumps(output)


async def task_completed(task_id: str) -> bool:
    """Check whether the agent has marked the task complete."""
    output = await server_request("/task_completed", {"task_id": task_id})
    return bool(output)


async def evaluate_task(task_id: str) -> dict[str, Any]:
    """Run AppWorld's programmatic evaluation for the task."""
    output = await server_request(
        "/evaluate", {"task_id": task_id, "suppress_errors": True, "report": False}
    )
    if not isinstance(output, dict):
        raise AppWorldServerError(f"unexpected evaluate output: {output!r}")
    return output
