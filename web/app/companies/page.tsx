import { EmptyState, PageHeader } from "@/components/ui";
import { ATS_LABELS } from "@/lib/format";
import { getCompanies } from "@/lib/queries";

export const dynamic = "force-dynamic";

export default async function CompaniesPage() {
  const companies = await getCompanies();
  return (
    <>
      <PageHeader title="Companies" subtitle={`${companies.length} companies tracked.`} />
      {companies.length === 0 ? (
        <EmptyState>No companies yet. Run the ingestion pipeline.</EmptyState>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {companies
            .sort((a, b) => b.openCount - a.openCount || a.name.localeCompare(b.name))
            .map((c) => (
              <div key={c.id} className="rounded-lg border border-line bg-card p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-[15px] font-medium text-ink">{c.name}</h2>
                    <p className="mt-0.5 text-sm text-ink-muted">{c.city}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-semibold tabular-nums text-ink">{c.openCount}</div>
                    <div className="text-xs text-ink-muted">open</div>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between text-xs text-ink-muted">
                  <span>{ATS_LABELS[c.ats] ?? c.ats}</span>
                  {c.careers_url && (
                    <a
                      href={c.careers_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:text-accent-hover"
                    >
                      Careers page ↗
                    </a>
                  )}
                </div>
              </div>
            ))}
        </div>
      )}
    </>
  );
}
