"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useGetLeadsQuery } from "@/store/leadsApi";
import { useGetActivityQuery, useGetStatsQuery } from "@/store/outreachApi";
import { initials } from "@/lib/initials";
import { DEFAULT_PAGE_SIZE } from "@/lib/pagination";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { Pagination } from "@/components/ui/Pagination";
import {
  GroupedActivityChart,
  HorizontalBarChart,
} from "@/components/features/dashboard/Charts";

const HIDDEN_STATUSES = new Set(["meeting_booked", "follow_up_required"]);

const PIPELINE_STAGES = [
  { key: "new", label: "Cold", colorClass: "bg-blue-400" },
  { key: "researched", label: "Warm", colorClass: "bg-orange-400" },
  { key: "emailed", label: "Contacted", colorClass: "bg-primary" },
  { key: "replied", label: "Hot", colorClass: "bg-red-400" },
] as const;

const subColorClasses = {
  green: "text-green-500",
  red: "text-red-500",
  primary: "text-primary",
  muted: "text-slate-500",
};

function formatMeetingTime(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function actionLabel(action: "sent" | "received") {
  return action === "sent" ? "Sent email" : "Received reply";
}

export default function DashboardPage() {
  const [activityPage, setActivityPage] = useState(1);
  const { data: leads = [], isLoading: leadsLoading, error: leadsError } = useGetLeadsQuery();
  const { data: outreach, isLoading: outreachLoading } = useGetStatsQuery();
  const { data: activity, isLoading: activityLoading } = useGetActivityQuery({
    page: activityPage,
    page_size: DEFAULT_PAGE_SIZE,
  });

  const isLoading = leadsLoading || outreachLoading;

  const visibleLeads = useMemo(
    () => leads.filter((lead) => !HIDDEN_STATUSES.has(lead.status)),
    [leads]
  );

  const byStatus = useMemo(
    () =>
      visibleLeads.reduce<Record<string, number>>((acc, lead) => {
        acc[lead.status] = (acc[lead.status] ?? 0) + 1;
        return acc;
      }, {}),
    [visibleLeads]
  );

  const total = visibleLeads.length;
  const pipelineCards = [
    { label: "Total leads", value: total, href: "/leads", sub: `${byStatus.new ?? 0} new` },
  ];

  const outreachCards = outreach
    ? [
        {
          label: "Email Threads",
          value: String(outreach.threads_total),
          sub: `${outreach.unread_threads} UNREAD`,
          subColor: outreach.unread_threads > 0 ? ("red" as const) : ("green" as const),
          icon: "radar",
        },
        {
          label: "Sent Today",
          value: String(outreach.outbound_today),
          sub: `${outreach.emails_outbound} TOTAL OUTBOUND`,
          subColor: "green" as const,
          icon: "target",
        },
        {
          label: "Replies Today",
          value: String(outreach.inbound_today),
          sub: `${outreach.emails_inbound} TOTAL INBOUND`,
          subColor: "primary" as const,
          icon: "speed",
        },
        {
          label: "Inbox",
          value: String(outreach.unread_threads),
          sub: "AWAITING REPLY",
          subColor: "primary" as const,
          icon: "token",
        },
      ]
    : [];

  const pipelineChart = PIPELINE_STAGES.map((stage) => ({
    label: stage.label,
    value: byStatus[stage.key] ?? 0,
    colorClass: stage.colorClass,
  }));

  const activityItems = activity?.items ?? [];
  const activityFrom =
    activity && activity.total > 0 ? (activity.page - 1) * activity.page_size + 1 : 0;
  const activityTo = activity ? Math.min(activity.page * activity.page_size, activity.total) : 0;

  return (
    <ScrollArea className="flex-1">
      <div className="p-4 sm:p-6 lg:p-8 space-y-6 lg:space-y-8">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-100">Dashboard</h1>
          <p className="text-slate-500 mt-1 text-sm sm:text-base">
            Pipeline trends, outreach volume, and recent activity.
          </p>
        </div>

        {isLoading && <p className="text-slate-500 text-sm">Loading…</p>}
        {leadsError != null && <p className="text-red-400 text-sm">Failed to load dashboard data.</p>}

        {!isLoading && !leadsError && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
              {pipelineCards.map((card) => (
                <Link
                  key={card.label}
                  href={card.href}
                  className="bg-primary/5 border border-primary/20 rounded-lg p-5 hover:bg-primary/10 transition-colors"
                >
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">{card.label}</p>
                  <p className="text-3xl font-bold text-primary">{card.value}</p>
                  <p className="text-xs text-slate-500 mt-2">{card.sub}</p>
                </Link>
              ))}
              {outreachCards.map((card) => (
                <div
                  key={card.label}
                  className="bg-primary/5 border border-primary/20 p-5 sm:p-6 rounded relative overflow-hidden group"
                >
                  <div className="absolute right-0 top-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                    <span className="material-symbols-outlined text-5xl sm:text-6xl">{card.icon}</span>
                  </div>
                  <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-1">{card.label}</p>
                  <h3 className="text-2xl sm:text-3xl font-bold text-slate-100">{card.value}</h3>
                  <div
                    className={`mt-4 flex items-center gap-2 text-xs font-bold ${subColorClasses[card.subColor]}`}
                  >
                    <span>{card.sub}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
                <div className="p-4 sm:p-5 border-b border-primary/20">
                  <h2 className="text-sm font-bold uppercase tracking-widest text-primary">Email activity</h2>
                  <p className="text-xs text-slate-500 mt-1">Sent vs received over the last 7 days</p>
                </div>
                <div className="p-4 sm:p-5">
                  <GroupedActivityChart data={outreach?.email_activity_7d ?? []} />
                </div>
              </div>

              <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
                <div className="p-4 sm:p-5 border-b border-primary/20 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-bold uppercase tracking-widest text-primary">Lead pipeline</h2>
                    <p className="text-xs text-slate-500 mt-1">Leads by stage</p>
                  </div>
                  <Link href="/leads" className="text-xs text-primary font-bold hover:underline shrink-0">
                    View leads
                  </Link>
                </div>
                <div className="p-4 sm:p-5">
                  <HorizontalBarChart items={pipelineChart} />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
                <div className="p-4 sm:p-5 border-b border-primary/20 flex items-center justify-between">
                  <h2 className="text-sm font-bold uppercase tracking-widest text-primary">Next meeting</h2>
                  <Link href="/meetings" className="text-xs text-primary font-bold hover:underline">
                    View all
                  </Link>
                </div>
                {outreach?.next_meeting ? (
                  <div className="p-4 sm:p-5 space-y-2">
                    <p className="font-bold text-slate-100">{outreach.next_meeting.title || "Meeting"}</p>
                    <p className="text-sm text-slate-500">
                      {outreach.next_meeting.lead_name || outreach.next_meeting.lead_email}
                    </p>
                    <p className="text-sm text-primary">{formatMeetingTime(outreach.next_meeting.start_at)}</p>
                    {outreach.next_meeting.html_link ? (
                      <a
                        href={outreach.next_meeting.html_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block text-xs text-primary font-bold hover:underline"
                      >
                        Open in Google Calendar
                      </a>
                    ) : null}
                  </div>
                ) : (
                  <p className="p-4 sm:p-5 text-slate-500 text-sm">No upcoming meetings scheduled.</p>
                )}
              </div>

              <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
                <div className="p-4 sm:p-5 border-b border-primary/20">
                  <h2 className="text-sm font-bold uppercase tracking-widest text-primary">Recent activity</h2>
                </div>
                {activityLoading && <p className="p-4 sm:p-5 text-slate-500 text-sm">Loading activity…</p>}
                {!activityLoading && activityItems.length === 0 && (
                  <p className="p-4 sm:p-5 text-slate-500 text-sm">No outreach activity yet.</p>
                )}
                {!activityLoading && activityItems.length > 0 && (
                  <>
                    <div className="divide-y divide-primary/10">
                      {activityItems.map((line, i) => (
                        <div key={`${line.time}-${line.lead_id}-${i}`} className="px-4 sm:px-5 py-3 flex items-center gap-3 sm:gap-4">
                          <span className="text-slate-500 text-xs shrink-0 w-14 sm:w-16">{line.time}</span>
                          <Link
                            href={`/leads/${line.lead_id}`}
                            className="size-8 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary text-xs shrink-0 hover:bg-primary/20 transition-colors"
                          >
                            {initials(line.lead_name, line.lead_email)}
                          </Link>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm text-slate-100 font-medium truncate">
                              {line.lead_name || line.lead_email || `Lead #${line.lead_id}`}
                            </p>
                            <p
                              className={`text-xs font-bold ${
                                line.action === "sent" ? "text-green-500" : "text-primary"
                              }`}
                            >
                              {actionLabel(line.action)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                    {activity ? (
                      <Pagination
                        page={activity.page}
                        totalPages={activity.total_pages}
                        total={activity.total}
                        from={activityFrom}
                        to={activityTo}
                        onPageChange={setActivityPage}
                        label="activities"
                      />
                    ) : null}
                  </>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </ScrollArea>
  );
}
