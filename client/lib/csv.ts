import type { Lead } from "@/types";

function escapeCsvCell(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

export function leadsToCsv(leads: Lead[]): string {
  const headers = [
    "id",
    "email",
    "name",
    "company_name",
    "company_website",
    "source",
    "status",
    "created_at",
    "updated_at",
  ];
  const rows = leads.map((lead) =>
    headers
      .map((h) => {
        const v = lead[h as keyof Lead];
        return escapeCsvCell(String(v ?? ""));
      })
      .join(",")
  );
  return [headers.join(","), ...rows].join("\n");
}

export function downloadCsv(content: string, filename: string): void {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
