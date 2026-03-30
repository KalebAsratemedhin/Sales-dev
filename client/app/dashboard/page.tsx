"use client";

import Link from "next/link";
import { useGetLeadsQuery } from "@/store/leadsApi";
import { ScrollArea } from "@/components/ui/ScrollArea";

const STATUS_LABELS: Record<string, string> = {
  new: "New",
  researched: "Researched",
  emailed: "Emailed",
  replied: "Replied",
  meeting_booked: "Meeting booked",
  follow_up_required: "Follow-up required",
};

export default function DashboardPage() {
  const { data: leads = [], isLoading, error } = useGetLeadsQuery();

  const total = leads.length;
  const byStatus = leads.reduce<Record<string, number>>((acc, lead) => {
    acc[lead.status] = (acc[lead.status] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <ScrollArea className="flex-1">
      <div className="p-8">
        <div className="space-y-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
            <p className="text-slate-500 mt-1">
              Monitor leads, research, outreach, and inbox from the sidebar.
            </p>
          </div>

          {isLoading && (
            <p className="text-slate-500 text-sm">Loading…</p>
          )}
          {error && (
            <p className="text-red-400 text-sm">Failed to load leads.</p>
          )}
          {!isLoading && !error && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Link
                  href="/leads"
                  className="bg-primary/5 border border-primary/20 rounded-lg p-5 hover:bg-primary/10 transition-colors"
                >
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
                    Total leads
                  </p>
                  <p className="text-3xl font-bold text-primary">{total}</p>
                </Link>
                {(["new", "researched", "emailed"] as const).map((status) => (
                  <Link
                    key={status}
                    href={`/leads?status=${status}`}
                    className="bg-primary/5 border border-primary/20 rounded-lg p-5 hover:bg-primary/10 transition-colors"
                  >
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
                      {STATUS_LABELS[status] ?? status}
                    </p>
                    <p className="text-3xl font-bold text-slate-100">
                      {byStatus[status] ?? 0}
                    </p>
                  </Link>
                ))}
              </div>
              <div className="flex flex-wrap gap-4">
                <Link
                  href="/leads"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  View all leads
                </Link>
                <Link
                  href="/settings"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  Configuration
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </ScrollArea>
  );
}
