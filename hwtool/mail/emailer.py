from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
from smtplib import SMTP_SSL
from typing import Any, Iterable

from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "@qq.com"
    SMTP_PASSWORD: str = ""  # 授权码
    SENDER: str = SMTP_USER
    SENDER_NAME: str | None = None


settings = EmailSettings()


class EmailSender:
    def __init__(self, smtp: SMTP_SSL) -> None:
        self.message = MIMEMultipart()
        self.message["From"] = formataddr(pair=(settings.SENDER_NAME, settings.SENDER))
        self.smtp = smtp

    def subject(self, title: str):
        self.message["Subject"] = Header(title, "utf-8")
        return self

    def content(self, content: str):
        self.message.attach(MIMEText(content, "plain", "utf-8"))
        return self

    def html(self, content: str):
        self.message.attach(MIMEText(content, "html", "utf-8"))
        return self

    def attach(self, path_: Any, rename: str | None = None):
        path = Path(path_)
        att = MIMEText(path.read_bytes(), "base64", "utf-8")  # type: ignore
        att.set_type("application/octet-stream")
        att.add_header("Content-Disposition", "attachment", filename=rename or path.name)
        self.message.attach(att)
        return self

    def attach_many(self, paths: Iterable[Any]):
        for path in paths:
            self.attach(path)

    def send(self, *receivers: str):
        self.message["To"] = ",".join(receivers)
        try:
            err = self.smtp.sendmail(settings.SMTP_USER, receivers, self.message.as_string())
            print("邮件发送成功")
            if err:
                print(err)
        except Exception as e:
            print("邮件发送失败")
            print(e)
        return


class Emailer:
    def __init__(self) -> None:
        self.smtp = SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        self.smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

    def launch(self) -> EmailSender:
        return EmailSender(self.smtp)

    def close(self):
        self.smtp.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
