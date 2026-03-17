"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/ScrollArea";

type InboxFilter = "all" | "unread" | "archived";

const MOCK_CONVERSATIONS = [
  {
    id: "1",
    name: "Alex Rivers",
    time: "10:42 AM",
    subject: "CRM Integration Proposal",
    preview:
      "Hi there, I saw your proposal regarding the new CRM integration. Can we hop on a quick call...",
    unread: true,
  },
  {
    id: "2",
    name: "Sarah Jenkins",
    time: "Yesterday",
    subject: "Quarterly Review Data",
    preview:
      "The latest figures for the Q3 review are attached. Let me know if you need any adjustments...",
    unread: true,
  },
  {
    id: "3",
    name: "Michael Chen",
    time: "Oct 12",
    subject: "Re: Follow up meeting",
    preview:
      "Thanks for the update. I'll check with the team and get back to you by Monday morning.",
    unread: false,
  },
  {
    id: "4",
    name: "Elena Rodriguez",
    time: "Oct 11",
    subject: "Contract Signature Pending",
    preview:
      "We are still waiting on the final signature from your legal department for the Enterprise plan.",
    unread: false,
  },
];

const MOCK_MESSAGES = [
  { id: "m1", from: "lead", text: "Hi there, I saw your proposal regarding the new CRM integration. Can we hop on a quick call tomorrow at 10 AM? I have some specific questions about the data migration phase.", time: "10:42 AM" },
  { id: "m2", from: "us", text: "Hi Alex! Tomorrow at 10 AM works perfectly for me. I'll prepare the technical documentation for the data migration steps so we can dive deep into that.", time: "10:45 AM", read: true },
  { id: "m3", from: "lead", text: "That sounds great. I'll invite our CTO to the meeting as well. Talk tomorrow!", time: "10:48 AM" },
];

export default function InboxPage() {
  const [filter, setFilter] = useState<InboxFilter>("all");
  const [selectedId, setSelectedId] = useState<string | null>("1");
  const [replyDraft, setReplyDraft] = useState("");

  const selected = MOCK_CONVERSATIONS.find((c) => c.id === selectedId);

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
        {/* Message List */}
        <ScrollArea className="w-80 border-r border-primary/10 shrink-0 h-full">
          <div className="flex flex-col">
          {MOCK_CONVERSATIONS.map((conv) => (
            <button
              key={conv.id}
              type="button"
              onClick={() => setSelectedId(conv.id)}
              className={`p-4 border-b border-primary/10 text-left cursor-pointer transition-colors relative ${
                selectedId === conv.id ? "bg-primary/10" : "hover:bg-primary/5"
              }`}
            >
              {selectedId === conv.id && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
              )}
              <div className="flex justify-between items-start mb-1">
                <span
                  className={`font-bold text-sm ${selectedId === conv.id ? "text-slate-100" : "text-slate-300"}`}
                >
                  {conv.name}
                </span>
                <span
                  className={`text-[10px] font-medium ${selectedId === conv.id ? "text-primary" : "text-slate-500"}`}
                >
                  {conv.time}
                </span>
              </div>
              <p
                className={`text-xs font-bold truncate mb-1 ${selectedId === conv.id ? "text-slate-100" : "text-slate-300"}`}
              >
                {conv.subject}
              </p>
              <p className="text-xs text-slate-500 line-clamp-2">{conv.preview}</p>
            </button>
          ))}
          </div>
        </ScrollArea>

        {/* Chat View */}
        <div className="flex-1 flex flex-col min-w-0">
          {selected ? (
            <>
              <div className="p-4 border-b border-primary/10 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary font-bold shrink-0">
                    {selected.name.slice(0, 2)}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-100">{selected.name}</h3>
                    <p className="text-xs text-primary font-medium flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                      Active Now
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="p-2 text-slate-500 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                    aria-label="Call"
                  >
                    <span className="material-symbols-outlined">call</span>
                  </button>
                  <button
                    type="button"
                    className="p-2 text-slate-500 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                    aria-label="Video"
                  >
                    <span className="material-symbols-outlined">videocam</span>
                  </button>
                  <button
                    type="button"
                    className="p-2 text-slate-500 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                    aria-label="More"
                  >
                    <span className="material-symbols-outlined">more_vert</span>
                  </button>
                </div>
              </div>

              <ScrollArea className="flex-1">
              <div className="p-6 space-y-6">
                <div className="flex items-center justify-center">
                  <div className="h-px flex-1 bg-primary/10" />
                  <span className="px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                    Today
                  </span>
                  <div className="h-px flex-1 bg-primary/10" />
                </div>
                {MOCK_MESSAGES.map((msg) =>
                  msg.from === "lead" ? (
                    <div key={msg.id} className="flex items-end gap-3 max-w-[80%]">
                      <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary text-xs font-bold shrink-0">
                        {selected.name.slice(0, 2)}
                      </div>
                      <div className="flex flex-col gap-1">
                        <div className="bg-primary/10 text-slate-100 p-4 rounded-xl rounded-bl-none border border-primary/5">
                          <p className="text-sm leading-relaxed">{msg.text}</p>
                        </div>
                        <span className="text-[10px] text-slate-500 ml-1">{msg.time}</span>
                      </div>
                    </div>
                  ) : (
                    <div
                      key={msg.id}
                      className="flex flex-row-reverse items-end gap-3 max-w-[80%] ml-auto"
                    >
                      <div className="flex flex-col gap-1 items-end">
                        <div className="bg-primary text-primary-foreground p-4 rounded-xl rounded-br-none shadow-lg shadow-primary/10">
                          <p className="text-sm font-medium leading-relaxed">{msg.text}</p>
                        </div>
                        <div className="flex items-center gap-1 mr-1">
                          <span className="text-[10px] text-slate-500">{msg.time}</span>
                          {"read" in msg && msg.read && (
                            <span className="material-symbols-outlined text-[12px] text-primary">
                              done_all
                            </span>
                          )}
                        </div>
                      </div>
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
                    aria-label="Reply"
                  />
                  <div className="flex items-center justify-between border-t border-primary/10 pt-3">
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        className="p-2 text-slate-500 hover:text-primary transition-colors"
                        aria-label="Attach"
                      >
                        <span className="material-symbols-outlined text-lg">attach_file</span>
                      </button>
                      <button
                        type="button"
                        className="p-2 text-slate-500 hover:text-primary transition-colors"
                        aria-label="Emoji"
                      >
                        <span className="material-symbols-outlined text-lg">mood</span>
                      </button>
                      <button
                        type="button"
                        className="p-2 text-slate-500 hover:text-primary transition-colors"
                        aria-label="Image"
                      >
                        <span className="material-symbols-outlined text-lg">image</span>
                      </button>
                      <div className="w-px h-4 bg-primary/20 mx-1" />
                      <button
                        type="button"
                        className="p-2 text-slate-500 hover:text-primary transition-colors flex items-center gap-1"
                      >
                        <span className="material-symbols-outlined text-lg">auto_fix</span>
                        <span className="text-xs font-bold uppercase tracking-tighter">
                          AI Draft
                        </span>
                      </button>
                    </div>
                    <button
                      type="button"
                      className="px-6 py-2 bg-primary text-primary-foreground font-bold rounded-lg flex items-center gap-2 hover:opacity-90 transition-opacity"
                    >
                      <span>Send Reply</span>
                      <span className="material-symbols-outlined text-sm">send</span>
                    </button>
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

        {/* Right Sidebar: Contact */}
        {selected && (
          <ScrollArea className="w-72 border-l border-primary/10 shrink-0 h-full bg-primary/5">
          <div className="flex flex-col">
            <div className="p-6 text-center border-b border-primary/10">
              <div className="w-20 h-20 rounded-full bg-primary/20 border-2 border-primary/30 mx-auto mb-3 flex items-center justify-center text-primary text-2xl font-bold">
                {selected.name.slice(0, 2)}
              </div>
              <h4 className="font-bold text-lg text-slate-100">{selected.name}</h4>
              <p className="text-xs text-slate-500 mb-4">Contact</p>
              <div className="flex justify-center gap-2 flex-wrap">
                <span className="px-2 py-1 bg-primary/20 text-primary text-[10px] font-bold rounded uppercase">
                  Enterprise
                </span>
                <span className="px-2 py-1 bg-green-500/20 text-green-500 text-[10px] font-bold rounded uppercase">
                  Hot Lead
                </span>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                  Contact Info
                </h5>
                <div className="space-y-3 text-sm text-slate-300">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary text-lg">mail</span>
                    <span>—</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary text-lg">phone</span>
                    <span>—</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary text-lg">
                      location_on
                    </span>
                    <span>—</span>
                  </div>
                </div>
              </div>
              <div>
                <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                  Recent Notes
                </h5>
                <div className="p-3 bg-background rounded-lg border border-primary/10">
                  <p className="text-xs text-slate-400 leading-relaxed italic">
                    Wire to handle-reply and thread APIs for real data.
                  </p>
                </div>
              </div>
              <div>
                <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
                  Activity Timeline
                </h5>
                <div className="space-y-4">
                  <div className="flex gap-3">
                    <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[12px] text-primary-foreground">
                        mail
                      </span>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-300">Email Sent</p>
                      <p className="text-[10px] text-slate-500">—</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </ScrollArea>
        )}
      </div>
    </div>
  );
}
