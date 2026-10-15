# Claude Code — Kickoff Prompt
# Paste this as your first message when you open this repo in Claude Code.

---

I'm building the BC Co-op & Tech Job Tracker — a daily pipeline that scrapes public ATS job boards, filters to BC / Remote co-op and entry-level postings, and serves a Next.js dashboard.

The repo already contains:
- `CLAUDE.md` — coding conventions, architecture, env var names, do-not rules
- `companies.yaml` — seed list of ~70 BC tech companies with ATS type and slug
- `requirements.txt` — Python dependencies
- `supabase/migrations/001_initial_schema.sql` — full DB schema ready to run
- `.github/workflows/daily-ingest.yml` — GitHub Actions cron skeleton
- `.gitignore`

Read `CLAUDE.md` fully before writing any code. Everything in it is law for this repo.

---

## Phase 1 — ATS Detection Script (do this first)

Write `ingestion/detect_ats.py`. This script:
1. Loads every entry from `companies.yaml`
2. For each company, tries its declared ATS + slug. If it gets back ≥ 1 job, mark it verified. If it gets a non-200 or empty jobs array, try the other three ATS platforms with the same slug (as a fallback attempt — many slugs are the company name lowercased).
3. Prints a table: company name | city | ats | slug | job_count | verified (yes/no)
4. Writes a `companies_verified.yaml` that is a copy of `companies.yaml` with:
   - `active: false` for companies where no ATS returned jobs
   - `ats` and `slug` corrected where a fallback platform worked
   - A `job_count` field showing how many jobs were found

Use `httpx` with a 10-second timeout. Sleep 0.4s between requests. Do not crash if one company fails — catch the exception, log it, mark as unverified, continue.

Run this after writing it and show me the output table.

---

## Phase 2 — Ingestion Pipeline

Once `companies_verified.yaml` exists, build the full pipeline in `ingestion/`:

### `ingestion/models.py`
Pydantic `Posting` dataclass:
- `external_id: str`
- `company_slug: str`
- `title: str`
- `location: str | None`
- `url: str | None`
- `description: str | None`  (used only locally for skill extraction; never stored in DB)

### `ingestion/adapters/greenhouse.py`
Fetches `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`
Returns `list[Posting]`. Maps `jobs[].id` → `external_id`, `jobs[].location.name` → `location`, `jobs[].absolute_url` → `url`, `jobs[].content` → `description`.

### `ingestion/adapters/lever.py`
Fetches `https://api.lever.co/v0/postings/{slug}?mode=json`
Returns `list[Posting]`. Maps `[].id` → `external_id`, `[].categories.location` → `location`, `[].hostedUrl` → `url`, `[].descriptionPlain` → `description`.

### `ingestion/adapters/ashby.py`
Fetches `https://api.ashbyhq.com/posting-api/job-board/{slug}`
Returns `list[Posting]`. Response is `{"jobPostings": [...]}`. Maps `[].id` → `external_id`, `[].location` → `location`, `[].jobUrl` → `url`, `[].descriptionHtml` stripped of HTML → `description`.

### `ingestion/adapters/smartrecruiters.py`
Fetches `https://api.smartrecruiters.com/v1/companies/{slug}/postings` (paginated, limit=100).
Returns `list[Posting]`. Fetches detail per posting for the description only when needed for skill extraction.

### `ingestion/filters.py`
Two functions:
- `is_bc_location(location: str | None) -> bool` — returns True if location contains any of: Victoria, Vancouver, Surrey, Burnaby, Richmond, Kelowna, BC, British Columbia, or Remote (case-insensitive). Returns False for US/EU/etc.
- `is_coop(title: str) -> bool` — returns True if title matches any of: intern, co-op, coop, co op, student, new grad, entry.level, junior (case-insensitive word boundary match).

### `ingestion/skills.py`
`SKILL_KEYWORDS: dict[str, list[str]]` — a dict where each key is the canonical skill name and each value is a list of regex patterns. Include at least these 40 skills to start:
Python, JavaScript, TypeScript, React, Next.js, Vue, Angular, Node.js, Django, FastAPI, Flask, Go, Rust, Java, Kotlin, Swift, C++, C#, .NET, PHP, Ruby, Rails, SQL, PostgreSQL, MySQL, MongoDB, Redis, GraphQL, REST, Docker, Kubernetes, AWS, GCP, Azure, Terraform, Git, Linux, Machine Learning, Data Science, Figma.

`extract_skills(text: str) -> list[str]` — lowercases text, matches each pattern, returns list of canonical skill names found (deduplicated, sorted).

### `ingestion/upsert.py`
Uses `supabase-py`. Functions:
- `ensure_company(supabase, company: dict) -> str` — upserts to `companies` table, returns UUID.
- `upsert_postings(supabase, company_id: str, postings: list[Posting]) -> tuple[int, int]` — upserts each posting, returns (new_count, updated_count). On insert: sets `first_seen`, `last_seen`, `status=open`. On update: sets `last_seen`.
- `close_missing(supabase, company_id: str, seen_external_ids: set[str]) -> int` — marks as `status=closed`, sets `closed_at=now()` for any posting where `status=open` and `external_id NOT IN seen_external_ids`. Returns count closed.
- `upsert_skills(supabase, posting_id: str, skill_names: list[str])` — ensures each skill exists in `skills` table, then upserts rows in `posting_skills`.

### `ingestion/run.py`
The pipeline entrypoint:
1. Loads `companies_verified.yaml` (falls back to `companies.yaml` if verified doesn't exist)
2. Skips entries with `active: false`
3. For each active company: calls the right adapter, filters by BC location + co-op flag, extracts skills, upserts, closes missing
4. Logs progress to stdout and `ingestion/run.log`
5. Writes a row to the `runs` table with counts and duration

---

## Phase 3 — Tests

Write `tests/test_filters.py` and `tests/test_skills.py` with at least 5 test cases each. Mock HTTP calls in adapter tests using `pytest-httpx`.

Run `pytest tests/ -v` and make sure everything passes.

---

## Phase 4 — Next.js Dashboard

Scaffold `web/` as a Next.js 14 App Router project with TypeScript and Tailwind CSS.

Install: `npm install @supabase/ssr @supabase/supabase-js recharts`

Build four pages:
1. `app/page.tsx` — Overview: stat tiles (total open, co-op count, companies tracked, last run time), a line chart of new postings per day (last 30 days), and a horizontal bar chart of top 10 skills.
2. `app/postings/page.tsx` — filterable table of postings: filter by city, co-op toggle, date range. Each row links to the original posting URL.
3. `app/skills/page.tsx` — ranked bar chart of all skills, count of postings mentioning each.
4. `app/companies/page.tsx` — cards for each company: name, city, ATS platform, count of open postings.

Use server components for data fetching. `lib/supabase.ts` should export a `createClient()` function using `@supabase/ssr` and `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

The design should be clean and data-focused: dark sidebar nav, white content area, Recharts charts with a consistent color palette. Make it look like something you'd show a recruiter.

---

## Phase 5 — README

Write a `README.md` that includes:
- Project overview (2-3 sentences)
- Architecture diagram as a Mermaid flowchart showing: companies.yaml → Python pipeline → Supabase → Next.js dashboard → Vercel; GitHub Actions → Python pipeline
- Setup instructions (clone, install, set env vars, run migration, run pipeline, start dev server)
- Table of environment variables
- How the daily cron works
- Deploy to Vercel badge placeholder
- GitHub Actions CI badge placeholder

---

## Checklist before you start writing code

- [ ] Read `CLAUDE.md`
- [ ] Start with Phase 1 (detect_ats.py) and run it before building Phase 2
- [ ] Never crash the whole pipeline on one company's failure
- [ ] Never store full job descriptions in the database
- [ ] Never put SUPABASE_SERVICE_KEY in any NEXT_PUBLIC_ var
- [ ] Run `pytest` after Phase 3 and confirm all tests pass
- [ ] Commit after each phase with a clear message

Let's start with Phase 1. Write and run `ingestion/detect_ats.py` now.
