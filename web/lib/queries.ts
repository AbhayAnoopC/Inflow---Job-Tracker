import { createClient } from "@/lib/supabase";

export type SkillCount = { name: string; count: number };
export type DayCount = { date: string; count: number };
export type CompanyRow = {
  id: string;
  name: string;
  city: string;
  ats: string;
  careers_url: string | null;
  openCount: number;
};
export type PostingRow = {
  id: string;
  title: string;
  location: string | null;
  url: string | null;
  is_coop: boolean;
  first_seen: string;
  companies: { name: string; city: string };
};
export type PostingFilters = {
  city?: string;
  coopOnly?: boolean;
  from?: string;
  to?: string;
};

const PAGE = 1000; // PostgREST default max rows per request

type Page<T> = PromiseLike<{ data: T[] | null; error: { message: string } | null }>;

async function fetchAll<T>(build: (from: number, to: number) => Page<T>): Promise<T[]> {
  const rows: T[] = [];
  for (let start = 0; ; start += PAGE) {
    const { data, error } = await build(start, start + PAGE - 1);
    if (error) throw new Error(error.message);
    rows.push(...(data ?? []));
    if (!data || data.length < PAGE) return rows;
  }
}

function unwrap<T>(res: { data: T | null; error: { message: string } | null }): T {
  if (res.error) throw new Error(res.error.message);
  return res.data as T;
}

export async function getOverview() {
  const supabase = createClient();
  const since = new Date();
  since.setUTCDate(since.getUTCDate() - 29);
  since.setUTCHours(0, 0, 0, 0);

  const [open, coop, companies, lastRun, recent] = await Promise.all([
    supabase.from("postings").select("id", { count: "exact", head: true }).eq("status", "open"),
    supabase
      .from("postings")
      .select("id", { count: "exact", head: true })
      .eq("status", "open")
      .eq("is_coop", true),
    supabase.from("companies").select("id", { count: "exact", head: true }),
    supabase.from("runs").select("ran_at").order("ran_at", { ascending: false }).limit(1),
    fetchAll<{ first_seen: string }>((from, to) =>
      supabase
        .from("postings")
        .select("first_seen")
        .gte("first_seen", since.toISOString())
        .order("first_seen")
        .range(from, to)
    ),
  ]);
  for (const r of [open, coop, companies, lastRun]) {
    if (r.error) throw new Error(r.error.message);
  }

  const perDay = new Map<string, number>();
  for (let i = 0; i < 30; i++) {
    const d = new Date(since);
    d.setUTCDate(since.getUTCDate() + i);
    perDay.set(d.toISOString().slice(0, 10), 0);
  }
  for (const { first_seen } of recent) {
    const key = first_seen.slice(0, 10);
    if (perDay.has(key)) perDay.set(key, (perDay.get(key) ?? 0) + 1);
  }
  const daily: DayCount[] = Array.from(perDay, ([date, count]) => ({ date, count }));

  return {
    openCount: open.count ?? 0,
    coopCount: coop.count ?? 0,
    companyCount: companies.count ?? 0,
    lastRunAt: (lastRun.data?.[0]?.ran_at as string | undefined) ?? null,
    daily,
  };
}

/** Skill → number of open postings mentioning it, descending. */
export async function getSkillCounts(): Promise<SkillCount[]> {
  const supabase = createClient();
  const rows = await fetchAll<{ skills: { name: string } | null }>((from, to) =>
    supabase
      .from("posting_skills")
      .select("posting_id, skill_id, skills(name), postings!inner(status)")
      .eq("postings.status", "open")
      .order("posting_id")
      .order("skill_id")
      .range(from, to) as unknown as Page<{ skills: { name: string } | null }>
  );
  const counts = new Map<string, number>();
  for (const r of rows) {
    if (r.skills) counts.set(r.skills.name, (counts.get(r.skills.name) ?? 0) + 1);
  }
  return Array.from(counts, ([name, count]) => ({ name, count })).sort(
    (a, b) => b.count - a.count || a.name.localeCompare(b.name)
  );
}

export async function getCities(): Promise<string[]> {
  const supabase = createClient();
  const rows = unwrap(await supabase.from("companies").select("city"));
  return Array.from(new Set(rows.map((r: { city: string }) => r.city))).sort();
}

export async function getPostings(filters: PostingFilters, limit = 300) {
  const supabase = createClient();
  let q = supabase
    .from("postings")
    .select("id,title,location,url,is_coop,first_seen,companies!inner(name,city)", {
      count: "exact",
    })
    .eq("status", "open");
  if (filters.city) q = q.eq("companies.city", filters.city);
  if (filters.coopOnly) q = q.eq("is_coop", true);
  if (filters.from) q = q.gte("first_seen", `${filters.from}T00:00:00-08:00`);
  if (filters.to) q = q.lte("first_seen", `${filters.to}T23:59:59-08:00`);
  const res = await q.order("first_seen", { ascending: false }).limit(limit);
  if (res.error) throw new Error(res.error.message);
  return { rows: (res.data ?? []) as unknown as PostingRow[], total: res.count ?? 0 };
}

export async function getCompanies(): Promise<CompanyRow[]> {
  const supabase = createClient();
  const [companies, open] = await Promise.all([
    supabase.from("companies").select("id,name,city,ats,careers_url").order("name"),
    fetchAll<{ company_id: string }>((from, to) =>
      supabase
        .from("postings")
        .select("company_id")
        .eq("status", "open")
        .order("id")
        .range(from, to)
    ),
  ]);
  if (companies.error) throw new Error(companies.error.message);
  const counts = new Map<string, number>();
  for (const { company_id } of open) counts.set(company_id, (counts.get(company_id) ?? 0) + 1);
  return (companies.data ?? []).map((c) => ({
    ...(c as Omit<CompanyRow, "openCount">),
    openCount: counts.get((c as { id: string }).id) ?? 0,
  }));
}
