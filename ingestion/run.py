"""Pipeline entrypoint: python ingestion/run.py (or `python run.py` from ingestion/)."""
import logging
import os
import sys
import time
from pathlib import Path

import httpx
import yaml
from supabase import Client, create_client

from adapters import ashby, greenhouse, lever, smartrecruiters
from filters import is_bc_location
from models import Posting
from skills import extract_skills
from upsert import close_missing, ensure_company, get_posting_ids, upsert_postings, upsert_skills

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERIFIED = ROOT / "companies_verified.yaml"
SEED = ROOT / "companies.yaml"

FETCHERS = {
    "greenhouse": greenhouse.fetch_postings,
    "lever": lever.fetch_postings,
    "ashby": ashby.fetch_postings,
    "smartrecruiters": smartrecruiters.fetch_postings,
}

log = logging.getLogger("run")


def setup_logging() -> None:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handlers = [logging.StreamHandler(sys.stdout), logging.FileHandler(HERE / "run.log", mode="w", encoding="utf-8")]
    for h in handlers:
        h.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=handlers)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def load_companies() -> list[dict]:
    path = VERIFIED if VERIFIED.exists() else SEED
    log.info("Loading companies from %s", path.name)
    companies = yaml.safe_load(path.read_text(encoding="utf-8"))["companies"]
    seen: set[tuple[str, str]] = set()
    active: list[dict] = []
    for c in companies:
        key = (c.get("ats", ""), str(c.get("slug", "")))
        if not c.get("active", True) or key in seen or c.get("ats") not in FETCHERS:
            continue
        seen.add(key)
        active.append(c)
    return active


def process_company(supabase: Client, client: httpx.Client, company: dict) -> tuple[int, int]:
    """Returns (new_count, closed_count) for one company. Raises on failure."""
    ats, slug = company["ats"], str(company["slug"])
    postings = [p for p in FETCHERS[ats](slug, client) if is_bc_location(p.location)]
    if ats == "smartrecruiters":
        smartrecruiters.enrich_descriptions(slug, postings, client)

    company_id = ensure_company(supabase, company)
    new, updated = upsert_postings(supabase, company_id, postings)

    ids = get_posting_ids(supabase, company_id)
    for p in postings:
        skills = extract_skills(f"{p.title} {p.description or ''}")
        upsert_skills(supabase, ids[p.external_id], skills)

    closed = close_missing(supabase, company_id, {p.external_id for p in postings})
    log.info("%s: %d BC postings (%d new, %d updated, %d closed)", company["name"], len(postings), new, updated, closed)
    return new, closed


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    setup_logging()
    started = time.monotonic()
    supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    total_new = total_closed = errors = 0
    companies = load_companies()
    log.info("Running %d active companies", len(companies))
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for company in companies:
            try:
                new, closed = process_company(supabase, client, company)
                total_new += new
                total_closed += closed
            except Exception:  # noqa: BLE001 - one company must never kill the run
                errors += 1
                log.exception("Failed: %s", company.get("name"))

    duration = round(time.monotonic() - started, 2)
    supabase.table("runs").insert(
        {"new_count": total_new, "closed_count": total_closed, "error_count": errors, "duration_s": duration}
    ).execute()
    log.info("Done: %d new, %d closed, %d errors, %.1fs", total_new, total_closed, errors, duration)
    return 0


if __name__ == "__main__":
    sys.exit(main())
