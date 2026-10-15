import SkillsBarChart from "@/components/charts/SkillsBarChart";
import { Card, EmptyState, PageHeader } from "@/components/ui";
import { getSkillCounts } from "@/lib/queries";

export const dynamic = "force-dynamic";

export default async function SkillsPage() {
  const skills = await getSkillCounts();
  return (
    <>
      <PageHeader
        title="Skills"
        subtitle="How many open postings mention each skill, ranked."
      />
      <Card>
        {skills.length ? <SkillsBarChart data={skills} /> : <EmptyState>No skill data yet.</EmptyState>}
      </Card>
    </>
  );
}
