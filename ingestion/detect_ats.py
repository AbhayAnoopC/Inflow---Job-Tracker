"""Verify each company's declared ATS + slug, fall back to other ATS platforms.

Usage: python ingestion/detect_ats.py
Reads companies.yaml, writes companies_verified.yaml (both at the repo root).
"""
import logging
import re
import sys
import time
from pathlib import Path
from typing import Callable

import httpx
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "companies.yaml"
DST = ROOT / "companies_verified.yaml"
TIMEOUT = 10.0
SLEEP = 0.4

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("detect_ats")


def _count_greenhouse(data: object) -> int:
    return len(data.get("jobs", [])) if isinstance(data, dict) else 0


def _count_lever(data: object) -> int:
    return len(data) if isinstance(data, list) else 0


def _count_ashby(data: object) -> int:
    if not isinstance(data, dict):
        return 0
    return len(data.get("jobs") or data.get("jobPostings") or [])


def _count_smartrecruiters(data: object) -> int:
    return int(data.get("totalFound", 0)) if isinstance(data, dict) else 0


ATS: dict[str, tuple[str, Callable[[object], int]]] = {
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", _count_greenhouse),
    "lever": ("https://api.lever.co/v0/postings/{slug}?mode=json", _count_lever),
    "ashby": ("https://api.ashbyhq.com/posting-api/job-board/{slug}", _count_ashby),
    "smartrecruiters": ("https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=1", _count_smartrecruiters),
}


def probe(client: httpx.Client, ats: str, slug: str) -> int:
    """Return job count for ats/slug; 0 on non-200, empty, or error."""
    url_tpl, counter = ATS[ats]
    try:
        resp = client.get(url_tpl.format(slug=slug))
        if resp.status_code != 200:
            return 0
        return counter(resp.json())
    except Exception as exc:  # noqa: BLE001 - never crash on one company
        log.warning("%s/%s failed: %s", ats, slug, exc)
        return 0
    finally:
        time.sleep(SLEEP)


def name_slug(name: str) -> str:
    base = re.sub(r"\(.*?\)", "", name).lower()
    return re.sub(r"[^a-z0-9]", "", base)


def detect(client: httpx.Client, company: dict) -> tuple[str, str, int]:
    """Return (ats, slug, job_count); job_count 0 means unverified."""
    declared_ats = company.get("ats", "")
    slug = str(company.get("slug", ""))
    if declared_ats in ATS and slug:
        count = probe(client, declared_ats, slug)
        if count >= 1:
            return declared_ats, slug, count
    slugs = [s for s in dict.fromkeys([slug, name_slug(company["name"])]) if s]
    for s in slugs:
        for ats in ATS:
            if ats == declared_ats and s == slug:
                continue
            count = probe(client, ats, s)
            if count >= 1:
                return ats, s, count
    return declared_ats, slug, 0


def main() -> int:
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    rows: list[dict] = []
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
        for company in data["companies"]:
            out = dict(company)
            try:
                ats, slug, count = detect(client, company)
            except Exception as exc:  # noqa: BLE001
                log.error("%s failed: %s", company.get("name"), exc)
                ats, slug, count = company.get("ats", ""), str(company.get("slug", "")), 0
            out["ats"], out["slug"], out["job_count"] = ats, slug, count
            if count == 0:
                out["active"] = False
            rows.append(out)

    header = f"{'company':<34}{'city':<14}{'ats':<17}{'slug':<24}{'jobs':>5}  verified"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['name'][:33]:<34}{str(r.get('city',''))[:13]:<14}{r['ats']:<17}"
              f"{r['slug'][:23]:<24}{r['job_count']:>5}  {'yes' if r['job_count'] else 'no'}")
    verified = sum(1 for r in rows if r["job_count"])
    print(f"\n{verified}/{len(rows)} verified")

    DST.write_text(yaml.safe_dump({"companies": rows}, sort_keys=False, allow_unicode=True),
                   encoding="utf-8")
    print(f"Wrote {DST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
