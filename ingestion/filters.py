import re

_BC_RE = re.compile(
    r"\b(victoria|vancouver|surrey|burnaby|richmond|kelowna|bc|british columbia)\b", re.I
)
_REMOTE_RE = re.compile(r"\b(remote|distributed|work from home)\b", re.I)
# Remote roles explicitly tied to another region are not useful for BC applicants.
_NON_CANADA_RE = re.compile(
    r"\b(us|usa|u\.s\.|united states|uk|united kingdom|europe|emea|eu|apac|latam|india|australia)\b",
    re.I,
)
_CANADA_RE = re.compile(r"\bcanada\b", re.I)

_COOP_RE = re.compile(
    r"\b(intern(?:ship)?s?|co[\s-]?ops?|students?|new[\s-]grads?|entry[\s-]level|junior)\b", re.I
)


def is_bc_location(location: str | None) -> bool:
    if not location:
        return False
    if _BC_RE.search(location):
        return True
    if _REMOTE_RE.search(location):
        return bool(_CANADA_RE.search(location)) or not _NON_CANADA_RE.search(location)
    return False


def is_coop(title: str) -> bool:
    return bool(_COOP_RE.search(title))
