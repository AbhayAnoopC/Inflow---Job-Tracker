# BC Co-op & Tech Job Tracker — Claude Code Guide

## What This Project Is

A daily-updated pipeline that scrapes public ATS job boards from ~70 BC tech companies, filters to BC/Remote co-op and entry-level postings, extracts skills from descriptions, and serves the data through a Next.js dashboard deployed on Vercel.

**Repo structure:**
```
bc-job-tracker/
├── ingestion/            # Python pipeline (ATS adapters, filters, Supabase upsert)
│   ├── adapters/         # One module per ATS: greenhouse.py, lever.py, ashby.py, smartrecruiters.py
│   ├── filters.py        # BC location filter + co-op classifier
│   ├── skills.py         # Keyword skill extractor + 150-term list
│   ├── upsert.py         # Supabase upsert + diff logic
│   ├── run.py            # Pipeline entrypoint: loads companies.yaml, runs all adapters
│   └── models.py         # Pydantic Posting dataclass
├── companies.yaml        # Seed list: name, city, ats, slug, careers_url, active
├── tests/
│   ├── test_adapters.py  # Unit tests for each adapter (mocked HTTP)
│   ├── test_filters.py   # Location + co-op classifier tests
│   └── test_skills.py    # Skill extractor tests
├── web/                  # Next.js 14 dashboard (TypeScript + Tailwind + Recharts)
│   ├── app/
│   │   ├── page.tsx              # Overview page
│   │   ├── postings/page.tsx     # Filterable postings table
│   │   ├── skills/page.tsx       # Skill trends chart
│   │   └── companies/page.tsx    # Company cards
│   ├── lib/
│   │   └── supabase.ts           # Supabase SSR client
│   └── components/               # Shared UI components
├── supabase/
│   └── migrations/               # SQL schema files
├── .github/
│   └── workflows/
│       └── daily-ingest.yml      # GitHub Actions cron (7am PT daily)
├── requirements.txt
└── README.md
```

## Coding Conventions

### Python (ingestion/)
- Python 3.12. Use `httpx` for HTTP (not `requests`). Use `pydantic` for the `Posting` model.
- All adapters return `list[Posting]`. Never return raw dicts from an adapter.
- Never raise on a single company failure. Catch exceptions per-company, log the error, continue.
- Rate limit: sleep 0.5s between requests to the same ATS host.
- Environment variables via `os.environ` — never hardcode credentials.
- Type hints on every function signature.
- `pytest` for all tests. Mock HTTP with `pytest-httpx`. No live API calls in tests.

### TypeScript (web/)
- Next.js 14 App Router. Server components by default; use `"use client"` only for interactive bits.
- Fetch data in Server Components using the Supabase SSR client — never expose the service role key to the client.
- Tailwind for styles. No CSS modules, no styled-components.
- Recharts for all charts. Keep chart components in `web/components/charts/`.
- Use `font-variant-numeric: tabular-nums` on any column with numbers.

### Database
- Supabase Postgres. All schema changes go in `supabase/migrations/` as numbered SQL files.
- Use Row-Level Security; the dashboard reads with the anon key (SELECT only, no auth needed).
- Never store full job descriptions in the DB — store title, location, URL, skills, and metadata only.
- Upsert on `(company_id, external_id)` — this is the natural dedup key.

## Environment Variables

### ingestion/
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=   # write access; keep out of the frontend
```

### web/
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=   # read-only anon key; safe to expose
```

Store both sets as GitHub Actions secrets for the cron. Store web vars in Vercel environment settings.

## Key Design Decisions

1. **No full descriptions stored.** We link to the original ATS posting. This avoids legal grey zones and keeps the DB small.
2. **Diff by disappearance.** A posting is marked `closed` when it no longer appears in a run. `last_seen` updates every run; `closed_at` is set when status flips.
3. **Co-op detection is title-first.** Regex on the title catches 90%+ of cases. Employment type field is a secondary signal — only some ATS platforms expose it.
4. **Skills are extracted, not AI-classified.** MVP uses a 150-term keyword list for speed and zero API cost. Claude API upgrade is a stretch goal.
5. **GitHub Actions cron, not a server.** Keeps infrastructure costs at $0.

## Common Tasks

**Add a new company:**
Edit `companies.yaml`. Add a row with `name`, `city`, `ats`, `slug`, `careers_url`, `active: true`. The next run picks it up automatically.

**Add a new skill keyword:**
Edit `ingestion/skills.py` → `SKILL_KEYWORDS` dict. Key is the canonical name, value is a list of regex patterns that map to it.

**Run the pipeline locally:**
```bash
cd ingestion
pip install -r ../requirements.txt
SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python run.py
```

**Run tests:**
```bash
pytest tests/ -v
```

**Start the dev dashboard:**
```bash
cd web
npm install
npm run dev
```

## DO NOT

- Do not add `*` wildcard imports.
- Do not call any ATS API from inside a Next.js route handler — the pipeline is Python-only.
- Do not use `any` in TypeScript without a comment explaining why.
- Do not commit `.env` or `.env.local` files.
- Do not store Supabase service role key in `NEXT_PUBLIC_*` vars.
