"""Load AppWorld tasks as Inspect samples.

Only task ids are needed host-side (vendored split lists from the AppWorld
data release, Apache-2.0). Task instructions and supervisor details live in
the encrypted data bundle inside the sandbox image and are fetched from the
environment server's /initialize response at solve time, respecting
AppWorld's anti-contamination packaging.
"""

from pathlib import Path
from typing import Literal

from inspect_ai.dataset import Sample

Split = Literal["train", "dev", "test_normal", "test_challenge"]

SPLITS_DIR = Path(__file__).parent / "splits"


def load_task_ids(split: Split) -> list[str]:
    """Read the task ids for a split from the vendored split lists."""
    split_file = SPLITS_DIR / f"{split}.txt"
    return [
        line.strip() for line in split_file.read_text().splitlines() if line.strip()
    ]


def task_id_to_sample(task_id: str) -> Sample:
    """Build a placeholder Sample; instruction is filled in at solve time."""
    return Sample(
        id=task_id,
        input=f"AppWorld task {task_id} (instruction is loaded from the environment).",
        metadata={"scenario_id": task_id.split("_")[0]},
    )


def appworld_dataset(split: Split) -> list[Sample]:
    """Build the Inspect dataset for an AppWorld split."""
    return [task_id_to_sample(task_id) for task_id in load_task_ids(split)]
