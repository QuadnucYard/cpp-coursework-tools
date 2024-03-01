from pathlib import Path

import typer
from typing_extensions import Annotated

from scripts.mail.mail import send_emails

from .extract.extract import extract_archive
from .extract.gather_code import gather_codes

app = typer.Typer()


@app.command()
def extract(path: str, dest_name: str, roster: Annotated[str, typer.Option()]) -> None:
    extract_archive(Path(path), dest_name, Path(roster))


@app.command()
def gather(path: str) -> None:
    gather_codes(Path(path))


@app.command()
def mail(folder: str, subject: str, preview: bool = False, send_self: bool = False) -> None:
    send_emails(folder, subject, preview=preview, send_self=send_self)


@app.command()
def review() -> None: ...


if __name__ == "__main__":
    app()
