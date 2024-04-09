import re


def tint_raw_block(html_text: str) -> str:
    html_text = re.sub(r"(^@@.+@@$)", r'<div class="line-loc">\1</div>', html_text, flags=re.M)
    html_text = re.sub(r"(^\+[^+].*?\n)", r'<div class="line-add">\1</div>', html_text, flags=re.M)
    html_text = re.sub(r"(^\-[^-].*?\n)", r'<div class="line-del">\1</div>', html_text, flags=re.M)
    html_text = re.sub(r"(// *!.*)", r'<span class="cmt-alert">\1</span>', html_text)
    html_text = re.sub(r"(// *\?.*)", r'<span class="cmt-query">\1</span>', html_text)
    html_text = re.sub(r"(// *\*.*)", r'<span class="cmt-emph">\1</span>', html_text)
    return html_text
