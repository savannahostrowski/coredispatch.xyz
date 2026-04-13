export interface IssueQuote {
  text: string;
  author: string;
  url?: string;
}

export interface IssueCredit {
  name: string;
  url?: string;
}

export interface Issue {
  number: number;
  title: string;
  slug: string;
  editorial_notes: string;
  period_start: string;
  period_end: string;
  quote?: IssueQuote;
  credits?: IssueCredit[];
  items: Item[];
}

export interface Item {
  section: string;
  title: string;
  url: string;
  summary: string;
  source: string;
  metadata?: Record<string, unknown>;
}

export type Section =
  | "upcoming_releases"
  | "official_news"
  | "pep_updates"
  | "steering_council"
  | "welcome"
  | "merged_prs"
  | "discussions"
  | "events"
  | "musings"
  | "picks";

export const SECTION_LABELS: Record<Section, string> = {
  upcoming_releases: "Upcoming Releases",
  official_news: "Official News",
  pep_updates: "PEP Updates",
  steering_council: "Steering Council Updates",
  welcome: "Welcome to the Team",
  merged_prs: "Merged PRs",
  discussions: "Discussion",
  events: "Upcoming CFPs & Conferences",
  musings: "Core Team Musings",
  picks: "Community",
};

export const SECTION_DESCRIPTIONS: Partial<Record<Section, string>> = {
  official_news: "From the Python, PSF, PyPI and PyCon blogs.",
  pep_updates: "PEPs that changed status since last edition.",
  steering_council: "Meeting summaries and other communications from the Python Steering Council.",
  welcome: "New core team members and promotions.",
  merged_prs: "High-traffic PRs, new features, and changes that landed in What's New.",
  discussions: "Most active PEP discussions on Discourse since last edition.",
  musings: "Recent posts from the Python core team.",
  picks: "Community-submitted links, talks, and tools.",
};
