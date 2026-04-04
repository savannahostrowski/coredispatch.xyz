import { getAllIssues } from "@/lib/issues";
import { IssueCard } from "@/components/IssueCard";
import { SubscribeForm } from "@/components/SubscribeForm";
import Link from "next/link";

export default function Home() {
  const issues = getAllIssues();
  const recent = issues.slice(0, 4);

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      {/* Hero + Subscribe */}
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight">
          <span className="bg-gradient-to-r from-gradient-start to-gradient-end bg-clip-text text-transparent">
            Core Dispatch
          </span>
        </h1>
        <p className="mt-4 text-lg text-muted max-w-md mx-auto">
          A regular digest of what{"'"}s happening in Python core development — from merged PRs
          and PEP decisions to community discussions and upcoming events.
        </p>
        <div className="mt-8 mx-auto max-w-sm">
          <SubscribeForm />
        </div>
      </div>

      {/* Recent Issues */}
      {recent.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-4">Recent Issues</h2>
          <div className="space-y-3">
            {recent.map((issue) => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
          </div>
          {issues.length > 4 && (
            <div className="mt-6 text-center">
              <Link
                href="/editions"
                className="text-sm text-accent hover:text-accent-hover transition-colors"
              >
                View all {issues.length} issues {"\u2192"}
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
