from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import rich
from dataclasses_json import DataClassJsonMixin
from result import Err, Ok

from . import results as R

if TYPE_CHECKING:
    from .cases import TestCases
    from .checker import Checker
    from .compiler import Compiler
    from .runner import TestRunner
    from .worktree import WorkTree


console = rich.get_console()


@dataclass
class TestCaseLog(DataClassJsonMixin):
    output: str | None
    status: str
    message: str


@dataclass
class TestLog(DataClassJsonMixin):
    submitter: str
    status: str = ""
    result: list[TestCaseLog] | None = None
    message: str = ""
    passed: int = 0


class Tester:

    def __init__(
        self, worktree: WorkTree, testcases: TestCases, compiler: Compiler, runner: TestRunner, checker: Checker
    ) -> None:
        self.worktree = worktree
        self.testcases = testcases
        self.compiler = compiler
        self.runner = runner
        self.checker = checker

        self.tmp_path = Path("tmp")

        self.output_trunc = 20
        self.time_limit = 1.0
        self.tle_as_ac = False
        self.tle_handler: Callable[[str, str], R.TestResult | None] | None = None

    def run_tests(self, exe: Path, log: TestLog) -> bool:
        results: list[R.TestResult] = []
        log.result = []

        for i, (tc_in, tc_ans) in enumerate(self.testcases):
            console.print(f"Case {i}", style="bold bright_blue")

            match self.runner.run(exe, tc_in):
                case Ok(out):
                    res = self.checker.check(i, stdin=tc_in, stdout=out, ans=tc_ans)
                    if isinstance(res, R.AC | R.WA):
                        results.append(res)
                        log.result.append(TestCaseLog(out, res.status, res.msg))
                        if isinstance(res, R.AC):
                            log.passed += 1

                        console.print(results[-1], style=results[-1].color, highlight=False)

                    elif isinstance(res, R.INT):
                        console.print("Interrupt", style="bold bright_cyan")
                        return False
                case Err(e):
                    # 暂时放弃TLE的处理
                    results.append(e)
                    log.result.append(TestCaseLog(str(e), e.status, e.msg))

                    console.print(results[-1].status, style=results[-1].color, highlight=False, end=": ")
                    console.print(results[-1].msg, highlight=False, markup=False)

        return True

    def test_one(self, folder_: Path | str) -> TestLog:
        folder = Path(folder_)
        log = TestLog(folder.name)
        console.print(f"Test {folder}", style="bold magenta")

        # 加入提交文件到工作树
        if not self.worktree.set_root(folder):
            console.print("Failed to find submission", style="red")
            log.status = R.MISS().status
            return log

        # 找到后编译
        match self.worktree.compile_with(self.compiler):
            case Ok(exe):
                if self.run_tests(exe, log):
                    console.print(
                        f"Passed: {log.passed}/{len(self.testcases)}",
                        style="bold green" if log.passed == len(self.testcases) else "bold red",
                    )
                    console.input("Press any key to continue...")
                exe.unlink()

            case Err(e):
                log.status = e.status
                log.message = e.msg
                console.print(e, style=e.color)
                console.input("Press any key to continue...")

        return log

    def test_many(self, folder_: Path | str, save_path: Path | None = None) -> list[TestLog]:
        folder = Path(folder_)
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)

        logs: list[TestLog] = []
        for f in folder.iterdir():
            if not (f.is_dir() and f.name != "src"):
                continue
            logs.append(self.test_one(f))
            if save_path:
                logs_json = [t.to_dict() for t in logs]
                save_path.write_text(json.dumps(logs_json, ensure_ascii=False, indent=2), encoding="utf-8")

        console.print("Test completed!", style="bold green")

        if save_path:
            console.print(f"Save logs to {save_path}", style="green")

        return logs
