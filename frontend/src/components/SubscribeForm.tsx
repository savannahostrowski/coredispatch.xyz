import { useState } from "react";

const BUTTONDOWN_URL = "https://buttondown.com/api/emails/embed-subscribe/coredispatch";

export default function SubscribeForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");

  async function handleSubmit(e: { preventDefault: () => void }) {
    e.preventDefault();
    setStatus("submitting");
    try {
      await fetch(BUTTONDOWN_URL, {
        method: "POST",
        body: new URLSearchParams({ email }),
        mode: "no-cors",
      });
      setStatus("success");
      setEmail("");
    } catch {
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <div className="rounded-lg border border-success/30 bg-success/5 p-4 text-center">
        <p className="text-sm font-medium text-success">
          Check your email to confirm your subscription.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap gap-2">
      <input
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        className="flex-999 max-w-full rounded-lg border border-border bg-surface px-3.5 py-2 text-sm placeholder:text-muted/60 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all"
      />
      <button
        type="submit"
        disabled={status === "submitting"}
        className="flex-1 rounded-lg bg-gradient-to-r from-gradient-start to-gradient-end px-5 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity disabled:opacity-50"
      >
        {status === "submitting" ? "..." : "Subscribe"}
      </button>
      {status === "error" && <p className="self-center text-xs text-red-500">Try again</p>}
    </form>
  );
}
