"use client";

import Link from "next/link";
import type { Lead } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";

function initials(name: string, email: string): string {
  if (name?.trim()) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    if (parts[0].length >= 2) return parts[0].slice(0, 2).toUpperCase();
    return parts[0][0].toUpperCase();
  }
  if (email?.length >= 2) return email.slice(0, 2).toUpperCase();
  return "—";
}

function relativeTime(iso: string): string {
  try {
    const d = new Date(iso);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} mins ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`;
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  } catch {
    return iso;
  }
}

/** Placeholder score 0–100 from lead id for visual consistency with design. */
function scoreFromLead(lead: Lead): number {
  return Math.min(100, 50 + (lead.id % 51));
}

export function LeadTable({
  leads,
  totalCount,
  page,
  pageSize,
  onPageChange,
}: {
  leads: Lead[];
  totalCount?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
}) {
  const count = totalCount ?? leads.length;
  const size = pageSize ?? 10;
  const totalPages = Math.max(1, Math.ceil(count / size));
  const currentPage = page ?? 1;
  const from = (currentPage - 1) * size + 1;
  const to = Math.min(currentPage * size, count);

  if (leads.length === 0) {
    return (
      <div className="bg-white/5 border border-primary/10 rounded-xl overflow-hidden">
        <div className="py-16 px-6 text-center">
          <span className="material-symbols-outlined text-4xl text-slate-500 mb-4 block">
            group
          </span>
          <p className="text-slate-100 font-medium mb-1">No leads found</p>
          <p className="text-sm text-slate-500">
            Try changing the filter or add leads from the sidebar.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/5 dark:bg-background/40 border border-primary/10 rounded-xl overflow-hidden shadow-2xl shadow-primary/5">
      <table className="w-full text-left border-collapse">
        <thead className="bg-primary/5 border-b border-primary/10 text-[11px] uppercase tracking-wider font-bold text-slate-500">
          <tr>
            <th className="px-6 py-4 w-10">
              <input
                type="checkbox"
                className="rounded border-primary/30 bg-transparent text-primary focus:ring-primary size-4"
                aria-label="Select all"
              />
            </th>
            <th className="px-6 py-4">Lead Name</th>
            <th className="px-6 py-4">Status</th>
            <th className="px-6 py-4">Score</th>
            <th className="px-6 py-4">Company</th>
            <th className="px-6 py-4">Last Active</th>
            <th className="px-6 py-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-primary/5 text-sm">
          {leads.map((lead) => {
            const score = scoreFromLead(lead);
            return (
              <tr key={lead.id} className="hover:bg-primary/5 transition-colors group">
                <td className="px-6 py-4">
                  <input
                    type="checkbox"
                    className="rounded border-primary/30 bg-transparent text-primary focus:ring-primary size-4"
                    aria-label={`Select ${lead.email}`}
                  />
                </td>
                <td className="px-6 py-4">
                  <Link
                    href={`/leads/${lead.id}`}
                    className="flex items-center gap-3 hover:opacity-90"
                  >
                    <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary shrink-0">
                      {initials(lead.name ?? "", lead.email)}
                    </div>
                    <div>
                      <p className="font-bold text-slate-100">{lead.name || "—"}</p>
                      <p className="text-[10px] text-slate-500">{lead.email}</p>
                    </div>
                  </Link>
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={lead.status} />
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-primary/10 rounded-full overflow-hidden w-16 max-w-16">
                      <div
                        className="bg-primary h-full rounded-full transition-all"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="text-[11px] font-bold text-slate-300">{score}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-slate-500">{lead.company_name || "—"}</td>
                <td className="px-6 py-4 text-slate-500">
                  {relativeTime(lead.updated_at)}
                </td>
                <td className="px-6 py-4 text-right">
                  <Link
                    href={`/leads/${lead.id}`}
                    className="inline-flex text-slate-400 hover:text-primary transition-colors"
                    aria-label="More actions"
                  >
                    <span className="material-symbols-outlined text-[20px]">more_horiz</span>
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {totalPages > 1 && onPageChange && (
        <div className="px-6 py-4 border-t border-primary/10 bg-primary/5 flex items-center justify-between text-xs text-slate-500 font-medium">
          <p>
            Showing {from} to {to} of {count} leads
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="size-8 flex items-center justify-center rounded border border-primary/20 bg-background hover:text-primary transition-colors disabled:opacity-50 disabled:pointer-events-none"
              aria-label="Previous page"
            >
              <span className="material-symbols-outlined text-sm">chevron_left</span>
            </button>
            {Array.from({ length: Math.min(3, totalPages) }, (_, i) => currentPage - 1 + i)
              .filter((p) => p >= 1 && p <= totalPages)
              .map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => onPageChange(p)}
                  className={`size-8 flex items-center justify-center rounded font-bold transition-colors ${
                    p === currentPage
                      ? "bg-primary text-primary-foreground"
                      : "border border-primary/20 bg-background hover:text-primary"
                  }`}
                >
                  {p}
                </button>
              ))}
            <button
              type="button"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="size-8 flex items-center justify-center rounded border border-primary/20 bg-background hover:text-primary transition-colors disabled:opacity-50 disabled:pointer-events-none"
              aria-label="Next page"
            >
              <span className="material-symbols-outlined text-sm">chevron_right</span>
            </button>
          </div>
        </div>
      )}
      {(!onPageChange || totalPages <= 1) && (
        <div className="px-6 py-4 border-t border-primary/10 bg-primary/5 text-xs text-slate-500 font-medium">
          Showing 1 to {leads.length} of {count} leads
        </div>
      )}
    </div>
  );
}
