-- BC Job Tracker — Initial Schema
-- Run this in the Supabase SQL editor or via supabase db push

-- Enable UUID generation
create extension if not exists "pgcrypto";

-- ── companies ────────────────────────────────────────────────────────────────
create table if not exists companies (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  city         text not null,
  ats          text not null check (ats in ('greenhouse', 'lever', 'ashby', 'smartrecruiters', 'workday')),
  slug         text not null,
  careers_url  text,
  active       boolean not null default true,
  created_at   timestamptz not null default now(),
  unique (ats, slug)
);

-- ── postings ─────────────────────────────────────────────────────────────────
create table if not exists postings (
  id           uuid primary key default gen_random_uuid(),
  company_id   uuid not null references companies(id) on delete cascade,
  external_id  text not null,
  title        text not null,
  location     text,
  is_coop      boolean not null default false,
  status       text not null default 'open' check (status in ('open', 'closed')),
  url          text,
  first_seen   timestamptz not null default now(),
  last_seen    timestamptz not null default now(),
  closed_at    timestamptz,
  unique (company_id, external_id)
);

-- ── skills ───────────────────────────────────────────────────────────────────
create table if not exists skills (
  id    uuid primary key default gen_random_uuid(),
  name  text not null unique   -- normalized, e.g. "Python", "React", "Kubernetes"
);

-- ── posting_skills (many-to-many join) ───────────────────────────────────────
create table if not exists posting_skills (
  posting_id  uuid not null references postings(id) on delete cascade,
  skill_id    uuid not null references skills(id) on delete cascade,
  primary key (posting_id, skill_id)
);

-- ── runs (pipeline audit log) ────────────────────────────────────────────────
create table if not exists runs (
  id            uuid primary key default gen_random_uuid(),
  ran_at        timestamptz not null default now(),
  new_count     int not null default 0,
  closed_count  int not null default 0,
  error_count   int not null default 0,
  duration_s    numeric(8,2)
);

-- ── Row-Level Security ───────────────────────────────────────────────────────
-- The dashboard reads with the anon key. Allow SELECT on all tables.
-- Writes only happen from the ingestion pipeline using the service role key.

alter table companies      enable row level security;
alter table postings       enable row level security;
alter table skills         enable row level security;
alter table posting_skills enable row level security;
alter table runs           enable row level security;

create policy "Public read: companies"
  on companies for select using (true);

create policy "Public read: postings"
  on postings for select using (true);

create policy "Public read: skills"
  on skills for select using (true);

create policy "Public read: posting_skills"
  on posting_skills for select using (true);

create policy "Public read: runs"
  on runs for select using (true);

-- ── Indexes ──────────────────────────────────────────────────────────────────
create index if not exists idx_postings_status     on postings(status);
create index if not exists idx_postings_is_coop    on postings(is_coop);
create index if not exists idx_postings_first_seen on postings(first_seen desc);
create index if not exists idx_postings_company    on postings(company_id);
create index if not exists idx_posting_skills_skill on posting_skills(skill_id);
