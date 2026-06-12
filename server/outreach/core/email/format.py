import html
import os
import re


def _branding() -> dict[str, str]:
    sender = (os.environ.get("GMAIL_SENDER") or "").strip()
    return {
        "sender_name": (os.environ.get("GMAIL_SENDER_NAME") or "").strip() or sender.split("@")[0],
        "company_name": (os.environ.get("COMPANY_NAME") or "").strip(),
        "company_description": (os.environ.get("COMPANY_DESCRIPTION") or "").strip(),
    }


def normalize_body(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"(?<=[.!?])(?=[A-Z])", " ", text)
    text = re.sub(r" +", " ", text)
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


def _build_footer(*, calendly_link: str = "") -> tuple[str, str]:
    brand = _branding()
    lines = []
    if brand["sender_name"]:
        lines.append(brand["sender_name"])
    if brand["company_name"]:
        lines.append(brand["company_name"])
    if brand["company_description"]:
        lines.append(brand["company_description"])
    if calendly_link and calendly_link not in ("(none)", ""):
        lines.append(f"Book a call: {calendly_link}")

    if not lines:
        return "", ""

    plain = "--\n" + "\n".join(lines)
    html_lines = "".join(f"<div>{html.escape(line)}</div>" for line in lines)
    html_footer = (
        '<hr style="border:none;border-top:1px solid #e0e0e0;margin:24px 0;">'
        f'<div style="color:#666;font-size:13px;line-height:1.5;">{html_lines}</div>'
    )
    return plain, html_footer


def _plain_block_to_html(block: str) -> str:
    block = block.strip()
    if not block:
        return ""

    lines = block.split("\n")
    if all(re.match(r"^[-*•]\s+", ln) for ln in lines if ln.strip()):
        items = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            item = re.sub(r"^[-*•]\s+", "", ln)
            items.append(f"<li>{_inline_markdown(item)}</li>")
        return f"<ul style=\"margin:0 0 16px;padding-left:20px;\">{''.join(items)}</ul>"

    return f"<p style=\"margin:0 0 16px;\">{_inline_markdown(block.replace(chr(10), ' '))}</p>"


def _inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def plain_to_html(plain: str) -> str:
    plain = normalize_body(plain)
    blocks = re.split(r"\n\n+", plain)
    body = "".join(_plain_block_to_html(b) for b in blocks if b.strip())
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;'
        'line-height:1.6;color:#222;">'
        f"{body}</div>"
    )


def finalize_email_body(body: str, *, calendly_link: str = "") -> tuple[str, str]:
    """Normalize LLM output and append branded footer. Returns (plain, html)."""
    plain_body = normalize_body(body)
    footer_plain, footer_html = _build_footer(calendly_link=calendly_link)
    if footer_plain:
        plain = f"{plain_body}\n\n{footer_plain}"
    else:
        plain = plain_body

    html_body = plain_to_html(plain_body)
    if footer_html:
        html_body = f"{html_body}{footer_html}"
    return plain, html_body
