from typing import ClassVar

from colorama import Fore


class TestResult:
    color: ClassVar[str | None] = None

    def __init__(self, msg: str = "") -> None:
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.msg}"

    @property
    def status(self) -> str:
        return self.__class__.__name__


class UnexpectedResult(TestResult, BaseException): ...


class AC(TestResult):
    color = Fore.GREEN

    def __init__(self, msg: str = "Accepted") -> None:
        super().__init__(msg)


class WA(TestResult):
    color = Fore.RED


class MISS(UnexpectedResult):
    color = Fore.RED


class PE(UnexpectedResult):
    color = Fore.RED


class RE(UnexpectedResult):
    color = Fore.MAGENTA


class TLE(UnexpectedResult):
    color = Fore.CYAN


class CE(UnexpectedResult):
    color = Fore.YELLOW


class UKE(UnexpectedResult):
    color = Fore.BLUE


class INT(UnexpectedResult):
    color = Fore.BLUE
