export function formatPerformance(value: number | null | undefined): {
  text: string;
  color: string;
} {
  if (value == null) return { text: "N/A", color: "text-gray-400" };
  const sign = value >= 0 ? "+" : "";
  return {
    text: `${sign}${value.toFixed(1)}%`,
    color: value >= 0 ? "text-green-600" : "text-red-600",
  };
}

export function formatRelativeTime(iso: string | null): string {
  if (!iso) return "Never";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
