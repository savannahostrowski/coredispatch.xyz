import fs from "fs";
import path from "path";
import YAML from "yaml";
import type { Issue, Item } from "./types";

const EDITIONS_DIR = process.env.EDITIONS_DIR || path.join(process.cwd(), "..", "editions");
const DRAFTS_DIR = process.env.DRAFTS_DIR || path.join(process.cwd(), "..", "drafts");

interface IssueCredit {
  name: string;
  url?: string;
}

interface IssueQuote {
  text: string;
  author: string;
  url?: string;
}

interface IssueFile {
  number: number;
  title: string;
  slug: string;
  period_start: string;
  period_end: string;
  week_start?: string;
  week_end?: string;
  editorial_notes: string;
  quote?: IssueQuote;
  credits?: IssueCredit[];
  items: IssueFileItem[];
}

interface IssueFileItem {
  section: string;
  title: string;
  url: string;
  summary: string;
  source: string;
  metadata?: Record<string, unknown>;
}

function parseIssueFile(filePath: string): IssueFile | null {
  try {
    const content = fs.readFileSync(filePath, "utf-8");
    const data = YAML.parse(content);
    if (!data || typeof data !== "object" || !data.number) return null;
    return data as IssueFile;
  } catch {
    return null;
  }
}

function loadIssuesFromDir(dir: string): Issue[] {
  if (!fs.existsSync(dir)) return [];

  const files = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".yml") && !f.startsWith("_"));

  const issues: Issue[] = [];

  for (const file of files) {
    const data = parseIssueFile(path.join(dir, file));
    if (!data) continue;

    const periodStart = data.period_start || data.week_start || "";
    const periodEnd = data.period_end || data.week_end || "";

    issues.push({
      id: data.slug,
      number: data.number,
      title: data.title,
      slug: data.slug,
      editorial_notes: data.editorial_notes || "",
      status: "published",
      published_at: null,
      period_start: periodStart,
      period_end: periodEnd,
      created_at: periodStart,
      quote: data.quote,
      credits: data.credits,
    });
  }

  return issues;
}

function loadItemsFromDir(dir: string, number: number): Item[] {
  if (!fs.existsSync(dir)) return [];

  const files = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".yml") && !f.startsWith("_"));

  for (const file of files) {
    const data = parseIssueFile(path.join(dir, file));
    if (!data || data.number !== number) continue;

    return (data.items || []).map((item, idx) => ({
      id: `${data.slug}-${idx}`,
      issue_id: data.slug,
      section: item.section,
      title: item.title,
      url: item.url,
      summary: item.summary || "",
      editorial_note: "",
      source: item.source || "manual",
      source_id: "",
      status: "approved",
      sort_order: idx,
      metadata_: item.metadata || null,
      fetched_at: null,
      created_at: data.period_start || data.week_start || "",
    }));
  }

  return [];
}

// --- Published editions ---

export function getAllIssues(): Issue[] {
  return loadIssuesFromDir(EDITIONS_DIR).sort((a, b) => b.number - a.number);
}

export function getIssueByNumber(number: number): Issue | null {
  const all = getAllIssues();
  return all.find((i) => i.number === number) ?? null;
}

export function getIssueItems(number: number): Item[] {
  return loadItemsFromDir(EDITIONS_DIR, number);
}

export function getLatestIssue(): Issue | null {
  const all = getAllIssues();
  return all.length > 0 ? all[0] : null;
}

export function getAdjacentIssues(number: number): { prev: Issue | null; next: Issue | null } {
  const all = getAllIssues();
  const idx = all.findIndex((i) => i.number === number);
  return {
    prev: idx < all.length - 1 ? all[idx + 1] : null,
    next: idx > 0 ? all[idx - 1] : null,
  };
}

// --- Drafts (staging) ---

export function getAllDrafts(): Issue[] {
  return loadIssuesFromDir(DRAFTS_DIR).sort((a, b) => b.number - a.number);
}

export function getDraftByNumber(number: number): Issue | null {
  const all = getAllDrafts();
  return all.find((i) => i.number === number) ?? null;
}

export function getDraftItems(number: number): Item[] {
  return loadItemsFromDir(DRAFTS_DIR, number);
}
