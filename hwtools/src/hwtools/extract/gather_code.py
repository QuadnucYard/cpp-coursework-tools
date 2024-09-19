import shutil
from pathlib import Path


def gather_codes(root: Path) -> None:
    src = root / "src"
    src.mkdir(exist_ok=True)

    suffixes = (".cpp", ".cc", ".h", ".hpp")

    for item in root.iterdir():
        if not item.is_dir() or item.name == "src":
            continue
        for f in item.iterdir():
            if f.suffix in suffixes:
                print("gather", f)
                shutil.copyfile(f, src / f"{item.name}-{f.name}")
