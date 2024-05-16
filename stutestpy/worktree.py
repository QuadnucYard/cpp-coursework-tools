from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias

from result import Result

from . import results as R

if TYPE_CHECKING:
    from .compiler import Compiler
    from .finder import SubmissionFinder

StrPath: TypeAlias = str | Path


class WorkTree:
    def __init__(self, tmp_path: StrPath, loaders: list[SubmissionFinder] | None = None) -> None:
        self.tmp_path = Path(tmp_path)
        self.root = self.tmp_path
        self.loaders = loaders or []
        self.fixed_files: list[Path] = []
        self.files: list[Path] = []

    def add_fixed(self, file: StrPath):
        self.fixed_files.append(Path(file))
        self.files.append(Path(file))

    def add_file(self, file: StrPath):
        self.files.append(Path(file))

    def reset(self):
        self.files = self.fixed_files.copy()

    def clear(self):
        self.files.clear()
        self.fixed_files.clear()

    def set_root(self, root: StrPath) -> bool:
        self.root = Path(root)
        self.reset()

        for loader in self.loaders:
            sub = loader.find_submission(self.root)
            if not sub:
                return False
            self.add_file(sub)
        return True

    @property
    def sources(self):
        return [f for f in self.files if f.suffix in (".c", ".cc", ".cpp")]

    def compile_with(
        self,
        compiler: Compiler,
    ) -> Result[Path, R.CE]:
        sources = self.sources
        return compiler.compile(sources, self.tmp_path / "example.exe", includes=[self.root])
