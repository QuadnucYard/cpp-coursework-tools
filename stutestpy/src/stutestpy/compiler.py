from __future__ import annotations

import subprocess
import sys
from abc import abstractmethod
from pathlib import Path
from typing import override

import rich
from more_itertools import flatten
from result import Err, Ok, Result

from . import results as R

console = rich.get_console()


class Compiler:
    @abstractmethod
    def compile(self, source: list[Path], dest: Path, *, includes: list[Path] | None = None) -> Result[Path, R.CE]: ...


class LocalCompiler(Compiler):
    def __init__(self, args: list[str] | None = None) -> None:
        super().__init__()
        self.args = args or [
            "clang++",
            "-std=c++23",
            "-Wall",
            "-Wextra",
            # "-Wpedantic",
            # "-Wconversion",
            "-g",
            "-fsanitize=address,undefined",
            "-fsanitize-address-use-after-scope",
            "-fno-omit-frame-pointer",
        ]

    @override
    def compile(self, sources: list[Path], dest: Path, *, includes: list[Path] | None = None) -> Result[Path, R.CE]:
        console.print(f"Compile: {sources}", style="yellow")
        r = subprocess.run(
            [
                *self.args,
                *sources,
                *(flatten(("-I", i) for i in includes) if includes else []),
                "-o",
                dest,
            ],
            stdout=sys.stdout,
            stderr=sys.stderr,
            # capture_output=True,
        )
        return Err(R.CE()) if r.returncode != 0 else Ok(Path(dest))
