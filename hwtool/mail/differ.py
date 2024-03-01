import difflib
import filecmp
from pathlib import Path
from typing import Iterable


def get_different_pairs(source: Path, base: Path) -> Iterable[tuple[Path, Path]]:
    base_files = {f.relative_to(base): f for f in base.glob("*.*")}
    for f in source.glob("*.*"):
        f_rel = f.relative_to(source)
        if f_rel in base_files and not filecmp.cmp(base_files[f_rel], f):
            yield f, base_files[f_rel]  # source and base


def get_different_files(source: Path, base: Path) -> Iterable[Path]:
    return (a for a, _ in get_different_pairs(source, base))


def auto_decode(bytes: bytes) -> str:
    try:
        return bytes.decode()
    except Exception as _:
        return bytes.decode("gbk")


# difflib.context_diff()()


def get_single_differences(fa: Path, fb: Path) -> list[str]:
    s1 = auto_decode(fa.read_bytes()).splitlines()
    s2 = auto_decode(fb.read_bytes()).splitlines()
    return list(difflib.unified_diff(s1, s2, fa.name, fb.name))
    # diff = list(difflib.ndiff(s1, s2))
    # diff_groups: list[list[str]] = []
    # g: list[str] = []
    # for l in diff:
    #     if l.startswith("+ ") or l.startswith("- "):
    #         g.append(l)
    #     elif g:
    #         diff_groups.append(g)
    #         g = []
    # if g:
    #     diff_groups.append(g)
    # return diff_groups


source_suffixes = (".cpp", ".cc", ".h", ".hpp")


def get_all_differences(source: Path, base: Path) -> dict[Path, list[str]]:
    return {
        a: get_single_differences(b, a) for a, b in get_different_pairs(source, base) if a.suffix in source_suffixes
    }
