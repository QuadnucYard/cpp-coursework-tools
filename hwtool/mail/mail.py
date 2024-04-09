import html
from pathlib import Path

import pandas as pd
import premailer
from jinja2 import Template
from markdown import markdown
from rich.console import Console

from .differ import get_all_differences, get_different_files
from .emailer import Emailer, settings
from .tinter import tint_raw_block

console = Console()

email_template = Template((Path(__file__).parent / "email_template.jinja").read_text(encoding="utf-8"))

roster = pd.read_table(Path(__file__).parents[1] / "data" / "roster-2.tsv")


def send_emails(
    folder: str, subject: str, *, preview: bool = False, send_self: bool = False, qq_only: bool = False
) -> None:
    collect_folder = Path(".") / "collect" / folder
    eval_folder = Path(".") / "eval" / folder

    df = pd.read_excel(eval_folder / "eval.xlsx")

    i1 = df.columns.to_list().index("性别") + 1
    i2 = df.columns.to_list().index("基础分")

    log_path = Path(".") / "logs" / "mail" / folder
    log_path.mkdir(parents=True, exist_ok=True)

    subject = f"{subject} - 作业反馈"  # 加个后缀

    console.log(f"[b i magenta]Send emails to {len(df)} students! :rocket:")

    with Emailer() as emailer:
        for idx, row in df.iterrows():
            folder_name = f"{row['学号']}{row['姓名']}"
            if qq_only:
                qq = roster[roster["学号"] == row["学号"]].iloc[0]["qq"]
                if not qq or pd.isna(qq):
                    continue
                receiver = f"{int(qq)}@qq.com"  # 读到的是浮点数
            else:
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
                scores={k: f"{v:.1f}" for k, v in row[i1:i2].to_dict().items()},
                remarks=markdown(str(row["评语"]).replace("\n", "  \n")),
                diff=[tint_raw_block(html.escape("\n".join(a))) for a in diff.values()],
                attach=len(att) > 0,
            )
            content = premailer.transform(content)  # css处理
            (log_path / f"{idx:02}-{row['学号']}.html").write_text(content, "utf-8")
            # 调试输出
            console.print(f"[yellow]{idx} [blue]{folder_name}", end=" ")
            console.print(f"[green]send to {receiver}: {subject}")
            console.print(main_score)
            console.print(f"[cyan]{att}")
            # 发送邮件
            if preview:  # 预览模式不发送邮件
                continue
            mail = emailer.launch().subject(f"{subject}").html(content)
            mail.attach_many(att)
            if send_self:  # 如果发给自己，发一个就结束
                mail.send(settings.SMTP_USER)
                console.log("[b red]Self send break")
                break
            mail.send(receiver)
    console.log("[b i green]Complete! :star2:")
