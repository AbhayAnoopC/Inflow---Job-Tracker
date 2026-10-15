import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(raw: str | None) -> str | None:
    """Unescape entities, drop tags, collapse whitespace. Handles double-escaped HTML."""
    if not raw:
        return None
    text = html.unescape(raw)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip() or None
