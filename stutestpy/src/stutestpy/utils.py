from colorama import Back, Fore, Style


def auto_decode(bytes: bytes) -> str:
    try:
        return bytes.decode()
    except Exception as _:
        return bytes.decode("gbk")


def colored(s: str, *, fg: str | None = None, bg: str | None = None, sty: str | None = None) -> str:
    if fg:
        s = f"{fg}{s}{Fore.RESET}"
    if bg:
        s = f"{bg}{s}{Back.RESET}"
    if sty:
        s = f"{sty}{s}{Style.RESET_ALL}"
    return s


def trunc_lines(s: str, limit: int, ell: str = "...") -> str:
    lines = s.splitlines()
    return s if len(lines) <= limit else "\n".join(lines[:limit]) + "\n" + ell
