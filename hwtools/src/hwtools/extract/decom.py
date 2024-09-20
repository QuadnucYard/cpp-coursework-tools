import zipfile
from pathlib import Path

import py7zr
import rarfile  # type: ignore


def try_decode(str: str) -> str:
    """Try to decode a file name in archive."""
    try:
        string = str.encode("cp437").decode("utf-8")
    except Exception as _:
        string = str.encode("cp437").decode("gbk")
    return string


def support_gbk(zip_file: zipfile.ZipFile) -> zipfile.ZipFile:
    """Make a zip file work well with GBK encoding."""
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
