import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Core Dispatch",
    template: "%s — Core Dispatch",
  },
  description:
    "A regular digest of what's happening in CPython — from merged PRs and PEP decisions to community discussions and upcoming events.",
  metadataBase: new URL("https://coredispatch.xyz"),
  openGraph: {
    title: "Core Dispatch",
    description:
      "A regular digest of what's happening in CPython — from merged PRs and PEP decisions to community discussions and upcoming events.",
    url: "https://coredispatch.xyz",
    siteName: "Core Dispatch",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary",
    title: "Core Dispatch",
    description:
      "A regular digest of what's happening in CPython — from merged PRs and PEP decisions to community discussions and upcoming events.",
  },
  alternates: {
    types: {
      "application/rss+xml": "/api/feed/rss",
    },
  },
  robots: {
    index: true,
    follow: true,
  },
};

function Header() {
  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-50">
      <nav className="mx-auto flex max-w-3xl items-center justify-between px-6 py-3">
        <Link
          href="/"
          className="flex items-center gap-1.5 font-bold tracking-tight text-lg group"
        >
          <span className="bg-gradient-to-r from-gradient-start to-gradient-end bg-clip-text text-transparent">
            core
          </span>
          <span className="text-python-yellow">/</span>
          <span>dispatch</span>
        </Link>
        <div className="flex items-center gap-5 text-sm">
          <Link
            href="/editions"
            className="text-muted hover:text-foreground transition-colors"
          >
            Editions
          </Link>
          <Link
            href="/subscribe"
            className="rounded-full bg-gradient-to-r from-gradient-start to-gradient-end px-3.5 py-1.5 text-xs font-medium text-white hover:opacity-90 transition-opacity"
          >
            Subscribe
          </Link>
        </div>
      </nav>
    </header>
  );
}

function Footer() {
  return (
    <footer className="mt-auto border-t border-border py-10">
      <div className="mx-auto max-w-3xl px-6 text-center text-sm text-muted">
        <p className="font-medium text-foreground/60">
          Core Dispatch
        </p>
        <p className="mt-1">
          A regular digest of what&apos;s happening in CPython.
        </p>
        <div className="mt-4 flex items-center justify-center gap-4">
          <a
            href="https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml"
            className="hover:text-foreground transition-colors"
          >
            Submit a link
          </a>
          <span className="text-border">|</span>
          <a
            href="/api/feed/rss"
            className="hover:text-foreground transition-colors"
          >
            RSS
          </a>
          <span className="text-border">|</span>
          <a
            href="https://github.com/savannahostrowski/coredispatch.xyz"
            className="hover:text-foreground transition-colors"
          >
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
