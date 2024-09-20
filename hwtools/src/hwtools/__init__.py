from pathlib import Path
from typing import Annotated

import typer

from . import extract as ext
from .mail.mail import send_emails
from .project import Project

app = typer.Typer()


@app.command()
def extract(
    path: str,
    collection: Annotated[Path, typer.Option()],
    proj: Annotated[str, typer.Option()],
    roster: Annotated[Path, typer.Option()],
) -> None:
    ext.extract_archive(Path(path), Project(collection, proj), roster_path=Path(roster))


@app.command()
def gather(path: Path) -> None:
    ext.gather_codes(Path(path))


@app.command()
def update_eval(
    collection: Annotated[Path, typer.Option()],
    proj: Annotated[str, typer.Option()],
) -> None:
    ext.update_eval(Project(collection, proj))


@app.command()
def mail(
    collection: Annotated[Path, typer.Option()],
    proj: Annotated[str, typer.Option()],
    roster: Annotated[Path, typer.Option()],
    subject: Annotated[str, typer.Option()],
    preview: bool = False,
    send_self: bool = False,
    qq_only: bool = False,
) -> None:
    send_emails(
        Project(collection, proj),
        roster_path=roster,
        mail_subject=subject,
        preview=preview,
        send_self=send_self,
        qq_only=qq_only,
    )


@app.command(deprecated=True)
def review() -> None: ...


def main() -> int:
    app()
    return 0
