from dataclasses import dataclass
from typing import List


@dataclass
class CommandResult:
    stdout: List[str] | None
    stderr: List[str] | None
    exit_code: int
