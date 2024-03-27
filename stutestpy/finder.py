from abc import abstractmethod
from pathlib import Path

from typing_extensions import override


class SubmissionFinder:
    @abstractmethod
    def find_submission(self, folder: Path) -> Path | None: ...


class FindSubmissionByKeywords(SubmissionFinder):

    def __init__(self, keywords: list[str]) -> None:
        self.keywords = keywords

    @override
    def find_submission(self, folder: Path) -> Path | None:
        for k in self.keywords:
            for f in folder.glob("**/*.cpp"):
                if f.is_file() and f.suffix == ".cpp" and k in f.name:
                    return f
        return None
