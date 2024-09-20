import re
import shutil
import zipfile
from pathlib import Path

import pandas as pd  # type: ignore

from ..project import Project
from .decom import extractors, support_gbk
from .gather_code import gather_codes

exclude_patterns = [re.compile(s) for s in [r"^~", r"^\.", r"^__", r"x64", r"\.sln", r"\.vcxproj"]]
ignore_patterns = shutil.ignore_patterns("~*", ".*", "__*", ".vs", "x32", "x64", "*.sln", "*.vcxproj*")


def remove_name_prefix(file_name: str, names: list[str]) -> str:
    """Remove prefixes of `file_name` in `names` together with delimiter `_`.

    Args:
        file_name (str): The original name.
        names (list[str]): List of prefixes.

    Returns:
        str: The resulted string.
    """
    for n in names:
        file_name = file_name.removeprefix(n + "_")
    return file_name


def should_include(f: Path) -> bool:
    """Check whether the file can be included in the collection."""
    name = f.name
    return not (any(p.search(name) for p in exclude_patterns))


def auto_extract(file: Path, dest: Path) -> None:
    temp_path = Path(".TEMP")
    shutil.rmtree(temp_path, ignore_errors=True)
    temp_path.mkdir()

    if extractor := extractors.get(file.suffix):
        extractor(file, temp_path)

    # move files from inner
    cur = temp_path
    while len(inc := [f for f in cur.iterdir() if should_include(f)]) == 1:
        f = inc[0]
        if f.is_dir():
            cur = f
        else:
            break
    shutil.copytree(cur, dest, ignore=ignore_patterns, dirs_exist_ok=True)

    file.unlink()
    shutil.rmtree(temp_path)


def try_extract(file: Path, dest: Path) -> bool:
    if file.is_file() and file.suffix in extractors:
        auto_extract(file, dest)
        return True
    return False


def extract_archive(
    archive_path: Path,
    proj: Project,
    *,
    roster_path: Path,
    gather: bool = False,
    remove_existent: bool = True,
) -> None:
    """
    Extracts files from a specified archive and organizes them into project directories.

    This function reads a roster to create directories for each student, extracts relevant files from the provided archive, and processes attachments. It also offers options to gather source codes and manage existing files in the project structure.

    Args:
        archive_path (Path): The path to the archive file to be extracted.
        proj (Project): The project instance that contains the collection and evaluation paths.
        roster_path (Path): The path to the roster file containing student information.
        gather (bool, optional): If True, source codes will be gathered after extraction. Defaults to False.
        remove_existent (bool, optional): If True, existing evaluation directories will be removed before copying. Defaults to True.

    Returns:
        None

    Examples:
        extract_archive(Path('/path/to/archive.zip'), project_instance, roster_path=Path('/path/to/roster.csv'))
    """

    roster = pd.read_table(roster_path)

    proj.init_collect()  # 创建空collect目录

    name_dict = dict[str, Path]()
    for _, row in roster.iterrows():
        one_path = proj.collect_folder / f"{row['学号']}{row['姓名']}"
        one_path.mkdir(exist_ok=True)
        name_dict[row["姓名"]] = one_path
    names = list(name_dict.keys())

    with support_gbk(zipfile.ZipFile(archive_path)) as z:
        print(f"Extracting {archive_path}...")
        nl = z.namelist()
        for n in nl:
            if n.endswith(".rtf"):
                continue
            for k, v in name_dict.items():
                if k in n:
                    z.extract(n, v)

    for p in name_dict.values():
        attach = p / "attach"
        if attach.exists():
            print(f"Processing {p}...")
            for f in attach.iterdir():
                if not try_extract(f, p) and should_include(f):
                    shutil.move(f, p / remove_name_prefix(f.name, names))
            attach.rmdir()

    # 把 collect 内容复制到对应的 eval 下
    print("Copy to eval")
    proj.init_eval(remove_existent=remove_existent)

    # 代码汇总
    if gather:
        print("Gather source codes")
        gather_codes(proj.collect_folder)

    # 暂不支持自动分包

    print("Done!")


def update_eval(proj: Project):
    """
    Updates the evaluation files in the project based on the collected files.

    This function iterates through the collected files and checks if they need to be updated in the evaluation directory. If a file in the collection is newer than its counterpart in the evaluation folder, it copies the updated file to ensure the evaluation is current.

    Args:
        proj (Project): The project instance containing the paths to the collection and evaluation folders.

    Returns:
        None

    Examples:
        update_eval(project_instance)  # Updates the evaluation files based on the collected files.
    """

    for f in proj.collect_folder.rglob("*/*"):
        if not f.is_file():
            continue
        f_cmp = proj.eval_folder / f.relative_to(proj.collect_folder)
        # 如果文件已存在且修改时间不比collect里的早，那么跳过
        if f_cmp.exists() and f.stat().st_mtime_ns <= f_cmp.stat().st_mtime_ns:
            continue
        print("update", f_cmp, f.stat().st_mtime, f_cmp.stat().st_mtime if f_cmp.exists() else "")
        f_cmp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, f_cmp)
