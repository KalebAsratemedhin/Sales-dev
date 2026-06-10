"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useGetLeadQuery, useSendOutreachMutation } from "@/store/leadsApi";
import { Button } from "@/components/ui/Button";
import { toast } from "@/components/ui/use-toast";
import { useGetResearchByLeadQuery } from "@/store/researchApi";
import { useGetThreadsQuery } from "@/store/outreachApi";
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

export default function LeadDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data: lead, isLoading, error } = useGetLeadQuery(id, { skip: !id });
  const { data: research } = useGetResearchByLeadQuery(id, { skip: !id });
  const { data: threads = [] } = useGetThreadsQuery({ lead_id: id }, { skip: !id });
  const [sendOutreach, { isLoading: sending }] = useSendOutreachMutation();

  const canSendOutreach = Boolean(research) && lead?.status === "researched" && !threads.length;

  const handleSendOutreach = async () => {
    try {
      await sendOutreach(id).unwrap();
      toast({ title: "Outreach queued", description: "Email send is in progress." });
    } catch {
      toast({ title: "Send failed", description: "Could not queue outreach.", variant: "destructive" });
    }
  };

  if (isLoading || !lead) {
    return (
      <div className="flex-1 p-8">
        <h1 className="text-2xl font-bold text-slate-100">Lead</h1>
        {isLoading && <p className="text-slate-500 mt-2">Loading…</p>}
        {error != null && <p className="text-red-400 mt-2">Failed to load lead.</p>}
      </div>
    );
  }

  const companyDomain = domainFromUrl(lead.company_website || "");
  const thread = threads[0];

  return (
    <ScrollArea className="flex-1">
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex flex-col md:flex-row gap-8 items-start justify-between">
            <div className="flex gap-6 items-center">
              <div className="size-24 rounded-lg bg-primary/10 border-2 border-primary flex items-center justify-center text-primary text-2xl font-bold">
                {(lead.name || lead.email).slice(0, 2).toUpperCase()}
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-100">
                  {lead.name || lead.email}
                </h1>
                <p className="text-slate-500 mt-1">{lead.company_name || "—"}</p>
                <div className="mt-2">
                  <StatusBadge status={lead.status} />
                </div>
              </div>
            </div>
            {thread && (
              <Link href="/inbox" className="text-sm text-primary font-bold hover:underline">
                Open inbox thread
              </Link>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-background/40 border border-primary/20 rounded-lg p-6 space-y-4">
                <h3 className="font-bold text-sm uppercase tracking-wider text-slate-100">Contact</h3>
                <p className="text-sm text-slate-300">{lead.email}</p>
                <p className="text-sm text-slate-300">{companyDomain}</p>
                {lead.company_website && (
                  <a
                    href={lead.company_website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    Visit website
                  </a>
                )}
                <p className="text-xs text-slate-500">Source: {lead.source}</p>
                <p className="text-xs text-slate-500">Created {formatDate(lead.created_at)}</p>
              </div>
            </div>

            <div className="lg:col-span-2 space-y-6">
              <div className="bg-background/40 border border-primary/20 rounded-lg p-6">
                <h3 className="font-bold text-sm uppercase tracking-wider text-slate-100 mb-4">
                  Research
                </h3>
                {research ? (
                  <div className="space-y-3 text-sm text-slate-300">
                    <p className="leading-relaxed">{research.website_summary || "—"}</p>
                    {research.pain_points?.length > 0 && (
                      <div>
                        <p className="text-xs font-bold text-slate-500 uppercase mb-1">Pain points</p>
                        <ul className="list-disc pl-5 space-y-1">
                          {research.pain_points.map((p, i) => (
                            <li key={i}>{p}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {research.use_cases?.length > 0 && (
                      <div>
                        <p className="text-xs font-bold text-slate-500 uppercase mb-1">Use cases</p>
                        <ul className="list-disc pl-5 space-y-1">
                          {research.use_cases.map((u, i) => (
                            <li key={i}>{u}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm">
                    {lead.company_website ? "Research pending or not started." : "Add a company website to trigger research."}
                  </p>
                )}
                {canSendOutreach && (
                  <div className="mt-4 pt-4 border-t border-primary/10">
                    <p className="text-xs text-slate-500 mb-3">
                      Research is ready but the outreach email was not sent (e.g. SMTP or network error).
                    </p>
                    <Button onClick={handleSendOutreach} disabled={sending}>
                      {sending ? "Sending…" : "Send outreach email"}
                    </Button>
                  </div>
                )}
              </div>

              <div className="bg-background/40 border border-primary/20 rounded-lg p-6">
                <h3 className="font-bold text-sm uppercase tracking-wider text-slate-100 mb-4">
                  Email history
                </h3>
                {thread ? (
                  <div className="space-y-2 text-sm">
                    <p className="text-slate-300 font-medium">{thread.subject}</p>
                    <p className="text-slate-500">{thread.message_count} messages · last {formatDate(thread.last_message_at)}</p>
                    <p className="text-slate-400 line-clamp-3">{thread.preview}</p>
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm">No outreach emails yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>
  );
}
