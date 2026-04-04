import { notFound } from "next/navigation";
import Link from "next/link";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getAllDrafts, getDraftByNumber, getDraftItems } from "@/lib/issues";
import { formatDateRange } from "@/lib/format";
import { Preamble } from "@/components/Preamble";
import { QuoteOfTheWeek } from "@/components/QuoteOfTheWeek";
import { Credits } from "@/components/Credits";
import { SectionBlock } from "@/components/SectionBlock";

export const metadata = {
  robots: "noindex, nofollow",
};

export const dynamicParams = false;

export async function generateStaticParams() {
  return getAllDrafts().map((draft) => ({
    number: String(draft.number),
  }));
}

export default async function StagingIssuePage({
  params,
}: {
  params: Promise<{ number: string }>;
}) {
  const { number } = await params;
  const issue = getDraftByNumber(Number(number));
  if (!issue) notFound();

  const items = getDraftItems(issue.number);
  const editorial = issue.editorial_notes
    ?.replace(/<!--[\s\S]*?-->/g, "")
    .trim();

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Link
        href="/staging"
        className="inline-flex items-center gap-1 text-sm text-muted hover:text-foreground transition-colors"
      >
        {"\u2190"} Drafts
      </Link>

      <div className="mt-4 mb-6 rounded-lg border border-yellow-300 bg-yellow-50 p-3 text-center text-sm text-yellow-800 dark:border-yellow-700 dark:bg-yellow-950 dark:text-yellow-200">
        Draft — this edition is not published yet.
      </div>

      <div className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight">{issue.title}</h1>
        <p className="mt-2 text-sm text-muted">
          {formatDateRange(issue.period_start, issue.period_end)}
        </p>
      </div>

      {editorial && (
        <div className="mb-10 space-y-4 text-sm leading-relaxed text-muted [&_a]:text-accent [&_a:hover]:text-accent-hover [&_code]:rounded [&_code]:bg-border/50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-foreground/80">
          <Markdown remarkPlugins={[remarkGfm]}>{editorial}</Markdown>
        </div>
      )}

      <Preamble />

      <SectionBlock section="upcoming_releases" items={items.filter((i) => i.section === "upcoming_releases")} />

      {(["official_news", "pep_updates", "steering_council", "merged_prs", "discussions"] as const).map((section) => (
        <SectionBlock
          key={section}
          section={section}
          items={items.filter((i) => i.section === section)}
        />
      ))}

      <SectionBlock section="musings" items={items.filter((i) => i.section === "musings")} />

      <SectionBlock section="picks" items={items.filter((i) => i.section === "picks")} />

      <SectionBlock section="events" items={items.filter((i) => i.section === "events")} />

      {issue.quote && <QuoteOfTheWeek quote={issue.quote} />}

      {issue.credits && issue.credits.length > 0 && <Credits credits={issue.credits} />}
    </div>
  );
}
