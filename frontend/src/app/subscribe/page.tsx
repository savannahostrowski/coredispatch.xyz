import { SubscribeForm } from "@/components/SubscribeForm";

export const metadata = {
  title: "Subscribe — Core Dispatch",
};

export default function SubscribePage() {
  return (
    <div className="mx-auto max-w-xl px-6 py-10">
      <h1 className="text-3xl font-bold tracking-tight mb-2">Subscribe</h1>
      <p className="text-muted mb-8">
        Get Core Dispatch delivered to your inbox. No spam, just
        Python.
      </p>
      <SubscribeForm />
      <p className="mt-6 text-xs text-muted">
        Prefer RSS?{" "}
        <a
          href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/feed/rss`}
          className="underline hover:text-foreground transition-colors"
        >
          Grab the feed
        </a>
        .
      </p>
    </div>
  );
}
