import PostingsLineChart from "@/components/charts/PostingsLineChart";
import SkillsBarChart from "@/components/charts/SkillsBarChart";
import { Card, EmptyState, PageHeader, StatTile } from "@/components/ui";
import { formatDateTime, timeAgo } from "@/lib/format";
import { getOverview, getSkillCounts } from "@/lib/queries";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  const [overview, skills] = await Promise.all([getOverview(), getSkillCounts()]);
  return (
    <>
      <PageHeader
        title="Overview"
        subtitle="Co-op and entry-level tech postings across BC, refreshed every morning."
      />
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Open postings" value={overview.openCount.toLocaleString()} />
        <StatTile label="Co-op & entry-level" value={overview.coopCount.toLocaleString()} />
        <StatTile label="Companies tracked" value={overview.companyCount.toLocaleString()} />
        <StatTile
          label="Last run"
          value={overview.lastRunAt ? timeAgo(overview.lastRunAt) : "—"}
          hint={overview.lastRunAt ? formatDateTime(overview.lastRunAt) : "No runs yet"}
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="New postings per day (last 30 days)">
          <PostingsLineChart data={overview.daily} />
        </Card>
        <Card title="Top 10 skills">
          {skills.length ? (
            <SkillsBarChart data={skills.slice(0, 10)} />
          ) : (
            <EmptyState>No skill data yet.</EmptyState>
          )}
        </Card>
      </div>
    </>
  );
}
