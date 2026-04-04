import { notFound } from "next/navigation";
import Link from "next/link";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getAllIssues, getIssueByNumber, getIssueItems, getAdjacentIssues } from "@/lib/issues";
import { formatDateRange } from "@/lib/format";
import { Credits } from "@/components/Credits";
import { Preamble } from "@/components/Preamble";
import { QuoteOfTheWeek } from "@/components/QuoteOfTheWeek";
import { SectionBlock } from "@/components/SectionBlock";
import { SubscribeForm } from "@/components/SubscribeForm";

export async function generateStaticParams() {
  return getAllIssues().map((issue) => ({
    number: String(issue.number),
  }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ number: string }>;
}) {
  const { number } = await params;
  const issue = getIssueByNumber(Number(number));
  return {
    title: issue ? `${issue.title} — Core Dispatch` : "Not Found",
  };
}

export default async function IssuePage({
  params,
}: {
  params: Promise<{ number: string }>;
}) {
  const { number } = await params;
  const issue = getIssueByNumber(Number(number));
  if (!issue) notFound();

  const items = getIssueItems(issue.number);
  const { prev, next } = getAdjacentIssues(issue.number);
  const editorial = issue.editorial_notes
    ?.replace(/<!--[\s\S]*?-->/g, "")
    .trim();

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Link
        href="/issues"
        className="inline-flex items-center gap-1 text-sm text-muted hover:text-foreground transition-colors"
      >
        {"\u2190"} Editions
      </Link>

      <div className="mt-6 mb-10">
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

      {/* Prev / Next nav */}
      <div className="mt-14 flex items-center justify-between border-t border-border pt-6">
        {prev ? (
          <Link href={`/editions/${prev.number}`} className="text-sm text-muted hover:text-accent transition-colors">
            {"\u2190"} {prev.title}
          </Link>
        ) : <span />}
        {next ? (
          <Link href={`/editions/${next.number}`} className="text-sm text-muted hover:text-accent transition-colors text-right">
            {next.title} {"\u2192"}
          </Link>
        ) : <span />}
      </div>

      <div className="mt-10 rounded-xl bg-gradient-to-r from-gradient-start to-gradient-end p-[1px]">
        <div className="rounded-[11px] bg-surface p-6">
          <h2 className="font-semibold">Enjoyed this issue?</h2>
          <p className="mt-1 mb-4 text-sm text-muted">
            Get Core Dispatch in your inbox.
          </p>
          <SubscribeForm />
        </div>
      </div>
    </div>
  );
}
