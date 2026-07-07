"""The execute_code tool exposed to the agent.

Mirrors AppWorld's native interaction protocol: the agent acts exclusively by
writing Python that runs in the task world's stateful IPython shell
(world.execute), the same interface used by the paper's agents.
"""

from inspect_ai.tool import Tool, tool
from inspect_ai.util import store

from appworld_inspect.server import execute_in_world, task_completed


@tool
def execute_code() -> Tool:
    """Tool that executes Python code in the AppWorld environment."""

    async def execute(code: str) -> str:
        """Execute Python code in the AppWorld task environment.

        The environment is a stateful IPython shell with access to `apis`
        (all app APIs, e.g. apis.spotify.login(...)) and `supervisor`
        details. Variables persist across calls. Output printed by the code
        (including API call results) is returned.

        Args:
            code: Python source code to execute in the task world.

        Returns:
            The shell output of executing the code.
        """
        task_id = store().get("appworld_task_id")
        output = await execute_in_world(task_id, code)
        if await task_completed(task_id):
            store().set("appworld_task_completed", True)
            output += "\n\nTask marked complete via apis.supervisor.complete_task()."
        return output

    return execute
