import shutil
import zipfile
from pathlib import Path

import pandas as pd  # type: ignore
import py7zr
import rarfile  # type: ignore

from .gather_code import gather_codes


def zip_dir(dirpath: Path, outFullName: Path) -> None:
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    with zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED) as zip:
        for fpath in dirpath.glob("*"):
            zip.write(fpath, fpath)


def should_include(f: Path) -> bool:
    return not (f.name.startswith("~") or f.name.startswith(".") or f.name.startswith("__"))


def try_decode(str: str) -> str:
    try:
        string = str.encode("cp437").decode("utf-8")
    except Exception as _:
        string = str.encode("cp437").decode("gbk")
    return string


def support_gbk(zip_file: zipfile.ZipFile) -> zipfile.ZipFile:
    name_to_info = zip_file.NameToInfo
    # copy map first
    for name, info in name_to_info.copy().items():
        try:
            real_name = try_decode(name)
            if real_name != name:
                info.filename = real_name
                del name_to_info[name]
                name_to_info[real_name] = info
        except Exception as _:
            ...
    return zip_file


def auto_extract_rar(file: Path, dest: Path) -> None:
    with rarfile.RarFile(file) as rar:
        rar.extractall(dest)


def auto_extract_zip(file: Path, dest: Path) -> None:
    with support_gbk(zipfile.ZipFile(file)) as zip:
        zip.extractall(dest)


def auto_extract_7z(file: Path, dest: Path) -> None:
    with py7zr.SevenZipFile(file) as fp:
        fp.extractall(dest)


extractors = {".rar": auto_extract_rar, ".zip": auto_extract_zip, ".7z": auto_extract_7z}


def auto_extract(file: Path, dest: Path) -> None:
    temp_path = Path(".TEMP")
    shutil.rmtree(temp_path, ignore_errors=True)
    temp_path.mkdir()

    if extractor := extractors.get(file.suffix, None):
        extractor(file, temp_path)

    # move files from inner
    cur = temp_path
    while len(inc := [f for f in cur.iterdir() if should_include(f)]) == 1:
        f = inc[0]
        if f.is_dir():
            cur = f
        else:
            break
    for f in cur.iterdir():
        if should_include(f):
            shutil.move(f, dest / f.name)

    file.unlink()
    shutil.rmtree(temp_path)


def extract_archive(src_path: Path, dest_name: str, roster_path: Path, gather: bool = False) -> None:
    roster = pd.read_table(roster_path)

    dest_path = Path(".") / "collect" / dest_name
    dest_path.mkdir(parents=True, exist_ok=True)

    name_dict = dict[str, Path]()
    for _, row in roster.iterrows():
        one_path = dest_path / f"{row['学号']}{row['姓名']}"
        one_path.mkdir(exist_ok=True)
        name_dict[row["姓名"]] = one_path

    with support_gbk(zipfile.ZipFile(src_path)) as z:
        print(f"Extracting {src_path}...")
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
                if f.is_file() and f.suffix in extractors:
                    auto_extract(f, p)
                elif should_include(f):
                    shutil.move(f, p / f.name)
            attach.rmdir()

    # 把 collect 内容复制到对应的 eval 下
    shutil.copytree(dest_path, Path(".") / "eval" / dest_name)

    # 代码汇总
    if gather:
        gather_codes(dest_path)

    # 暂不支持自动分包

    print("Done!")
