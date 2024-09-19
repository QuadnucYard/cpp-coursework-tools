from collections.abc import Generator
from pathlib import Path
from typing import Any

import rich

console = rich.get_console()


class TestCases:
    def __init__(self, root: str | Path, prefix: str, *, has_stdin: bool = True) -> None:
        self.prefix = prefix
        self.has_stdin = has_stdin
        root = Path(root)
        self.cases = sorted(root.glob(rf"{prefix}-*.ans"), key=lambda x: int(x.stem.split("-")[-1])) or list(
            root.glob(rf"{prefix}.ans")
        )
        self.stdin_str = [f.with_suffix(".in").read_text() for f in self.cases if f.with_suffix(".in").exists()]
        self.ans_str = [f.read_text() for f in self.cases]
        if not self.cases:
            console.print("WARN: no test case found!", style="red")

    def __len__(self) -> int:
        return len(self.cases)

    def __iter__(self) -> Generator[tuple[str, str], Any, None]:
        """Iterate through all test cases

        Returns:
            Iterable[tuple[str, str]]: pairs of (stdin, ans)
        """
        return self._generator()

    def _generator(self) -> Generator[tuple[str, str], Any, None]:
        if self.has_stdin:
            yield from zip(self.stdin_str, self.ans_str, strict=True)
        else:
            yield ("", self.ans_str[0])
