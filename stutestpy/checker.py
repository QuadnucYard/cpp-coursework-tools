from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stutestpy import result
    from stutestpy.tester import Tester


class Checker:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check(self, tester: Tester, index: int, input: str, output: str, ans: str) -> result.TestResult: ...
