"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { Button } from "@/components/ui/Button";
import { toast } from "@/components/ui/use-toast";
import {
  useDraftReplyMutation,
  useGetThreadQuery,
  useGetThreadsQuery,
  useSendReplyMutation,
} from "@/store/outreachApi";

type InboxFilter = "all" | "unread" | "archived";

function formatTime(iso: string) {
  try {
    const d = new Date(iso);
    const now = new Date();
    if (d.toDateString() === now.toDateString()) {
      return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
    }
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  } catch {
    return iso;
  }
}

export default function InboxPage() {
  const [filter, setFilter] = useState<InboxFilter>("all");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [replyDraft, setReplyDraft] = useState("");

  const { data: threads = [], isLoading, error } = useGetThreadsQuery({ filter });
  const { data: threadDetail } = useGetThreadQuery(selectedId!, { skip: !selectedId });
  const [draftReply, { isLoading: drafting }] = useDraftReplyMutation();
  const [sendReply, { isLoading: sending }] = useSendReplyMutation();

  const selected = useMemo(
    () => threads.find((t) => t.id === selectedId) ?? null,
    [threads, selectedId]
  );

  const messages = threadDetail?.messages ?? [];

  const handleAiDraft = async () => {
    if (!selectedId) return;
    try {
      const res = await draftReply(selectedId).unwrap();
      setReplyDraft(res.body);
      toast({ title: "Draft ready", description: "Review and send when ready." });
    } catch {
      toast({ title: "Draft failed", description: "No inbound message or API error.", variant: "destructive" });
    }
  };

  const handleSend = async () => {
    if (!selectedId || !replyDraft.trim()) return;
    try {
      await sendReply({ threadId: selectedId, body: replyDraft.trim() }).unwrap();
      setReplyDraft("");
      toast({ title: "Reply sent" });
    } catch {
      toast({ title: "Send failed", variant: "destructive" });
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 bg-background">
      <div className="px-6 py-3 border-b border-primary/10 flex items-center gap-4 shrink-0">
        <div className="flex bg-primary/5 p-1 rounded-lg">
          {(["all", "unread", "archived"] as const).map((f) => (
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

      <div className="flex flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="w-80 border-r border-primary/10 shrink-0 h-full">
          <div className="flex flex-col">
            {isLoading && <p className="p-4 text-slate-500 text-sm">Loading…</p>}
            {error != null && <p className="p-4 text-red-400 text-sm">Failed to load threads.</p>}
            {!isLoading && error == null && threads.length === 0 && (
              <p className="p-4 text-slate-500 text-sm">No conversations yet.</p>
            )}
            {threads.map((conv) => (
              <button
                key={conv.id}
                type="button"
                onClick={() => {
                  setSelectedId(conv.id);
                  setReplyDraft("");
                }}
                className={`p-4 border-b border-primary/10 text-left cursor-pointer transition-colors relative ${
                  selectedId === conv.id ? "bg-primary/10" : "hover:bg-primary/5"
                }`}
              >
                {selectedId === conv.id && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                )}
                <div className="flex justify-between items-start mb-1">
                  <span className={`font-bold text-sm ${conv.unread ? "text-slate-100" : "text-slate-300"}`}>
                    {conv.name || conv.to_email || `Lead #${conv.lead_id}`}
                  </span>
                  <span className="text-[10px] font-medium text-slate-500">
                    {formatTime(conv.last_message_at)}
                  </span>
                </div>
                <p className="text-xs font-bold truncate mb-1 text-slate-300">
                  {conv.subject || "(no subject)"}
                </p>
                <p className="text-xs text-slate-500 line-clamp-2">{conv.preview}</p>
              </button>
            ))}
          </div>
        </ScrollArea>

        <div className="flex-1 flex flex-col min-w-0">
          {selected ? (
            <>
              <div className="p-4 border-b border-primary/10 flex items-center justify-between shrink-0">
                <div>
                  <h3 className="font-bold text-slate-100">
                    {selected.name || selected.to_email}
                  </h3>
                  <p className="text-xs text-slate-500">{selected.company_name}</p>
                </div>
                <Link
                  href={`/leads/${selected.lead_id}`}
                  className="text-xs text-primary font-bold hover:underline"
                >
                  View lead
                </Link>
              </div>

              <ScrollArea className="flex-1">
                <div className="p-6 space-y-6">
                  {messages.map((msg) =>
                    msg.direction === "inbound" ? (
                      <div key={msg.id} className="flex items-end gap-3 max-w-[80%]">
                        <div className="bg-primary/10 text-slate-100 p-4 rounded-xl rounded-bl-none border border-primary/5">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.body}</p>
                        </div>
                        <span className="text-[10px] text-slate-500">{formatTime(msg.sent_at)}</span>
                      </div>
                    ) : (
                      <div key={msg.id} className="flex flex-row-reverse items-end gap-3 max-w-[80%] ml-auto">
                        <div className="bg-primary text-primary-foreground p-4 rounded-xl rounded-br-none">
                          <p className="text-sm whitespace-pre-wrap">{msg.body}</p>
                        </div>
                        <span className="text-[10px] text-slate-500">{formatTime(msg.sent_at)}</span>
                      </div>
                    )
                  )}
                </div>
              </ScrollArea>

              <div className="p-6 border-t border-primary/10 shrink-0">
                <div className="flex flex-col gap-3 bg-primary/5 border border-primary/10 rounded-xl p-3">
                  <textarea
                    className="w-full bg-transparent border-none focus:ring-0 resize-none text-sm text-slate-100 placeholder:text-slate-500 min-h-[80px] focus:outline-none"
                    placeholder="Write a reply..."
                    rows={3}
                    value={replyDraft}
                    onChange={(e) => setReplyDraft(e.target.value)}
                  />
                  <div className="flex items-center justify-between border-t border-primary/10 pt-3">
                    <Button variant="ghost" onClick={handleAiDraft} disabled={drafting}>
                      {drafting ? "Drafting…" : "AI Draft"}
                    </Button>
                    <Button onClick={handleSend} disabled={sending || !replyDraft.trim()}>
                      {sending ? "Sending…" : "Send Reply"}
                    </Button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-500">
              Select a conversation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
