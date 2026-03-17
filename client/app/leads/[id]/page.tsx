"use client";

import { useParams } from "next/navigation";
import { useGetLeadQuery } from "@/store/leadsApi";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ScrollArea } from "@/components/ui/ScrollArea";

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function domainFromUrl(url: string): string {
  if (!url?.trim()) return "—";
  try {
    const u = new URL(url.startsWith("http") ? url : `https://${url}`);
    return u.hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

/** Placeholder score 0–100 from lead id. */
function scoreFromLeadId(id: number): number {
  return Math.min(100, 50 + (id % 51));
}

export default function LeadDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data: lead, isLoading, error } = useGetLeadQuery(id, { skip: !id });

  if (isLoading || !lead) {
    return (
      <div className="flex-1 p-8">
        <h1 className="text-2xl font-bold text-slate-100">Lead</h1>
        {isLoading && <p className="text-slate-500 mt-2">Loading…</p>}
        {error && <p className="text-red-400 mt-2">Failed to load lead.</p>}
      </div>
    );
  }

  const score = scoreFromLeadId(lead.id);
  const companyDomain = domainFromUrl(lead.company_website || "");

  return (
    <ScrollArea className="flex-1">
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Hero / Summary */}
          <div className="flex flex-col md:flex-row gap-8 items-start justify-between">
            <div className="flex gap-6 items-center">
              <div className="relative">
                <div className="size-24 rounded-lg bg-primary/10 border-2 border-primary overflow-hidden flex items-center justify-center text-primary text-2xl font-bold">
                  {(lead.name || lead.email).slice(0, 2).toUpperCase()}
                </div>
                <div className="absolute -bottom-2 -right-2 px-2 py-0.5 bg-primary text-primary-foreground text-[10px] font-bold uppercase rounded">
                  High Intent
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-100">
                  {lead.name || lead.email}
                </h1>
                <p className="text-slate-500 flex items-center gap-2 mt-1">
                  <span className="material-symbols-outlined text-sm">business</span>
                  {lead.company_name ? `${lead.company_name}` : "—"}
                </p>
                <div className="mt-2 flex gap-2 flex-wrap">
                  <span className="px-2 py-0.5 bg-primary/20 text-primary text-xs font-bold rounded flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs">verified</span>
                    Verified
                  </span>
                  <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-xs font-bold rounded flex items-center gap-1">
                    <span className="material-symbols-outlined text-xs">mail</span>
                    Responsive
                  </span>
                </div>
              </div>
            </div>
            <div className="flex gap-4">
              <button
                type="button"
                className="px-6 py-2.5 bg-primary/10 text-primary font-bold text-sm rounded border border-transparent hover:border-primary transition-all flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">edit</span>
                EDIT PROFILE
              </button>
              <button
                type="button"
                className="px-6 py-2.5 bg-primary text-primary-foreground font-bold text-sm rounded hover:opacity-90 transition-all flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">bolt</span>
                CONVERT LEAD
              </button>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-primary/5 border border-primary/20 p-5 rounded-lg">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
                Lead Score
              </p>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-primary">{score}</span>
                <span className="text-xs text-emerald-500 font-bold mb-1">+4pt</span>
              </div>
            </div>
            <div className="bg-primary/5 border border-primary/20 p-5 rounded-lg">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
                Engagement Rate
              </p>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-slate-100">84%</span>
                <span className="text-xs text-emerald-500 font-bold mb-1">+12%</span>
              </div>
            </div>
            <div className="bg-primary/5 border border-primary/20 p-5 rounded-lg">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
                Email Opens
              </p>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-slate-100">—</span>
                <span className="text-xs text-slate-500 font-bold mb-1">total</span>
              </div>
            </div>
            <div className="bg-primary/5 border border-primary/20 p-5 rounded-lg">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
                Avg Response
              </p>
              <div className="flex items-end gap-2">
                <span className="text-4xl font-bold text-slate-100">—</span>
                <span className="text-xs text-slate-500 font-bold mb-1">—</span>
              </div>
            </div>
          </div>

          {/* Details & Timeline Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left: Info Column */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-background/40 border border-primary/20 rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-primary/20 bg-primary/5 flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-sm">info</span>
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-100">
                    Technical Profile
                  </h3>
                </div>
                <div className="p-6 space-y-4">
                  <div className="space-y-1">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                      Company Domain
                    </p>
                    <p className="text-sm font-medium flex items-center justify-between text-slate-100">
                      {companyDomain}
                      {lead.company_website && (
                        <a
                          href={lead.company_website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="material-symbols-outlined text-xs text-primary"
                          aria-label="Open website"
                        >
                          link
                        </a>
                      )}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                      Industry Vertical
                    </p>
                    <p className="text-sm font-medium text-slate-300">—</p>
                  </div>
                  <div className="space-y-1 pt-4 border-t border-primary/10">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                      Primary Contact
                    </p>
                    <p className="text-sm font-medium text-slate-100">{lead.email}</p>
                  </div>
                </div>
              </div>
              <div className="bg-background/40 border border-primary/20 rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-primary/20 bg-primary/5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-sm">
                      bookmark
                    </span>
                    <h3 className="font-bold text-sm uppercase tracking-wider text-slate-100">
                      Internal Tags
                    </h3>
                  </div>
                  <button
                    type="button"
                    className="material-symbols-outlined text-xs text-slate-400 hover:text-primary"
                    aria-label="Add tag"
                  >
                    add_circle
                  </button>
                </div>
                <div className="p-6 flex flex-wrap gap-2">
                  <StatusBadge status={lead.status} className="border border-primary/30" />
                </div>
              </div>
            </div>

            {/* Right: Timeline Column */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between mb-2 px-2">
                <h3 className="font-bold text-sm uppercase tracking-widest flex items-center gap-2 text-slate-100">
                  <span className="material-symbols-outlined text-primary">history</span>
                  Activity Timeline
                </h3>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="px-3 py-1 bg-primary/20 text-primary text-xs font-bold rounded"
                  >
                    All
                  </button>
                  <button
                    type="button"
                    className="px-3 py-1 bg-white/5 text-slate-400 text-xs font-bold rounded hover:bg-primary/5"
                  >
                    Communications
                  </button>
                  <button
                    type="button"
                    className="px-3 py-1 bg-white/5 text-slate-400 text-xs font-bold rounded hover:bg-primary/5"
                  >
                    System
                  </button>
                </div>
              </div>
              <div className="space-y-4 relative before:absolute before:left-[19px] before:top-2 before:bottom-2 before:w-0.5 before:bg-primary/10">
                <div className="relative pl-12">
                  <div className="absolute left-0 top-0 size-10 bg-primary/20 border border-primary rounded-full flex items-center justify-center z-10">
                    <span className="material-symbols-outlined text-primary text-lg">mail</span>
                  </div>
                  <div className="bg-primary/5 border border-primary/20 p-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-sm font-bold text-slate-100">Lead added</p>
                      <span className="text-[10px] font-medium text-slate-500 uppercase">
                        {formatDate(lead.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 leading-relaxed">
                      Lead created from {lead.source || "pipeline"}. Last updated{" "}
                      {formatDate(lead.updated_at)}.
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex justify-center pt-4">
                <button
                  type="button"
                  className="px-4 py-2 text-[10px] font-bold tracking-widest text-slate-500 border border-primary/20 rounded hover:bg-primary/5 transition-colors"
                >
                  FETCH OLDER RECORDS
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>
  );
}
