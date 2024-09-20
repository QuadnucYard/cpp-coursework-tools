import shutil
from pathlib import Path


def gather_codes(root: Path) -> None:
    """
    Gathers source code files from project directories into a centralized source folder.

    This function creates a 'src' directory within the specified root path and collects all relevant source code files with specific suffixes from subdirectories. The gathered files are renamed to include their original directory name, facilitating organization and access.

    Args:
        root (Path): The root directory containing project subdirectories with source code files.

    Returns:
        None

    Examples:
        gather_codes(Path('/path/to/project'))  # Gathers source code files into the 'src' directory.
    """

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
