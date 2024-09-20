import shutil
from pathlib import Path


class Project:
    collection: Path
    path: Path
    name: str

    def __init__(self, collection: Path, name: str) -> None:
        self.collection = collection
        self.path = collection / name
        self.name = name

        self.collect_folder = self.path / "collect"
        self.eval_folder = self.path / "eval"
        self.logs_folder = self.path / "logs"
        self.mails_folder = self.path / "mails"

    def init_collect(self) -> None:
        shutil.rmtree(self.collect_folder, ignore_errors=True)  # 强行删除原有目录
        self.collect_folder.mkdir(parents=True, exist_ok=True)
        print("Create collect directory")

    def init_eval(self, *, remove_existent: bool = True):
        if self.eval_folder.exists():
            if remove_existent:
                shutil.rmtree(self.eval_folder)
                print("Remove existent eval dir")
            else:
                print("Overwrite existent eval dir")
        shutil.copytree(self.collect_folder, self.eval_folder, dirs_exist_ok=True)
