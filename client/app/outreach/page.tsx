"use client";

import { MonitorsLayout } from "@/components/features/MonitorsLayout";
import { useGetStatsQuery } from "@/store/outreachApi";

export default function OutreachPage() {
  const { data: stats, isLoading } = useGetStatsQuery();

  const monitorStats = stats
    ? [
        {
          label: "Email Threads",
          value: String(stats.threads_total),
          sub: `${stats.unread_threads} UNREAD`,
          subColor: stats.unread_threads > 0 ? ("red" as const) : ("green" as const),
          icon: "radar",
        },
        {
          label: "Sent Today",
          value: String(stats.outbound_today),
          sub: `${stats.emails_outbound} TOTAL OUTBOUND`,
          subColor: "green" as const,
          icon: "target",
        },
        {
          label: "Replies Today",
          value: String(stats.inbound_today),
          sub: `${stats.emails_inbound} TOTAL INBOUND`,
          subColor: "primary" as const,
          icon: "speed",
        },
        {
          label: "Inbox",
          value: String(stats.unread_threads),
          sub: "AWAITING REPLY",
          subColor: "primary" as const,
          icon: "token",
        },
      ]
    : undefined;

  return (
    <MonitorsLayout
      title="Outreach"
      titleHighlight="Overview"
      stats={monitorStats}
      isLoading={isLoading}
    />
  );
}
