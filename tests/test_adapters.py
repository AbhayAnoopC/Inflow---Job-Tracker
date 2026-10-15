import httpx
import pytest
from pytest_httpx import HTTPXMock

from adapters import ashby, greenhouse, lever, smartrecruiters
from models import Posting


@pytest.fixture
def client() -> httpx.Client:
    with httpx.Client() as c:
        yield c


def test_greenhouse(httpx_mock: HTTPXMock, client: httpx.Client) -> None:
    httpx_mock.add_response(
        url="https://boards-api.greenhouse.io/v1/boards/acme/jobs?content=true",
        json={
            "jobs": [
                {
                    "id": 123,
                    "title": "Dev Intern",
                    "location": {"name": "Vancouver, BC"},
                    "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
                    "content": "&lt;p&gt;Use &lt;b&gt;Python&lt;/b&gt;&lt;/p&gt;",
                }
            ]
        },
    )
    result = greenhouse.fetch_postings("acme", client)
    assert result == [
        Posting(
            external_id="123",
            company_slug="acme",
            title="Dev Intern",
            location="Vancouver, BC",
            url="https://boards.greenhouse.io/acme/jobs/123",
            description="Use Python",
        )
    ]


def test_lever(httpx_mock: HTTPXMock, client: httpx.Client) -> None:
    httpx_mock.add_response(
        url="https://api.lever.co/v0/postings/acme?mode=json",
        json=[
            {
                "id": "abc-1",
                "text": "Co-op Engineer",
                "categories": {"location": "Victoria, BC"},
                "hostedUrl": "https://jobs.lever.co/acme/abc-1",
                "descriptionPlain": "Build things in Go",
            }
        ],
    )
    (p,) = lever.fetch_postings("acme", client)
    assert (p.external_id, p.title, p.location) == ("abc-1", "Co-op Engineer", "Victoria, BC")
    assert p.url == "https://jobs.lever.co/acme/abc-1"
    assert p.description == "Build things in Go"


def test_ashby_job_postings_key_and_html_stripped(httpx_mock: HTTPXMock, client: httpx.Client) -> None:
    httpx_mock.add_response(
        url="https://api.ashbyhq.com/posting-api/job-board/acme",
        json={
            "jobPostings": [
                {
                    "id": "j1",
                    "title": "Junior Dev",
                    "location": "Remote",
                    "jobUrl": "https://jobs.ashbyhq.com/acme/j1",
                    "descriptionHtml": "<h1>Role</h1><p>React &amp; Node</p>",
                }
            ]
        },
    )
    (p,) = ashby.fetch_postings("acme", client)
    assert p.external_id == "j1"
    assert p.location == "Remote"
    assert p.description == "Role React & Node"


def test_ashby_live_jobs_key(httpx_mock: HTTPXMock, client: httpx.Client) -> None:
    httpx_mock.add_response(
        url="https://api.ashbyhq.com/posting-api/job-board/acme",
        json={"jobs": [{"id": "j2", "title": "Dev", "location": "Burnaby", "jobUrl": "u"}]},
    )
    (p,) = ashby.fetch_postings("acme", client)
    assert p.external_id == "j2" and p.description is None


def test_smartrecruiters_pagination_and_enrichment(httpx_mock: HTTPXMock, client: httpx.Client) -> None:
    base = "https://api.smartrecruiters.com/v1/companies/acme/postings"
    httpx_mock.add_response(
        url=f"{base}?limit=100&offset=0",
        json={
            "totalFound": 101,
            "content": [
                {"id": str(i), "name": f"Job {i}", "location": {"city": "Vancouver", "region": "BC", "country": "ca"}}
                for i in range(100)
            ],
        },
    )
    httpx_mock.add_response(
        url=f"{base}?limit=100&offset=100",
        json={
            "totalFound": 101,
            "content": [{"id": "100", "name": "Job 100", "location": {"remote": True}}],
        },
    )
    result = smartrecruiters.fetch_postings("acme", client)
    assert len(result) == 101
    assert result[0].location == "Vancouver, BC, ca"
    assert result[0].description is None
    assert result[100].location == "Remote"
    assert result[0].url == "https://jobs.smartrecruiters.com/acme/0"

    httpx_mock.add_response(
        url=f"{base}/0",
        json={"jobAd": {"sections": {"jobDescription": {"text": "<p>Kotlin dev</p>"}}}},
    )
    smartrecruiters.enrich_descriptions("acme", result[:1], client)
    assert result[0].description == "Kotlin dev"


def test_http_error_raises(httpx_mock: HTTPXMock, client: httpx.Client) -> None:
    httpx_mock.add_response(url="https://api.lever.co/v0/postings/gone?mode=json", status_code=404)
    with pytest.raises(httpx.HTTPStatusError):
        lever.fetch_postings("gone", client)
