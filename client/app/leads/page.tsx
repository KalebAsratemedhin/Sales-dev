"use client";

import { useState, useMemo, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useGetLeadsQuery } from "@/store/leadsApi";
import { LeadTable } from "@/components/features/LeadTable";
import { LinkedInSyncRange } from "@/components/features/LinkedInSyncRange";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { leadsToCsv, downloadCsv } from "@/lib/csv";
import { Skeleton } from "@/components/ui/Skeleton";

const PAGE_SIZE = 10;
const STATUS_FILTERS = [
  { value: "", label: "All Leads", countLabel: true },
  { value: "new", label: "Cold", icon: "ac_unit" },
  { value: "researched", label: "Warm", icon: "wb_sunny" },
  { value: "emailed", label: "Contacted", icon: null },
  { value: "replied", label: "Hot", icon: "local_fire_department" },
  { value: "meeting_booked", label: "Meeting", icon: "event" },
  { value: "follow_up_required", label: "Follow-up required", countLabel: true },
] as const;

const VALID_STATUS = new Set<string>(
  STATUS_FILTERS.map((f) => f.value).filter(Boolean)
);

function LeadTableSkeleton() {
  return (
    <div className="bg-white/5 border border-primary/10 rounded-xl overflow-hidden">
      <div className="p-6 space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center gap-4">
            <Skeleton className="size-8 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-48" />
            </div>
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-4 w-12" />
          </div>
        ))}
      </div>
    </div>
  );
}

function LeadsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const statusFromUrl = searchParams.get("status");
  const initialStatus =
    statusFromUrl && VALID_STATUS.has(statusFromUrl) ? statusFromUrl : "";
  const [statusFilter, setStatusFilter] = useState<string>(initialStatus);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const next = statusFromUrl && VALID_STATUS.has(statusFromUrl) ? statusFromUrl : "";
    setStatusFilter(next);
    setPage(1);
  }, [statusFromUrl]);

  const setStatusFilterAndUpdateUrl = (value: string) => {
    setStatusFilter(value);
    setPage(1);
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set("status", value);
    else params.delete("status");
    const q = params.toString();
    router.replace(q ? `/leads?${q}` : "/leads", { scroll: false });
  };

  const { data: leads = [], isLoading, error } = useGetLeadsQuery(
    statusFilter ? { status: statusFilter } : undefined
  );

  const totalCount = leads.length;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  const pageLeads = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return leads.slice(start, start + PAGE_SIZE);
  }, [leads, page]);

  const handlePageChange = (p: number) => setPage(Math.max(1, Math.min(p, totalPages)));

  const handleExportCsv = () => {
    const csv = leadsToCsv(leads);
    const name = statusFilter ? `leads-${statusFilter}.csv` : "leads.csv";
    downloadCsv(csv, name);
  };

  return (
    <ScrollArea className="flex-1">
      <div className="p-8 bg-background">
        <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="flex gap-2 text-xs font-medium text-slate-500 mb-2 uppercase tracking-widest">
              <span>SalesMind</span>
              <span>/</span>
              <span className="text-primary">Leads</span>
            </div>
            <h3 className="text-3xl font-bold mb-2 text-slate-100">High Intent Pipeline</h3>
            <p className="text-slate-500 max-w-2xl">
              Manage and track your high-intent prospects with electric amber insights and
              real-time behavioral data.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleExportCsv}
              disabled={isLoading || leads.length === 0}
              className="px-4 py-2 border border-primary/20 bg-primary/5 hover:bg-primary/10 text-primary rounded text-sm font-bold flex items-center gap-2 transition-colors disabled:opacity-50 disabled:pointer-events-none"
            >
              <span className="material-symbols-outlined text-sm">download</span>
              Export CSV
            </button>
          </div>
        </div>

        <div className="mb-8">
          <LinkedInSyncRange />
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {STATUS_FILTERS.map((filter) => {
            const { value, label } = filter;
            const isActive = statusFilter === value;
            return (
              <button
                key={value || "all"}
                type="button"
                onClick={() => setStatusFilterAndUpdateUrl(value)}
                className={`flex items-center gap-2 px-4 py-1.5 rounded font-medium text-sm whitespace-nowrap transition-colors ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "border border-primary/20 bg-primary/5 hover:bg-primary/10 text-slate-300"
                }`}
              >
                {label}
                {"countLabel" in filter && filter.countLabel && value === "" && (
                  <span
                    className={
                      isActive ? "bg-primary-foreground/20 px-1.5 rounded text-[10px]" : "bg-primary/20 text-primary px-1.5 rounded text-[10px]"
                    }
                  >
                    {totalCount.toLocaleString()}
                  </span>
                )}
                {"icon" in filter && filter.icon && (
                  <span
                    className={`material-symbols-outlined text-sm ${
                      label === "Hot" ? "text-red-400" : label === "Warm" ? "text-orange-400" : "text-blue-400"
                    }`}
                  >
                    {filter.icon}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {isLoading && <LeadTableSkeleton />}
        {error && (
          <p className="py-8 text-center text-sm text-red-400">
            Failed to load leads. Check API base URL.
          </p>
        )}
        {!isLoading && !error && (
          <LeadTable
            leads={pageLeads}
            totalCount={totalCount}
            pageSize={PAGE_SIZE}
            page={page}
            onPageChange={handlePageChange}
          />
        )}
      </div>
    </ScrollArea>
  );
}

export default function LeadsPage() {
  return (
    <Suspense
      fallback={
        <ScrollArea className="flex-1">
          <div className="p-8 bg-background">
            <div className="mb-8 h-24" />
            <div className="flex gap-2 mb-6 h-10" />
            <LeadTableSkeleton />
          </div>
        </ScrollArea>
      }
    >
      <LeadsContent />
    </Suspense>
  );
}
