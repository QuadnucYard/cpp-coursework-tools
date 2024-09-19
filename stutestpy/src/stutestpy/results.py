from typing import ClassVar


class TestResult:
    color: ClassVar[str | None] = None

    def __init__(self, msg: str = "") -> None:
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.status}: {self.msg}"

    @property
    def status(self) -> str:
        return self.__class__.__name__


class UnexpectedResult(TestResult, BaseException): ...


class AC(TestResult):
    color = "green"

    def __init__(self, msg: str = "Accepted") -> None:
        super().__init__(msg)


class WA(TestResult):
    color = "red"


class MISS(UnexpectedResult):
    color = "red"


class PE(UnexpectedResult):
    color = "red"


class RE(UnexpectedResult):
    color = "magenta"


class TLE(UnexpectedResult):
    color = "cyan"


class CE(UnexpectedResult):
    color = "rgb(255,165,0)"

    def __init__(self, msg: str = "Compilation Error", details: str = "") -> None:
        super().__init__(msg)
        self.details = details


class UKE(UnexpectedResult):
    color = "rgb(123,104,238)"


class INT(UnexpectedResult):
    color = "blue"
