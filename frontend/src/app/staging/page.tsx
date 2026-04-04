import { getAllDrafts } from "@/lib/issues";
import { IssueCard } from "@/components/IssueCard";

export const metadata = {
  title: "Staging — Core Dispatch",
  robots: "noindex, nofollow",
};

export default function StagingPage() {
  const drafts = getAllDrafts();

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="mb-6 rounded-lg border border-yellow-300 bg-yellow-50 p-3 text-center text-sm text-yellow-800 dark:border-yellow-700 dark:bg-yellow-950 dark:text-yellow-200">
        Staging — these drafts are not published yet.
      </div>
      <h1 className="text-3xl font-bold tracking-tight mb-2">Drafts</h1>
      <p className="text-muted mb-8">Preview editions before publishing.</p>

      {drafts.length === 0 ? (
        <p className="text-muted">No drafts.</p>
      ) : (
        <div className="space-y-3">
          {drafts.map((draft) => (
            <IssueCard key={draft.id} issue={draft} basePath="/staging" />
          ))}
        </div>
      )}
    </div>
  );
}
