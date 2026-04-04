import Link from "next/link";
import type { Issue } from "@/lib/types";
import { formatDateRange } from "@/lib/format";

interface IssueCardProps {
  issue: Issue;
}

export function IssueCard({ issue }: IssueCardProps) {
  const editorial = issue.editorial_notes
    ?.replace(/<!--[\s\S]*?-->/g, "")
    .trim();

  return (
    <Link
      href={`/editions/${issue.number}`}
      className="group block rounded-lg border border-border bg-surface p-5 transition-all hover:border-accent/40 hover:shadow-sm"
    >
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="font-semibold group-hover:text-accent transition-colors">
          {issue.title}
        </h3>
        <span className="shrink-0 rounded-full bg-accent-light px-2 py-0.5 text-xs font-medium text-accent">
          #{issue.number}
        </span>
      </div>
      <p className="mt-1.5 text-sm text-muted">
        {formatDateRange(issue.period_start, issue.period_end)}
      </p>
      {editorial && (
        <p className="mt-2 text-sm text-muted/80 line-clamp-2">{editorial}</p>
      )}
    </Link>
  );
}
