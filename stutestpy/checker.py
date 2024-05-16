from __future__ import annotations

import traceback
from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeAlias

import rich

from . import results as R

if TYPE_CHECKING:
    from .matcher import SequenceMatcher

console = rich.get_console()
console._highlight = False

CheckerResult: TypeAlias = R.AC | R.WA | R.PE | R.INT


class Checker:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check(self, index: int, stdin: str, stdout: str, ans: str) -> CheckerResult: ...


class SequenceMatchChecker(Checker):
    def __init__(
        self,
        matcher_cls: type[SequenceMatcher],
        default_judge: bool = False,
        **matcher_args,
    ) -> None:
        self.matcher_cls = matcher_cls
        self.matcher_args = matcher_args
        self.default_judge = default_judge
        self.fallback_fun: Callable[[str, str, str], CheckerResult | None] | None = None

    def check(self, index: int, stdin: str, stdout: str, ans: str) -> CheckerResult:
        matcher = self.matcher_cls(ans, **self.matcher_args)
        try:
            m = matcher(stdout)
            if m.ok:
                console.print("stdout: ", style="blue")
                console.print(m.match_str)
                return R.AC()
            # fallback
            if self.fallback_fun:
                fb = self.fallback_fun(stdin, stdout, ans)
                if fb:
                    return fb
            # 无法自动识别
            console.print(f"Matched: {len(m.matched)}/{matcher.num_patterns}", style="red")
            console.print("stdout: ", style="blue")
            console.print(m.match_str, highlight=False, markup=False)
            console.print(f"Manual judge #{index} (yes=AC): ", end="", style="cyan")
            judge = console.input().lower()
            if judge in ("int", "i"):
                return R.INT()
            if self.default_judge:
                j = judge not in ("no", "n", "f")
            else:
                j = judge in ("yes", "y", "t")
            return R.AC() if j else R.WA()
        except Exception as _:
            return R.PE(traceback.format_exc())
