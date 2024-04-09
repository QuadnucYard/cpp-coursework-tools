import difflib
import filecmp
from collections.abc import Iterable
from pathlib import Path


def get_different_pairs(source: Path, base: Path) -> Iterable[tuple[Path, Path]]:
    base_files = {f.relative_to(base): f for f in base.rglob("*.*")}
    for f in source.rglob("*.*"):
        if not f.is_file():
            continue
        f_rel = f.relative_to(source)
        if f_rel in base_files and not filecmp.cmp(base_files[f_rel], f):
            yield f, base_files[f_rel]  # source and base


def get_different_files(source: Path, base: Path) -> Iterable[Path]:
    return (a for a, _ in get_different_pairs(source, base))


def auto_decode(bytes: bytes) -> str:
    try:
        return bytes.decode("utf-8")
    except Exception as _:
        try:
            return bytes.decode("gbk")
        except Exception as _:
            return bytes.decode("utf-16")


def get_file_lines(f: Path) -> list[str]:
    a = [s.rstrip() for s in auto_decode(f.read_bytes()).splitlines()]
    while len(a) > 0 and a[-1] == "":
        a.pop()
    return a


def get_single_differences(fa: Path, fb: Path) -> list[str]:
    s1 = get_file_lines(fa)
    s2 = get_file_lines(fb)
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


source_suffixes = (".cpp", ".cc", ".h", ".hpp", ".txt", ".md")


def get_all_differences(source: Path, base: Path) -> dict[Path, list[str]]:
    return {
        a: get_single_differences(b, a) for a, b in get_different_pairs(source, base) if a.suffix in source_suffixes
    }
