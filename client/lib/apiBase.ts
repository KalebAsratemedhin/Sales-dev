export function getApiBase(): string {
  if (typeof window === "undefined") return "";
  const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");
  return base || "";
}
