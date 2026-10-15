from datetime import datetime, timezone
from typing import Any

from supabase import Client

from filters import is_coop
from models import Posting

CHUNK = 200


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _chunks(items: list[Any], size: int = CHUNK) -> list[list[Any]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def ensure_company(supabase: Client, company: dict) -> str:
    """Upsert a company on (ats, slug) and return its UUID."""
    row = {
        "name": company["name"],
        "city": company["city"],
        "ats": company["ats"],
        "slug": str(company["slug"]),
        "careers_url": company.get("careers_url"),
        "active": bool(company.get("active", True)),
    }
    res = supabase.table("companies").upsert(row, on_conflict="ats,slug").execute()
    return res.data[0]["id"]


def _existing_ids(supabase: Client, company_id: str) -> set[str]:
    ids: set[str] = set()
    start = 0
    while True:
        res = (
            supabase.table("postings")
            .select("external_id")
            .eq("company_id", company_id)
            .range(start, start + 999)
            .execute()
        )
        ids.update(r["external_id"] for r in res.data)
        if len(res.data) < 1000:
            return ids
        start += 1000


def upsert_postings(supabase: Client, company_id: str, postings: list[Posting]) -> tuple[int, int]:
    """Insert new postings and refresh existing ones. Returns (new_count, updated_count)."""
    existing = _existing_ids(supabase, company_id)
    now = _now()
    new_rows: list[dict] = []
    updated_rows: list[dict] = []
    for p in postings:
        row = {
            "company_id": company_id,
            "external_id": p.external_id,
            "title": p.title,
            "location": p.location,
            "url": p.url,
            "is_coop": is_coop(p.title),
            "status": "open",
            "closed_at": None,
            "last_seen": now,
        }
        if p.external_id in existing:
            updated_rows.append(row)  # first_seen omitted so the original value is kept
        else:
            new_rows.append({**row, "first_seen": now})

    for chunk in _chunks(new_rows):
        supabase.table("postings").upsert(chunk, on_conflict="company_id,external_id").execute()
    for chunk in _chunks(updated_rows):
        supabase.table("postings").upsert(chunk, on_conflict="company_id,external_id").execute()
    return len(new_rows), len(updated_rows)


def get_posting_ids(supabase: Client, company_id: str) -> dict[str, str]:
    """Map external_id -> posting UUID for a company."""
    out: dict[str, str] = {}
    start = 0
    while True:
        res = (
            supabase.table("postings")
            .select("id,external_id")
            .eq("company_id", company_id)
            .range(start, start + 999)
            .execute()
        )
        out.update({r["external_id"]: r["id"] for r in res.data})
        if len(res.data) < 1000:
            return out
        start += 1000


def close_missing(supabase: Client, company_id: str, seen_external_ids: set[str]) -> int:
    """Mark open postings not seen this run as closed. Returns count closed."""
    res = (
        supabase.table("postings")
        .select("id,external_id")
        .eq("company_id", company_id)
        .eq("status", "open")
        .execute()
    )
    stale = [r["id"] for r in res.data if r["external_id"] not in seen_external_ids]
    now = _now()
    for chunk in _chunks(stale):
        supabase.table("postings").update({"status": "closed", "closed_at": now}).in_(
            "id", chunk
        ).execute()
    return len(stale)


def upsert_skills(supabase: Client, posting_id: str, skill_names: list[str]) -> None:
    """Ensure each skill exists, then link them to the posting."""
    if not skill_names:
        return
    supabase.table("skills").upsert([{"name": n} for n in skill_names], on_conflict="name").execute()
    res = supabase.table("skills").select("id,name").in_("name", skill_names).execute()
    links = [{"posting_id": posting_id, "skill_id": r["id"]} for r in res.data]
    supabase.table("posting_skills").upsert(links, on_conflict="posting_id,skill_id").execute()
