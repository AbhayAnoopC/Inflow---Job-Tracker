import httpx

from adapters import _http
from models import Posting

URL = "https://api.lever.co/v0/postings/{slug}"


def fetch_postings(slug: str, client: httpx.Client) -> list[Posting]:
    data = _http.get_json(client, URL.format(slug=slug), params={"mode": "json"})
    postings: list[Posting] = []
    for job in data:
        postings.append(
            Posting(
                external_id=str(job["id"]),
                company_slug=slug,
                title=job.get("text", ""),
                location=(job.get("categories") or {}).get("location"),
                url=job.get("hostedUrl"),
                description=job.get("descriptionPlain"),
            )
        )
    return postings
