from __future__ import annotations

import subprocess
import sys
from abc import abstractmethod
from pathlib import Path
from typing import TypeAlias

import rich
from more_itertools import flatten
from result import Err, Ok, Result

from . import results as R

StrPath: TypeAlias = str | Path

console = rich.get_console()


class Compiler:
    @abstractmethod
    def compile(
        self, source: list[StrPath], dest: StrPath, *, includes: list[StrPath] | None = None
    ) -> Result[Path, R.CE]: ...


class LocalCompiler(Compiler):
    def compile(
        self, sources: list[StrPath], dest: StrPath, *, includes: list[StrPath] | None = None
    ) -> Result[Path, R.CE]:
        console.print(f"Compile: {sources}", style="yellow")
        r = subprocess.run(
            [
                # "g++",
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
                *sources,
                *(flatten(("-I", i) for i in includes) if includes else []),
                "-o",
                dest,
            ],
            stdout=sys.stdout,
            stderr=sys.stderr,
            # capture_output=True,
        )
        if r.returncode != 0:
            # print(auto_decode(r.stderr))
            return Err(R.CE())
        return Ok(Path(dest))
