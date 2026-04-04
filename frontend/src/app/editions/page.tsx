import { getAllIssues } from "@/lib/issues";
import { IssueCard } from "@/components/IssueCard";
import { SubscribeForm } from "@/components/SubscribeForm";

export const metadata = {
  title: "Editions",
};

export default function IssuesPage() {
  const issues = getAllIssues();

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-3xl font-bold tracking-tight mb-2">Editions</h1>
      <p className="text-muted mb-8">Every edition of Core Dispatch.</p>

      {issues.length === 0 ? (
        <p className="text-muted">No issues published yet. Stay tuned.</p>
      ) : (
        <div className="space-y-3">
          {issues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>
      )}

      <div className="mt-14 rounded-xl bg-gradient-to-r from-gradient-start to-gradient-end p-[1px]">
        <div className="rounded-[11px] bg-surface p-6">
          <h2 className="font-semibold">Never miss an edition</h2>
          <p className="mt-1 mb-4 text-sm text-muted">
            Delivered to your inbox.
          </p>
          <SubscribeForm />
        </div>
      </div>
    </div>
  );
}
