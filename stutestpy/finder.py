from abc import abstractmethod
from pathlib import Path
from typing import override


class SubmissionFinder:
    @abstractmethod
    def find_submission(self, folder: Path) -> Path | None: ...


class FindSubmissionByKeywords(SubmissionFinder):

    def __init__(self, keywords: list[str]) -> None:
        self.keywords = keywords

    @override
    def find_submission(self, folder: Path) -> Path | None:
        # 按照关键词顺序匹配
        for k in self.keywords:
            for f in folder.glob("**/*.cpp"):
                if f.is_file() and f.suffix == ".cpp" and k in f.name:
                    return f
        return None


class FindHeader(SubmissionFinder):

    def __init__(self, header: str) -> None:
        self.header = header

    @override
    def find_submission(self, folder: Path) -> Path | None:
        # 严格匹配头文件名
        f = folder / self.header
        if f.exists() and f.is_file():
            return f
        return None
