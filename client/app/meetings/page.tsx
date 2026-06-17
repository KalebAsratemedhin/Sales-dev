"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MonitorsLayout } from "@/components/features/MonitorsLayout";
import { Pagination } from "@/components/ui/Pagination";
import { DEFAULT_PAGE_SIZE } from "@/lib/pagination";
import { useGetMeetingsQuery, useGetStatsQuery } from "@/store/outreachApi";

type MeetingFilter = "upcoming" | "past";

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

export default function MeetingsPage() {
  const [filter, setFilter] = useState<MeetingFilter>("upcoming");
  const [page, setPage] = useState(1);
  const { data: stats, isLoading: statsLoading } = useGetStatsQuery();
  const { data: meetingsData, isLoading, error } = useGetMeetingsQuery({
    when: filter,
    page,
    page_size: DEFAULT_PAGE_SIZE,
  });

  useEffect(() => {
    setPage(1);
  }, [filter]);

  const meetings = meetingsData?.items ?? [];
  const from = meetingsData && meetingsData.total > 0 ? (meetingsData.page - 1) * meetingsData.page_size + 1 : 0;
  const to = meetingsData ? Math.min(meetingsData.page * meetingsData.page_size, meetingsData.total) : 0;

  const monitorStats = stats
    ? [
        {
          label: "Upcoming",
          value: String(stats.meetings_upcoming),
          sub: `${stats.meetings_today} TODAY`,
          subColor: "primary" as const,
          icon: "event_upcoming",
        },
        {
          label: "Past",
          value: String(stats.meetings_past),
          sub: "COMPLETED",
          subColor: "muted" as const,
          icon: "history",
        },
        {
          label: "Next meeting",
          value: stats.next_meeting
            ? new Date(stats.next_meeting.start_at).toLocaleTimeString(undefined, {
                hour: "2-digit",
                minute: "2-digit",
              })
            : "—",
          sub: stats.next_meeting?.lead_name || stats.next_meeting?.lead_email || "NONE SCHEDULED",
          subColor: stats.next_meeting ? ("green" as const) : ("muted" as const),
          icon: "calendar_month",
        },
        {
          label: "Threads",
          value: String(stats.threads_total),
          sub: `${stats.unread_threads} UNREAD`,
          subColor: stats.unread_threads > 0 ? ("red" as const) : ("green" as const),
          icon: "inbox",
        },
      ]
    : undefined;

  return (
    <MonitorsLayout title="Meetings" titleHighlight="Overview" stats={monitorStats} isLoading={statsLoading}>
      <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-primary/20 flex flex-wrap items-center justify-between gap-4">
          <h2 className="text-sm font-bold uppercase tracking-widest text-primary">Scheduled meetings</h2>
          <div className="flex bg-primary/5 p-1 rounded-lg">
            {(["upcoming", "past"] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                className={`px-4 py-1.5 text-xs font-bold rounded capitalize transition-colors ${
                  filter === f
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-slate-500 hover:text-primary"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {isLoading && <p className="p-6 text-slate-500 text-sm">Loading meetings…</p>}
        {error != null && <p className="p-6 text-red-400 text-sm">Failed to load meetings.</p>}
        {!isLoading && error == null && meetings.length === 0 && (
          <p className="p-6 text-slate-500 text-sm">
            No {filter} meetings yet. Bookings appear here when the scheduling agent creates calendar events.
          </p>
        )}

        {!isLoading && meetings.length > 0 && (
          <>
            <div className="divide-y divide-primary/10">
              {meetings.map((meeting) => (
                <div key={meeting.id} className="p-4 sm:p-6 hover:bg-primary/5 transition-colors">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                    <div className="min-w-0">
                      <p className="font-bold text-slate-100">{meeting.title || "Meeting"}</p>
                      <p className="text-sm text-slate-500 mt-1">
                        {meeting.lead_name || meeting.lead_email || `Lead #${meeting.lead_id}`}
                        {meeting.company_name ? ` · ${meeting.company_name}` : ""}
                      </p>
                      <p className="text-sm text-primary mt-2">{formatMeetingTime(meeting.start_at)}</p>
                      <p className="text-xs text-slate-500 mt-1">{meeting.duration_minutes} minutes</p>
                    </div>
                    <div className="flex flex-wrap gap-3">
                      <Link
                        href={`/leads/${meeting.lead_id}`}
                        className="text-xs text-primary font-bold hover:underline"
                      >
                        View lead
                      </Link>
                      {meeting.html_link ? (
                        <a
                          href={meeting.html_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary font-bold hover:underline"
                        >
                          Open in Google Calendar
                        </a>
                      ) : null}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {meetingsData ? (
              <Pagination
                page={meetingsData.page}
                totalPages={meetingsData.total_pages}
                total={meetingsData.total}
                from={from}
                to={to}
                onPageChange={setPage}
                label="meetings"
              />
            ) : null}
          </>
        )}
      </div>
    </MonitorsLayout>
  );
}
