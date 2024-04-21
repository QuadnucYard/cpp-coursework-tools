from pathlib import Path
from typing import Annotated

import typer

from . import extract as ext
from .mail.mail import send_emails

app = typer.Typer()


@app.command()
def extract(path: str, dest_name: str, roster: Annotated[str, typer.Option()]) -> None:
    ext.extract_archive(Path(path), dest_name, Path(roster))


@app.command()
def gather(path: str) -> None:
    ext.gather_codes(Path(path))


@app.command()
def update_eval(name: str) -> None:
    ext.update_eval(name)


@app.command()
def mail(folder: str, subject: str, preview: bool = False, send_self: bool = False, qq_only: bool = False) -> None:
    send_emails(folder, subject, preview=preview, send_self=send_self, qq_only=qq_only)


@app.command()
def review() -> None: ...


if __name__ == "__main__":
    app()
