import httpx

from adapters import _http
from models import Posting
from textutil import strip_html

URL = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


def fetch_postings(slug: str, client: httpx.Client) -> list[Posting]:
    data = _http.get_json(client, URL.format(slug=slug))
    # The documented key is "jobPostings"; the live API has been seen returning "jobs". Accept both.
    jobs = data.get("jobPostings") or data.get("jobs") or []
    postings: list[Posting] = []
    for job in jobs:
        postings.append(
            Posting(
                external_id=str(job["id"]),
                company_slug=slug,
                title=job.get("title", ""),
                location=job.get("location"),
                url=job.get("jobUrl"),
                description=strip_html(job.get("descriptionHtml")),
            )
        )
    return postings
