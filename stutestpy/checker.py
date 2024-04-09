from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

from colorama import Fore

from . import result
from .utils import colored

if TYPE_CHECKING:
    from .matcher import SequenceMatcher
    from .tester import Tester


class Checker:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check(self, tester: Tester, index: int, input: str, output: str, ans: str) -> result.TestResult: ...


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
        self.fallback_fun: Callable[[str, str, str], result.TestResult | None] | None = None

    def check(self, tester: Tester, index: int, input_: str, output: str, ans: str) -> result.TestResult:
        matcher = self.matcher_cls(ans, **self.matcher_args)
        try:
            m = matcher(output)
            if m.ok:
                print(colored("stdout: ", fg=Fore.BLUE))
                print(m.match_str)
                return result.AC()
            # fallback
            if self.fallback_fun:
                fb = self.fallback_fun(input_, output, ans)
                if fb:
                    return fb
            # 无法自动识别
            print(colored(f"Matched: {len(m.matched)}/{matcher.num_patterns}", fg=Fore.RED))
            print(colored("stdout: ", fg=Fore.BLUE))
            print(m.match_str)
            judge = input(colored(f"Manual judge #{index} (yes=AC): ", fg=Fore.CYAN)).lower()
            if judge in ("int", "i"):
                raise result.INT
            if self.default_judge:
                j = judge not in ("no", "n", "f")
            else:
                j = judge in ("yes", "y", "t")
            return result.AC() if j else result.WA()
        except Exception as _:
            raise result.PE from None
