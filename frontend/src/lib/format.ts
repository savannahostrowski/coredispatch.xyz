export function formatDate(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function formatDateRange(start: string, end: string): string {
  const s = new Date(start + "T00:00:00");
  const e = new Date(end + "T00:00:00");

  if (s.getFullYear() === e.getFullYear() && s.getMonth() === e.getMonth()) {
    return `${s.toLocaleDateString("en-US", { month: "long", day: "numeric" })}\u2013${e.getDate()}, ${e.getFullYear()}`;
  }
  if (s.getFullYear() === e.getFullYear()) {
    return `${s.toLocaleDateString("en-US", { month: "short", day: "numeric" })}\u2013${e.toLocaleDateString("en-US", { month: "short", day: "numeric" })}, ${e.getFullYear()}`;
  }
  return `${formatDate(start)}\u2013${formatDate(end)}`;
}

export function formatTrimmedDescription(description: string): string {
  const limit = 160;
  if (description.length <= limit) {
    return description;
  }
  const trimmed = description.substring(0, limit);
  return trimmed.substring(0, trimmed.lastIndexOf(" ")) + "\u2026";
}
