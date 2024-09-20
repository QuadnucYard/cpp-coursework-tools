import html
from pathlib import Path

import pandas as pd
import premailer
from jinja2 import Template
from markdown import markdown
from rich.console import Console

from ..project import Project
from .differ import get_all_differences, get_different_files
from .emailer import Emailer, settings
from .tinter import tint_raw_block

console = Console()

email_template = Template((Path(__file__).with_name("email_template.jinja")).read_text(encoding="utf-8"))


def send_emails(
    proj: Project,
    *,
    roster_path: Path,
    mail_subject: str,
    eval_name: str = "eval.xlsx",
    preview: bool = False,
    send_self: bool = False,
    qq_only: bool = False,
) -> None:
    """
    Send emails to students with their evaluation feedback and attachments.

    This function reads a roster and evaluation data, constructs email content,
    and sends emails to students based on their scores.
    It can operate in preview mode, allowing for content review without sending emails,
    and can also send a copy to the sender.

    Args:
        proj (Project): The project instance that contains the collection and evaluation paths.
        roster_path (Path): The path to the roster file.
        mail_subject (str): The subject line for the email.
        eval_name (str, optional): The name of the evaluation file. Defaults to "eval.xlsx".
        preview (bool, optional): If True, emails will not be sent, only previewed. Defaults to False.
        send_self (bool, optional): If True, a copy of the email will be sent to the sender. Defaults to False.
        qq_only (bool, optional): If True, only QQ email addresses will be used. Defaults to False.

    Returns:
        None

    Examples:
        send_emails(Path('/path/to/collection'), 'Project1', roster_path=Path('/path/to/roster.tsv'), mail_subject='Feedback')
    """

    roster = pd.read_table(roster_path)

    df = pd.read_excel(proj.eval_folder / eval_name)

    i1 = df.columns.to_list().index("性别") + 1
    i2 = df.columns.to_list().index("基础分")

    proj.mails_folder.mkdir(parents=True, exist_ok=True)

    mail_subject = f"{mail_subject} - 作业反馈"  # 加个后缀

    console.log(f"[b i magenta]Send emails to {len(df)} students! :rocket:")

    with Emailer() as emailer:
        for idx, row in df.iterrows():
            # 跳过没有分数的
            if row["分数"] == 0.0:
                continue

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
            diff = get_all_differences(proj.eval_folder / folder_name, proj.collect_folder / folder_name)
            # 附件
            att = list(get_different_files(proj.eval_folder / folder_name, proj.collect_folder / folder_name))
            # 设置内容
            content = email_template.render(
                main_score=main_score,
                scores={k: f"{v:.1f}" for k, v in row[i1:i2].to_dict().items()},
                remarks=markdown(str(row["评语"]).replace("\n", "  \n")),
                diff=[tint_raw_block(html.escape("\n".join(a))) for a in diff.values()],
                attach=len(att) > 0,
            )
            content = premailer.transform(content)  # css处理
            (proj.mails_folder / f"{idx:02}-{row['学号']}.html").write_text(content, "utf-8")
            # 调试输出
            console.print(f"[yellow]{idx} [blue]{folder_name}", end=" ")
            console.print(f"[green]send to {receiver}: {mail_subject}")
            console.print(main_score)
            console.print(f"[cyan]{att}")
            # 发送邮件
            if preview:  # 预览模式不发送邮件
                continue
            mail = emailer.launch().subject(f"{mail_subject}").html(content)
            mail.attach_many(att)
            if send_self:  # 如果发给自己，发一个就结束
                mail.send(settings.SMTP_USER)
                console.log("[b red]Self send break")
                break
            mail.send(receiver)
    console.log("[b i green]Complete! :star2:")
