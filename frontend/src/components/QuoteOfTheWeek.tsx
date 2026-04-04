import type { IssueQuote } from "@/lib/types";

interface QuoteOfTheWeekProps {
  quote: IssueQuote;
}

export function QuoteOfTheWeek({ quote }: QuoteOfTheWeekProps) {
  return (
    <section className="mb-10">
      <div className="mb-2 pb-2 border-b border-border">
        <div className="flex items-center gap-2.5">
          <span className="text-lg">{"\u{1F4AC}"}</span>
          <h2 className="text-base font-semibold">One More Thing...</h2>
        </div>
        <p className="mt-1 text-xs text-muted">Your favourite funny, informative, or mass-reply-inducing words.</p>
      </div>
      <blockquote className="border-l-3 border-accent/40 pl-4 py-2">
        <p className="text-[15px] italic leading-relaxed text-foreground/90">
          {quote.text}
        </p>
        <p className="mt-2 text-sm text-muted">
          {"— "}
          {quote.url ? (
            <a href={quote.url} className="text-accent hover:text-accent-hover transition-colors">
              {quote.author}
            </a>
          ) : (
            quote.author
          )}
        </p>
      </blockquote>
      <p className="mt-3 text-xs text-muted">
        Have a great quote?{" "}
        <a
          href="https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml&title=%5BQuote%5D+"
          className="text-accent hover:text-accent-hover transition-colors"
        >
          Submit one for next edition
        </a>
        .
      </p>
    </section>
  );
}
