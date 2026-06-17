"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { Button } from "@/components/ui/Button";
import { Pagination } from "@/components/ui/Pagination";
import { toast } from "@/components/ui/use-toast";
import { DEFAULT_PAGE_SIZE, paginate } from "@/lib/pagination";
import {
  useDraftReplyMutation,
  useGetThreadQuery,
  useGetThreadsQuery,
  useSendReplyMutation,
} from "@/store/outreachApi";

type InboxFilter = "all" | "unread" | "archived";
const THREAD_PAGE_SIZE = 12;

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
  const [threadPage, setThreadPage] = useState(1);
  const [mobileShowDetail, setMobileShowDetail] = useState(false);

  const { data: threads = [], isLoading, error } = useGetThreadsQuery({ filter });
  const { data: threadDetail } = useGetThreadQuery(selectedId!, { skip: !selectedId });
  const [draftReply, { isLoading: drafting }] = useDraftReplyMutation();
  const [sendReply, { isLoading: sending }] = useSendReplyMutation();

  useEffect(() => {
    setThreadPage(1);
    setSelectedId(null);
    setMobileShowDetail(false);
  }, [filter]);

  const pagedThreads = useMemo(
    () => paginate(threads, threadPage, THREAD_PAGE_SIZE),
    [threads, threadPage]
  );

  const selected = useMemo(
    () => threads.find((t) => t.id === selectedId) ?? null,
    [threads, selectedId]
  );

  const messages = threadDetail?.messages ?? [];

  const selectThread = (id: number) => {
    setSelectedId(id);
    setReplyDraft("");
    setMobileShowDetail(true);
  };

  const handleAiDraft = async () => {
    if (!selectedId) return;
    try {
      const res = await draftReply(selectedId).unwrap();
      setReplyDraft(res.body);
      toast({ id: "inbox-draft", title: "Draft ready", description: "Review and send when ready." });
    } catch {
      toast({
        id: "inbox-draft",
        title: "Draft failed",
        description: "No inbound message or API error.",
        variant: "destructive",
      });
    }
  };

  const handleSend = async () => {
    if (!selectedId || !replyDraft.trim()) return;
    try {
      await sendReply({ threadId: selectedId, body: replyDraft.trim() }).unwrap();
      setReplyDraft("");
      toast({ id: "inbox-send", title: "Reply sent" });
    } catch {
      toast({ id: "inbox-send", title: "Send failed", variant: "destructive" });
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 bg-background">
      <div className="px-4 sm:px-6 py-3 border-b border-primary/10 flex items-center gap-4 shrink-0 overflow-x-auto">
        <div className="flex bg-primary/5 p-1 rounded-lg shrink-0">
          {(["all", "unread", "archived"] as const).map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setFilter(f)}
              className={`px-3 sm:px-4 py-1.5 text-xs font-bold rounded capitalize transition-colors ${
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
        <div
          className={`${
            mobileShowDetail ? "hidden md:flex" : "flex"
          } w-full md:w-80 lg:w-96 border-r border-primary/10 shrink-0 flex-col min-h-0`}
        >
          <ScrollArea className="flex-1">
            <div className="flex flex-col">
              {isLoading && <p className="p-4 text-slate-500 text-sm">Loading…</p>}
              {error != null && <p className="p-4 text-red-400 text-sm">Failed to load threads.</p>}
              {!isLoading && error == null && threads.length === 0 && (
                <p className="p-4 text-slate-500 text-sm">No conversations yet.</p>
              )}
              {pagedThreads.items.map((conv) => (
                <button
                  key={conv.id}
                  type="button"
                  onClick={() => selectThread(conv.id)}
                  className={`p-4 border-b border-primary/10 text-left cursor-pointer transition-colors relative ${
                    selectedId === conv.id ? "bg-primary/10" : "hover:bg-primary/5"
                  }`}
                >
                  {selectedId === conv.id && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                  )}
                  <div className="flex justify-between items-start mb-1 gap-2">
                    <span className={`font-bold text-sm ${conv.unread ? "text-slate-100" : "text-slate-300"}`}>
                      {conv.name || conv.to_email || `Lead #${conv.lead_id}`}
                    </span>
                    <span className="text-[10px] font-medium text-slate-500 shrink-0">
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
          <Pagination
            page={pagedThreads.currentPage}
            totalPages={pagedThreads.totalPages}
            total={pagedThreads.total}
            from={pagedThreads.from}
            to={pagedThreads.to}
            onPageChange={setThreadPage}
            label="threads"
          />
        </div>

        <div
          className={`${
            mobileShowDetail ? "flex" : "hidden md:flex"
          } flex-1 flex-col min-w-0`}
        >
          {selected ? (
            <>
              <div className="p-4 border-b border-primary/10 flex items-center justify-between shrink-0 gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <button
                    type="button"
                    className="md:hidden p-1 text-slate-500 hover:text-primary"
                    aria-label="Back to threads"
                    onClick={() => setMobileShowDetail(false)}
                  >
                    <span className="material-symbols-outlined">arrow_back</span>
                  </button>
                  <div className="min-w-0">
                    <h3 className="font-bold text-slate-100 truncate">
                      {selected.name || selected.to_email}
                    </h3>
                    <p className="text-xs text-slate-500 truncate">{selected.company_name}</p>
                  </div>
                </div>
                <Link
                  href={`/leads/${selected.lead_id}`}
                  className="text-xs text-primary font-bold hover:underline shrink-0"
                >
                  View lead
                </Link>
              </div>

              <ScrollArea className="flex-1">
                <div className="p-4 sm:p-6 space-y-6">
                  {messages.map((msg) =>
                    msg.direction === "inbound" ? (
                      <div key={msg.id} className="flex items-end gap-3 max-w-[90%] sm:max-w-[80%]">
                        <div className="bg-primary/10 text-slate-100 p-3 sm:p-4 rounded-xl rounded-bl-none border border-primary/5">
                          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{msg.body}</p>
                        </div>
                        <span className="text-[10px] text-slate-500 shrink-0">{formatTime(msg.sent_at)}</span>
                      </div>
                    ) : (
                      <div key={msg.id} className="flex flex-row-reverse items-end gap-3 max-w-[90%] sm:max-w-[80%] ml-auto">
                        <div className="bg-primary text-primary-foreground p-3 sm:p-4 rounded-xl rounded-br-none">
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.body}</p>
                        </div>
                        <span className="text-[10px] text-slate-500 shrink-0">{formatTime(msg.sent_at)}</span>
                      </div>
                    )
                  )}
                </div>
              </ScrollArea>

              <div className="p-4 sm:p-6 border-t border-primary/10 shrink-0">
                <div className="flex flex-col gap-3 bg-primary/5 border border-primary/10 rounded-xl p-3">
                  <textarea
                    className="w-full bg-transparent border-none focus:ring-0 resize-none text-sm text-slate-100 placeholder:text-slate-500 min-h-[80px] focus:outline-none"
                    placeholder="Write a reply..."
                    rows={3}
                    value={replyDraft}
                    onChange={(e) => setReplyDraft(e.target.value)}
                  />
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-t border-primary/10 pt-3">
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
            <div className="flex-1 flex items-center justify-center text-slate-500 p-6 text-center">
              Select a conversation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
