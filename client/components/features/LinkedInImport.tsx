"use client";

import { useState } from "react";
import { useSyncFromPostsMutation, useSyncFromProfileMutation } from "@/store/linkedinApi";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { toast } from "@/components/ui/use-toast";

type Mode = "posts" | "profile";

function parsePostUrls(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function errorMessage(err: unknown): string {
  const e = err as { data?: { error?: string; details?: unknown } };
  if (e?.data?.error && typeof e.data.error === "string") return e.data.error;
  return "Request failed. Try again.";
}

export function LinkedInImport() {
  const [mode, setMode] = useState<Mode>("posts");

  const [postUrlsText, setPostUrlsText] = useState("");
  const [personaPosts, setPersonaPosts] = useState("");

  const [profileUrl, setProfileUrl] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [maxScrolls, setMaxScrolls] = useState("10");
  const [personaProfile, setPersonaProfile] = useState("");

  const [syncPosts, { isLoading: loadingPosts }] = useSyncFromPostsMutation();
  const [syncProfile, { isLoading: loadingProfile }] = useSyncFromProfileMutation();

  const parseOptionalPersona = (raw: string): number | null | undefined => {
    const t = raw.trim();
    if (!t) return undefined;
    const n = Number(t);
    if (!Number.isFinite(n)) return undefined;
    return n;
  };

  const handleSyncPosts = async () => {
    const post_urls = parsePostUrls(postUrlsText);
    if (!post_urls.length) {
      toast({ title: "Add post URLs", description: "Enter at least one URL, one per line.", variant: "destructive" });
      return;
    }
    const persona_id = parseOptionalPersona(personaPosts);
    try {
      const { created, updated } = await syncPosts({
        post_urls,
        ...(persona_id !== undefined ? { persona_id } : {}),
      }).unwrap();
      toast({
        title: "Sync from posts complete",
        description: `Created ${created}, updated ${updated}.`,
      });
    } catch (err) {
      toast({ title: "Sync failed", description: errorMessage(err), variant: "destructive" });
    }
  };

  const handleSyncProfile = async () => {
    if (!profileUrl.trim()) {
      toast({ title: "Profile URL required", variant: "destructive" });
      return;
    }
    if (!startDate.trim() || !endDate.trim()) {
      toast({ title: "Date range required", description: "Use YYYY-MM-DD for start and end.", variant: "destructive" });
      return;
    }
    const ms = maxScrolls.trim() ? Number(maxScrolls) : 10;
    if (!Number.isFinite(ms) || ms < 1 || ms > 100) {
      toast({ title: "Invalid max scrolls", description: "Use a number from 1 to 100.", variant: "destructive" });
      return;
    }
    const persona_id = parseOptionalPersona(personaProfile);
    try {
      const { created, updated } = await syncProfile({
        profile_url: profileUrl.trim(),
        start_date: startDate.trim(),
        end_date: endDate.trim(),
        max_scrolls: ms,
        ...(persona_id !== undefined ? { persona_id } : {}),
      }).unwrap();
      toast({
        title: "Sync from profile complete",
        description: `Created ${created}, updated ${updated}.`,
      });
    } catch (err) {
      toast({ title: "Sync failed", description: errorMessage(err), variant: "destructive" });
    }
  };

  const busy = loadingPosts || loadingProfile;

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
            <span className="material-symbols-outlined text-sm">sync</span>
            <span>Import from LinkedIn</span>
          </div>
          <div className="flex rounded-lg border border-primary/20 p-0.5 bg-primary/5">
            <button
              type="button"
              onClick={() => setMode("posts")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-colors ${
                mode === "posts" ? "bg-primary text-primary-foreground" : "text-slate-400 hover:text-primary"
              }`}
            >
              Post URLs
            </button>
            <button
              type="button"
              onClick={() => setMode("profile")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-colors ${
                mode === "profile" ? "bg-primary text-primary-foreground" : "text-slate-400 hover:text-primary"
              }`}
            >
              Profile activity
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {mode === "posts" ? (
          <>
            <div>
              <Label htmlFor="postUrls">Post or activity URLs</Label>
              <textarea
                id="postUrls"
                rows={4}
                value={postUrlsText}
                onChange={(e) => setPostUrlsText(e.target.value)}
                placeholder={"One URL per line"}
                className="mt-1.5 w-full rounded-md border border-primary/20 bg-primary/5 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <div>
              <Label htmlFor="personaPosts">Persona ID (optional)</Label>
              <Input
                id="personaPosts"
                inputMode="numeric"
                value={personaPosts}
                onChange={(e) => setPersonaPosts(e.target.value)}
                placeholder="e.g. 1"
              />
            </div>
            <div className="flex justify-end">
              <Button onClick={handleSyncPosts} disabled={busy}>
                {loadingPosts ? "Syncing…" : "Sync posts"}
              </Button>
            </div>
          </>
        ) : (
          <>
            <div>
              <Label htmlFor="profileUrl">LinkedIn profile URL</Label>
              <Input
                id="profileUrl"
                type="url"
                value={profileUrl}
                onChange={(e) => setProfileUrl(e.target.value)}
                placeholder="https://www.linkedin.com/in/username/"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="startDate">Start date</Label>
                <Input id="startDate" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </div>
              <div>
                <Label htmlFor="endDate">End date</Label>
                <Input id="endDate" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="maxScrolls">Max activity scrolls</Label>
                <Input
                  id="maxScrolls"
                  inputMode="numeric"
                  value={maxScrolls}
                  onChange={(e) => setMaxScrolls(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="personaProfile">Persona ID (optional)</Label>
                <Input
                  id="personaProfile"
                  inputMode="numeric"
                  value={personaProfile}
                  onChange={(e) => setPersonaProfile(e.target.value)}
                  placeholder="e.g. 1"
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleSyncProfile} disabled={busy}>
                {loadingProfile ? "Syncing…" : "Sync profile"}
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
