import httpx

from adapters import _http
from models import Posting
from textutil import strip_html

LIST_URL = "https://api.smartrecruiters.com/v1/companies/{slug}/postings"
DETAIL_URL = "https://api.smartrecruiters.com/v1/companies/{slug}/postings/{id}"
PAGE_SIZE = 100


def _location(loc: dict) -> str | None:
    text = ", ".join(p for p in (loc.get("city"), loc.get("region"), loc.get("country")) if p)
    if loc.get("remote"):
        text = f"{text} (Remote)" if text else "Remote"
    return text or None


def fetch_postings(slug: str, client: httpx.Client) -> list[Posting]:
    """List postings (paginated). Descriptions are NOT fetched here; see enrich_descriptions."""
    postings: list[Posting] = []
    offset = 0
    while True:
        data = _http.get_json(
            client, LIST_URL.format(slug=slug), params={"limit": PAGE_SIZE, "offset": offset}
        )
        content = data.get("content", [])
        for job in content:
            postings.append(
                Posting(
                    external_id=str(job["id"]),
                    company_slug=slug,
                    title=job.get("name", ""),
                    location=_location(job.get("location") or {}),
                    url=f"https://jobs.smartrecruiters.com/{slug}/{job['id']}",
                )
            )
        offset += PAGE_SIZE
        if not content or offset >= int(data.get("totalFound", 0)):
            return postings


def enrich_descriptions(slug: str, postings: list[Posting], client: httpx.Client) -> None:
    """Fetch the detail endpoint per posting to fill in description (call after filtering)."""
    for p in postings:
        data = _http.get_json(client, DETAIL_URL.format(slug=slug, id=p.external_id))
        sections = (data.get("jobAd") or {}).get("sections") or {}
        p.description = strip_html(" ".join((s or {}).get("text", "") for s in sections.values()))
