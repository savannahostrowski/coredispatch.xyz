const BUTTONDOWN_URL = "https://buttondown.com/api/emails/embed-subscribe/coredispatch";

export default function SubscribeForm() {
  return (
    <form action={BUTTONDOWN_URL} method="post" className="flex flex-wrap gap-2">
      <input
        type="email"
        name="email"
        required
        placeholder="you@example.com"
        className="flex-999 max-w-full rounded-lg border border-border bg-surface px-3.5 py-2 text-sm placeholder:text-muted/60 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all"
      />
      <button
        type="submit"
        className="flex-1 rounded-lg bg-gradient-to-r from-gradient-start to-gradient-end px-5 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity"
      >
        Subscribe
      </button>
    </form>
  );
}
