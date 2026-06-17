"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { MonitorsLayout } from "@/components/features/MonitorsLayout";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Pagination } from "@/components/ui/Pagination";
import { DEFAULT_PAGE_SIZE, paginate } from "@/lib/pagination";
import { useGetResearchListQuery, useGetStatsQuery } from "@/store/researchApi";

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function preview(text: string, limit = 160) {
  const t = (text || "").replace(/\s+/g, " ").trim();
  return t.length > limit ? `${t.slice(0, limit)}…` : t;
}

export default function ResearchPage() {
  const [page, setPage] = useState(1);
  const { data: stats, isLoading: statsLoading } = useGetStatsQuery();
  const { data: items = [], isLoading: listLoading, error: listError } = useGetResearchListQuery();

  const paged = useMemo(() => paginate(items, page, DEFAULT_PAGE_SIZE), [items, page]);

  const monitorStats = stats
    ? [
        {
          label: "Total Researched",
          value: String(stats.total),
          sub: `${stats.today} TODAY`,
          subColor: "green" as const,
          icon: "radar",
        },
        {
          label: "Completed Today",
          value: String(stats.today),
          sub: "LIVE FROM API",
          subColor: "primary" as const,
          icon: "target",
        },
        {
          label: "Your Leads",
          value: String(items.length),
          sub: "WITH RESEARCH",
          subColor: "primary" as const,
          icon: "speed",
        },
        {
          label: "Pipeline",
          value: "ON",
          sub: "RESEARCH SERVICE",
          subColor: "green" as const,
          icon: "token",
        },
      ]
    : undefined;

  return (
    <MonitorsLayout
      title="Research"
      titleHighlight="Overview"
      stats={monitorStats}
      isLoading={statsLoading}
    >
      <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-primary/20">
          <h2 className="text-sm font-bold uppercase tracking-widest text-primary">Research results</h2>
        </div>

        {listLoading && <p className="p-6 text-slate-500 text-sm">Loading research…</p>}
        {listError != null && <p className="p-6 text-red-400 text-sm">Failed to load research.</p>}
        {!listLoading && listError == null && items.length === 0 && (
          <p className="p-6 text-slate-500 text-sm">No research yet. Add a lead with a company website to start.</p>
        )}

        {!listLoading && paged.items.length > 0 && (
          <>
            <div className="divide-y divide-primary/10">
              {paged.items.map((item) => (
                <Link
                  key={item.id}
                  href={`/leads/${item.lead_id}`}
                  className="block p-4 sm:p-6 hover:bg-primary/5 transition-colors"
                >
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-2">
                    <div className="min-w-0">
                      <p className="font-bold text-slate-100">
                        {item.lead_name || item.lead_email || `Lead #${item.lead_id}`}
                      </p>
                      <p className="text-sm text-slate-500">
                        {item.company_name || item.lead_email} · {formatDate(item.created_at)}
                      </p>
                    </div>
                    {item.lead_status && <StatusBadge status={item.lead_status} />}
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">{preview(item.website_summary)}</p>
                  {(item.pain_points?.length > 0 || item.use_cases?.length > 0) && (
                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                      {item.pain_points?.length > 0 && (
                        <span>{item.pain_points.length} pain point{item.pain_points.length === 1 ? "" : "s"}</span>
                      )}
                      {item.use_cases?.length > 0 && (
                        <span>{item.use_cases.length} use case{item.use_cases.length === 1 ? "" : "s"}</span>
                      )}
                    </div>
                  )}
                </Link>
              ))}
            </div>
            <Pagination
              page={paged.currentPage}
              totalPages={paged.totalPages}
              total={paged.total}
              from={paged.from}
              to={paged.to}
              onPageChange={setPage}
              label="results"
            />
          </>
        )}
      </div>
    </MonitorsLayout>
  );
}
