import httpx

from adapters import _http
from models import Posting
from textutil import strip_html

URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def fetch_postings(slug: str, client: httpx.Client) -> list[Posting]:
    data = _http.get_json(client, URL.format(slug=slug), params={"content": "true"})
    postings: list[Posting] = []
    for job in data.get("jobs", []):
        postings.append(
            Posting(
                external_id=str(job["id"]),
                company_slug=slug,
                title=job.get("title", ""),
                location=(job.get("location") or {}).get("name"),
                url=job.get("absolute_url"),
                description=strip_html(job.get("content")),
            )
        )
    return postings
