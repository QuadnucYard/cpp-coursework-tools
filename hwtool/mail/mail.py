import html
from pathlib import Path

import pandas as pd
from colorama import Fore
from jinja2 import Template
from markdown import markdown

from .differ import get_all_differences, get_different_files
from .emailer import Emailer, settings

email_template = Template((Path(__file__).parent / "email_template.jinja").read_text(encoding="utf-8"))


def send_emails(folder: str, subject: str, *, preview: bool = False, send_self: bool = False) -> None:
    collect_folder = Path(".") / "collect" / folder
    eval_folder = Path(".") / "eval" / folder

    df = pd.read_excel(eval_folder / "eval.xlsx")

    i1 = df.columns.to_list().index("性别") + 1
    i2 = df.columns.to_list().index("基础分")

    with Emailer() as emailer:
        for idx, row in df.iterrows():
            folder_name = f"{row['学号']}{row['姓名']}"
            receiver = f"{row['一卡通号']}@seu.edu.cn"
            main_score = (
                f"评分：{row['分数']:.1f} = {row['基础分']:.1f} + {row['附加分']:.1f}"
                if "附加分" in row
                else f"评分：{row['基础分']:.1f}"
            )
            diff = get_all_differences(eval_folder / folder_name, collect_folder / folder_name)
            # 附件
            att = list(get_different_files(eval_folder / folder_name, collect_folder / folder_name))
            # 设置内容
            content = email_template.render(
                main_score=main_score,
                scores=row[i1:i2].to_dict(),
                remarks=markdown(str(row["评语"]).replace("\n", "  \n")),
                diff=[html.escape("\n".join(a)) for a in diff.values()],
                attach=len(att) > 0,
            )
            (Path("logs") / f"mail-{idx}.html").write_text(content, "utf-8")
            # 调试输出
            print(Fore.YELLOW, idx, end="")
            print(Fore.BLUE, folder_name, end="")
            print(Fore.GREEN, "send to", receiver, f"{subject} - 作业反馈")
            print(Fore.RESET, main_score)
            print(Fore.CYAN, att)
            print(Fore.RESET, end="")
            # 发送邮件
            if preview:  # 预览模式不发送邮件
                continue
            mail = emailer.launch().subject(f"{subject} - 作业反馈").html(content)
            mail.attach_many(att)
            if send_self:  # 如果发给自己，发一个就结束
                mail.send(settings.SMTP_USER)
                break
            mail.send(receiver)
