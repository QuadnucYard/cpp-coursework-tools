from __future__ import annotations

import subprocess
import sys
from io import FileIO
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any

from colorama import Fore, Style

from tools.stutestpy.utils import auto_decode, colored

from . import result
from .finder import FindSubmissionByKeywords

if TYPE_CHECKING:
    from .checker import Checker


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
            return auto_decode(stdout)
        except Exception as e:
            raise result.UKE(str(e)) from None

    def check(self, out: str, ans: str) -> None: ...

    def test_one(self, folder: Path) -> result.TestResult | list[result.TestResult]:
        print(colored(f"Test {folder}", fg=Fore.MAGENTA, sty=Style.BRIGHT))
        try:
            src = self.find_submission(folder)
            if not src:
                print(colored("Fail to find submission", fg=Fore.RED))
                return result.MISS()
            exe = self.compile(src)
            results: list[result.TestResult] = []
            for i, tc in enumerate(self.testcases):
                print(colored(f"Case {i}", fg=Fore.LIGHTBLUE_EX, sty=Style.BRIGHT))
                try:
                    out = self.run(tc, exe)
                    results.append(self.checker.check(self, i, self.testcases_str[i], out, self.testans_str[i]))
                except result.UnexpectedResult as e:
                    if isinstance(e, result.INT):
                        print(colored("Interrupt", fg=Fore.LIGHTCYAN_EX))
                        break
                    results.append(e)
                print("  ", colored(str(results[-1]), fg=results[-1].color), sep="")
            exe.unlink()
            return results
        except result.UnexpectedResult as e:
            print(e)
            return e

    def test_many(self, folder: Path) -> list[Any]:
        results = []
        for f in folder.iterdir():
            if f.is_dir() and f.name != "src":
                results.append((f, self.test_one(f)))
        return results
