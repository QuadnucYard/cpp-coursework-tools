import filecmp
from pathlib import Path

import pandas as pd
import typer
from colorama import Fore
from jinja2 import Template
from markdown import markdown

from .emailer import Emailer

app = typer.Typer()


def get_different_files(source: Path, base: Path):
    base_files = {f.relative_to(base): f for f in base.glob("*.*")}
    for f in source.glob("*.*"):
        f_rel = f.relative_to(source)
        if f_rel in base_files and not filecmp.cmp(base_files[f_rel], f):
            yield f


email_template = Template(Path("mail/email_template.jinja").read_text(encoding="utf-8"))


@app.command()
def main(result_path: str, subject: str, *, collect_path: str):
    folder = Path(result_path)
    collect_folder = Path(collect_path)
    df = pd.read_excel(folder / "eval.xlsx")

    i1 = df.columns.to_list().index("性别") + 1
    i2 = df.columns.to_list().index("基础分")

    with Emailer() as emailer:
        for idx, row in df.iterrows():
            folder_name = f"{row['学号']}{row['姓名']}"
            receiver = f"{row['一卡通号']}@seu.edu.cn"
            main_score = f"评分：{row['分数']} = {row['基础分']} + {row['附加分']}" if "附加分" in row else f"评分：{row['基础分']}"
            # 附件
            att = list(get_different_files(folder / folder_name, collect_folder / folder_name))
            # 设置内容
            content = email_template.render(
                main_score=main_score,
                scores=row[i1:i2].to_dict(),
                remarks=markdown(str(row["评语"]).replace("\n", "  \n")),
                attach=len(att) > 0,
            )
            # 调试输出
            print(Fore.YELLOW, idx, end="")
            print(Fore.BLUE, folder_name, end="")
            print(Fore.GREEN, "send to", receiver, f"{subject} - 作业反馈")
            print(Fore.RESET, main_score)
            print(Fore.CYAN, att)
            print(Fore.RESET, end="")
            # 发送邮件
            mail = emailer.launch().subject(f"{subject} - 作业反馈").html(content)
            mail.attach_many(att)
            mail.send(receiver)


if __name__ == "__main__":
    app()
