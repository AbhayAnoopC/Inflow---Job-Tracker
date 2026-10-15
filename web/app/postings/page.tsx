import Link from "next/link";
import { CoopBadge, EmptyState, PageHeader } from "@/components/ui";
import { formatDate } from "@/lib/format";
import { getCities, getPostings } from "@/lib/queries";

export const dynamic = "force-dynamic";

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

type Params = { city?: string; coop?: string; from?: string; to?: string };

export default async function PostingsPage({ searchParams }: { searchParams: Params }) {
  const cities = await getCities();
  const city = searchParams.city && cities.includes(searchParams.city) ? searchParams.city : undefined;
  const from = searchParams.from && DATE_RE.test(searchParams.from) ? searchParams.from : undefined;
  const to = searchParams.to && DATE_RE.test(searchParams.to) ? searchParams.to : undefined;
  const coopOnly = searchParams.coop === "1";

  const { rows, total } = await getPostings({ city, coopOnly, from, to });
  const filtered = Boolean(city || coopOnly || from || to);

  const field =
    "rounded-md border border-line bg-card px-2.5 py-1.5 text-sm text-ink focus:border-accent focus:outline-none";

  return (
    <>
      <PageHeader title="Postings" subtitle={`${total.toLocaleString()} open postings${filtered ? " match your filters" : ""}.`} />

      <form method="get" className="mb-5 flex flex-wrap items-end gap-4 rounded-lg border border-line bg-card p-4">
        <label className="flex flex-col gap-1 text-xs text-ink-muted">
          City
          <select name="city" defaultValue={city ?? ""} className={field}>
            <option value="">All cities</option>
            {cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-ink-muted">
          First seen from
          <input type="date" name="from" defaultValue={from ?? ""} className={field} />
        </label>
        <label className="flex flex-col gap-1 text-xs text-ink-muted">
          to
          <input type="date" name="to" defaultValue={to ?? ""} className={field} />
        </label>
        <label className="flex items-center gap-2 pb-2 text-sm text-ink">
          <input
            type="checkbox"
            name="coop"
            value="1"
            defaultChecked={coopOnly}
            className="h-4 w-4 accent-[#2d7a52]"
          />
          Co-op / entry-level only
        </label>
        <div className="flex items-center gap-3 pb-1">
          <button type="submit" className="rounded-md bg-accent px-3.5 py-1.5 text-sm text-white hover:bg-accent-hover">
            Apply
          </button>
          {filtered && (
            <Link href="/postings" className="text-sm text-accent hover:text-accent-hover">
              Clear
            </Link>
          )}
        </div>
      </form>

      {rows.length === 0 ? (
        <EmptyState>No postings match these filters.</EmptyState>
      ) : (
        <div className="overflow-hidden rounded-lg border border-line bg-card">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wide text-ink-muted">
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Company</th>
                <th className="px-4 py-3 font-medium">Location</th>
                <th className="px-4 py-3 font-medium">First seen</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((p) => (
                <tr key={p.id} className="border-b border-line bg-card even:bg-rowalt">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {p.url ? (
                        <a
                          href={p.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-accent hover:text-accent-hover"
                        >
                          {p.title}
                        </a>
                      ) : (
                        <span className="font-medium">{p.title}</span>
                      )}
                      {p.is_coop && <CoopBadge />}
                    </div>
                  </td>
                  <td className="px-4 py-3">{p.companies.name}</td>
                  <td className="px-4 py-3 text-ink-muted">{p.location ?? "—"}</td>
                  <td className="px-4 py-3 tabular-nums text-ink-muted">{formatDate(p.first_seen)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {total > rows.length && (
        <p className="mt-3 text-xs text-ink-muted">Showing the {rows.length} most recent of {total.toLocaleString()}.</p>
      )}
    </>
  );
}
