from __future__ import annotations

import shutil
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, override

from result import Result

from . import results as R

if TYPE_CHECKING:
    from .compiler import Compiler
    from .finder import SubmissionFinder

type StrPath = str | Path


class TreeLoader:
    @abstractmethod
    def load_to(self, worktree: WorkTree) -> bool: ...

    def unload(self, worktree: WorkTree) -> None: ...


class FixedLoader(TreeLoader):
    def __init__(self, loaders: list[SubmissionFinder] | None = None) -> None:
        self.loaders = loaders or []

    @override
    def load_to(self, worktree: WorkTree) -> bool:
        for loader in self.loaders:
            sub = loader.find_submission(worktree.root)
            if not sub:
                return False
            worktree.add_file(sub)
        return True


class EnsuredLoader(TreeLoader):
    def __init__(self, ensures: list[tuple[str, StrPath]] | None = None) -> None:
        self.ensures = ensures or []

    @override
    def load_to(self, worktree: WorkTree) -> bool:
        for name, alt in self.ensures:
            f = worktree.root / name
            if not f.exists():
                if f.suffix not in (".h", ".hpp"):
                    f = f.with_stem(f.stem + "-cp")
                shutil.copyfile(alt, f)
            worktree.add_file(f)
        return True


class ConditionalLoader(TreeLoader):
    def __init__(self, cond_main: str, alt: StrPath, alt_requires: list[str] | None = None) -> None:
        # 暂时只支持单个文件
        self.cond_main = cond_main
        self.alt = Path(alt)
        self.alt_requires = alt_requires or []

        self.extras: list[Path] = []

    @override
    def load_to(self, worktree: WorkTree) -> bool:
        if (f := worktree.root / self.cond_main).exists():
            worktree.add_file(f)
        elif all((worktree.root / a).exists() for a in self.alt_requires):
            copied = worktree.root / self.alt.name
            copied = copied.with_stem(copied.stem + "-cp")
            copied = shutil.copyfile(self.alt, copied)
            worktree.add_file(copied)
            self.extras.append(copied)
        else:
            return False
        return True

    @override
    def unload(self, worktree: WorkTree) -> None:
        # for f in self.extras:
        #     f.unlink(missing_ok=True)
        self.extras.clear()


class WorkTree:
    def __init__(self, tmp_path: StrPath, loader: TreeLoader, fixtures: list[StrPath] | None = None) -> None:
        self.tmp_path = Path(tmp_path)
        self.root = self.tmp_path
        self.loader = loader
        self.fixed_files: list[Path] = []
        self.files: list[Path] = []
        if fixtures:
            for f in fixtures:
                self.add_fixed(f)

    def add_fixed(self, file: StrPath) -> None:
        self.fixed_files.append(Path(file))
        self.files.append(Path(file))

    def add_file(self, file: StrPath) -> None:
        self.files.append(Path(file))

    def reset(self) -> None:
        self.files = self.fixed_files.copy()

    def clear(self) -> None:
        self.files.clear()
        self.fixed_files.clear()

    def set_root(self, root: StrPath) -> bool:
        self.root = Path(root)
        self.reset()
        return self.loader.load_to(self)

    @property
    def sources(self) -> list[Path]:
        return [f for f in self.files if f.suffix in (".c", ".cc", ".cpp")]

    def compile_with(
        self,
        compiler: Compiler,
    ) -> Result[Path, R.CE]:
        sources = self.sources
        return compiler.compile(sources, self.tmp_path / "example.exe", includes=[self.root])

    def finish(self) -> None:
        self.loader.unload(self)
