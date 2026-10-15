export function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <header className="mb-7">
      <h1 className="text-[26px] font-semibold tracking-tight text-ink">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>}
    </header>
  );
}

export function StatTile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-lg border border-line border-t-[3px] border-t-[#3a7d5c] bg-card px-5 py-4">
      <div className="text-[32px] font-semibold leading-tight tabular-nums text-ink">{value}</div>
      <div className="mt-1 text-sm text-ink-muted">{label}</div>
      {hint && <div className="mt-0.5 text-xs text-ink-muted">{hint}</div>}
    </div>
  );
}

export function Card({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-lg border border-line bg-card p-5 ${className}`}>
      {title && <h2 className="mb-4 text-[15px] font-medium text-ink">{title}</h2>}
      {children}
    </section>
  );
}

export function CoopBadge() {
  return (
    <span className="inline-block rounded-full bg-coop-bg px-2 py-0.5 text-xs font-medium text-coop-text">
      Co-op
    </span>
  );
}

export function EmptyState({ children }: { children: React.ReactNode }) {
  return <p className="py-10 text-center text-sm text-ink-muted">{children}</p>;
}
