import re
from abc import abstractmethod
from dataclasses import dataclass

from colorama import Fore
from typing_extensions import override

from .utils import colored


def highlight_matched(s: str, matched: list[tuple[int, int]]) -> str:
    for l, r in reversed(matched):
        s = s[:l] + colored(s[l:r], fg=Fore.CYAN) + s[r:]
    return s


@dataclass
class Match:
    ok: bool
    matched: list[tuple[int, int]]
    match_str: str


class SequenceMatcher:
    @abstractmethod
    def __init__(self, ans: str) -> None: ...

    @abstractmethod
    def __call__(self, output: str) -> Match: ...

    @property
    @abstractmethod
    def num_patterns(self) -> int: ...


class TokenSequenceMatcher(SequenceMatcher):
    @override
    def __init__(self, ans: str) -> None:
        self.matchers = [
            (i, t, re.compile(re.sub(r"(\\ )+", r"\\s*", re.escape(t)), re.I))
            for i, t in enumerate(re.split(r"[\t\n]", ans))
        ]

    @override
    def __call__(self, output: str) -> Match:
        ok = True
        last_pos = 0
        matched: list[tuple[int, int]] = []
        for idx, tok, pat in self.matchers:
            m = pat.search(output, last_pos)
            if not m:
                print(colored(f"Fail to match the {idx}-th token:", fg=Fore.RED), tok)
                ok = False
                continue
            matched.append(m.span())
            last_pos = m.span()[1]
        return Match(ok, matched, highlight_matched(output, matched))

        # todo 动态规划找最优匹配

    @property
    @override
    def num_patterns(self) -> int:
        return len(self.matchers)


class LineSequenceMatcher(SequenceMatcher):
    """行序列匹配"""

    @override
    def __init__(self, ans: str) -> None:
        self.matchers = [(l, re.compile(re.sub(r"(\\ |\\t)+", r"\\s*", re.escape(l)))) for l in ans.splitlines()]

    @override
    def __call__(self, output: str) -> Match:
        ok = True
        last_pos = 0
        matched: list[tuple[int, int]] = []
        for i, (line, pat) in enumerate(self.matchers):
            m = pat.search(output, last_pos)
            if not m:
                print(colored(f"Fail to match the {i}-th line:", fg=Fore.RED), line)
                ok = False
                continue
            matched.append(m.span())
            last_pos = m.span()[1]
        return Match(ok, matched, highlight_matched(output, matched))

    @property
    @override
    def num_patterns(self) -> int:
        return len(self.matchers)
