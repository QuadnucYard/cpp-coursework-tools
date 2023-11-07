from pathlib import Path
import shutil
import zipfile
import pandas as pd
import py7zr
import rarfile
import typer

app = typer.Typer()

roster = pd.read_table("roster.tsv")


def zip_dir(dirpath: Path, outFullName: Path):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    with zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED) as zip:
        for fpath in dirpath.glob("*"):
            zip.write(fpath, fpath)


def should_include(f: Path):
    return not (f.name.startswith("~") or f.name.startswith(".") or f.name.startswith("__"))


def try_decode(str: str):
    try:
        string = str.encode("cp437").decode("utf-8")
    except:
        string = str.encode("cp437").decode("gbk")
    return string


def support_gbk(zip_file: zipfile.ZipFile):
    name_to_info = zip_file.NameToInfo
    # copy map first
    for name, info in name_to_info.copy().items():
        try:
            real_name = try_decode(name)
            if real_name != name:
                info.filename = real_name
                del name_to_info[name]
                name_to_info[real_name] = info
        except:
            ...
    return zip_file


def auto_extract_rar(file: Path, dest: Path):
    with rarfile.RarFile(file) as rar:
        rar.extractall(dest)


def auto_extract_zip(file: Path, dest: Path):
    with support_gbk(zipfile.ZipFile(file)) as zip:
        zip.extractall(dest)


def auto_extract_7z(file: Path, dest: Path):
    with py7zr.SevenZipFile(file) as fp:
        fp.extractall(dest)


extractors = {".rar": auto_extract_rar, ".zip": auto_extract_zip, ".7z": auto_extract_7z}


def auto_extract(file: Path, dest: Path):
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


@app.command()
def main(path: str, dest: str):
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    name_dict = dict[str, Path]()
    for idx, row in roster.iterrows():
        one_path = dest_path / f"{row['学号']}{row['姓名']}"
        one_path.mkdir(exist_ok=True)
        name_dict[row["姓名"]] = one_path

    with support_gbk(zipfile.ZipFile(path)) as z:
        print(f"Extracting {path}...")
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

    # part1, part2 = divide(2, name_dict.values())
    # with zipfile.ZipFile('test.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    #     z.write()


if __name__ == "__main__":
    app()
