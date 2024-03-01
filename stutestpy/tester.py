from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from io import FileIO
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from colorama import Fore, Style
from dataclasses_json import DataClassJsonMixin, dataclass_json

from . import result
from .finder import FindSubmissionByKeywords
from .utils import auto_decode, colored, trunc_lines

if TYPE_CHECKING:
    from .checker import Checker


@dataclass
class TestCaseLog(DataClassJsonMixin):
    output: str | None
    status: str
    message: str


@dataclass
class TestLog(DataClassJsonMixin):
    submitter: str
    status: str = ""
    result: Optional[list[TestCaseLog]] = None
    message: str = ""
    passed: int = 0


class Tester:
    def __init__(self, data_dir: Path, prefix: str, checker: Checker) -> None:
        self.prefix = prefix
        self.testcases = list(data_dir.glob(rf"{prefix}-*.in"))
        self.testcases.sort(key=lambda x: int(x.stem.split("-")[-1]))
        self.testcases_str = [f.read_text() for f in self.testcases]
        self.testans_str = [f.with_suffix(".ans").read_text() for f in self.testcases]

        self.tmp_path = Path("tmp")
        self.checker = checker
        self.finder = FindSubmissionByKeywords([prefix])

        self.output_trunc = 20
        self.tle_as_ac = False

    def find_submission(self, folder: Path) -> Path | None:
        return self.finder.find_submission(folder)

    def compile(self, source: PathLike) -> Path:  # type: ignore
        output_path = self.tmp_path / "out.exe"
        print(colored(f"Compile: {source}", fg=Fore.YELLOW))
        r = subprocess.call(
            [
                "g++",
                # "clang++",
                source,
                "-o",
                output_path,
                "-std=c++20",
                "-Wall",
                "-Wextra",
                # "-g",
                # "-fsanitize=address",
                # "-fno-omit-frame-pointer",
            ],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        if r != 0:
            raise result.CE
        return output_path

    def run(self, tc: Path, exe: Path) -> str:
        try:
            p = subprocess.Popen(exe, stdin=FileIO(tc), stdout=subprocess.PIPE)
            try:
                stdout, stderr = p.communicate(timeout=1)
            except subprocess.TimeoutExpired as e:
                p.kill()
                outs, errs = p.communicate()
                raise result.TLE(str(e)) from None
            if stderr:
                raise result.RE(auto_decode(stderr))
            p.terminate()
            return trunc_lines(auto_decode(stdout), self.output_trunc)
        except Exception as e:
            raise result.UKE(str(e)) from None

    def check(self, out: str, ans: str) -> None: ...

    def test_one(self, folder: Path) -> TestLog:
        log = TestLog(folder.name)
        print(colored(f"Test {folder}", fg=Fore.MAGENTA, sty=Style.BRIGHT))
        try:
            # 查找提交
            src = self.find_submission(folder)
            if not src:
                print(colored("Fail to find submission", fg=Fore.RED))
                log.status = result.MISS().status
                return log
            # 找到后编译
            exe = self.compile(src)
            results: list[result.TestResult] = []
            log.result = []
            for i, tc in enumerate(self.testcases):
                print(colored(f"Case {i}", fg=Fore.LIGHTBLUE_EX, sty=Style.BRIGHT))
                out = None
                try:
                    out = self.run(tc, exe)
                    res = self.checker.check(self, i, self.testcases_str[i], out, self.testans_str[i])
                    results.append(res)
                    log.result.append(TestCaseLog(out, res.status, res.msg))
                    if isinstance(res, result.AC):
                        log.passed += 1
                except result.UnexpectedResult as e:
                    if isinstance(e, result.INT):
                        print(colored("Interrupt", fg=Fore.LIGHTCYAN_EX))
                        break
                    if self.tle_as_ac and isinstance(e, result.TLE):
                        log.passed += 1
                        ee = result.AC(f"TLE accepted: {e.msg}")
                        results.append(ee)
                        log.result.append(TestCaseLog(out, ee.status, ee.msg))
                    else:
                        results.append(e)
                        log.result.append(TestCaseLog(out, e.status, e.msg))
                print("  ", colored(str(results[-1]), fg=results[-1].color), sep="")
            exe.unlink()
            return log
        except result.UnexpectedResult as e:
            log.status = e.status
            log.message = e.msg
            print(e)
            return log

    def test_many(self, folder: Path, save_path: Path | None = None) -> list[TestLog]:
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
        print(colored("Test completed!", fg=Fore.GREEN, sty=Style.BRIGHT))
        if save_path:
            print(colored(f"Save logs to {save_path}", fg=Fore.GREEN))
        return logs
