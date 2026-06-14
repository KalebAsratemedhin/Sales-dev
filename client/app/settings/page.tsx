"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  useGetProductDocsQuery,
  useGetProfilePicQuery,
  useGetProfileQuery,
  useGetSettingsQuery,
  useLazyGetProductDocFileQuery,
  useUpdateProfileMutation,
  useUpdateSettingsMutation,
  useUploadProductDocsMutation,
} from "@/store/authApi";
import {
  useDisconnectCalendarMutation,
  useDisconnectGmailMutation,
  useGetCalendarStatusQuery,
  useGetGmailStatusQuery,
  useLazyGetCalendarAuthUrlQuery,
  useLazyGetGmailAuthUrlQuery,
  useSyncGmailN8nMutation,
  useUpdateCalendarSettingsMutation,
} from "@/store/outreachApi";
import { useGetConfigQuery, useUpdateConfigMutation } from "@/store/outreachConfigApi";
import type { ProductDoc } from "@/types";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { Skeleton } from "@/components/ui/Skeleton";
import { toast } from "@/components/ui/use-toast";
import { PersonaManager } from "@/components/features/PersonaManager";
import { GOOGLE_CALENDAR_OAUTH_STATE_KEY } from "@/lib/googleCalendar";
import { GOOGLE_GMAIL_OAUTH_STATE_KEY } from "@/lib/googleGmail";

export default function SettingsPage() {
  const searchParams = useSearchParams();
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const { data: settings, isLoading: settingsLoading } = useGetSettingsQuery();
  const { data: outreachConfig, isLoading: configLoading } = useGetConfigQuery();
  const { data: calendarStatus, isLoading: calendarLoading } = useGetCalendarStatusQuery();
  const { data: gmailStatus, isLoading: gmailLoading } = useGetGmailStatusQuery();
  const { data: docsData, isLoading: docsLoading } = useGetProductDocsQuery();

  const [updateProfile, { isLoading: isSavingProfile }] = useUpdateProfileMutation();
  const [updateSettings, { isLoading: isSavingSettings }] = useUpdateSettingsMutation();
  const [updateOutreachConfig, { isLoading: isSavingOutreachConfig }] = useUpdateConfigMutation();
  const [uploadProductDocs, { isLoading: isUploadingDocs }] = useUploadProductDocsMutation();
  const [fetchCalendarAuthUrl] = useLazyGetCalendarAuthUrlQuery();
  const [fetchGmailAuthUrl] = useLazyGetGmailAuthUrlQuery();
  const [disconnectCalendar, { isLoading: isDisconnecting }] = useDisconnectCalendarMutation();
  const [disconnectGmail, { isLoading: isDisconnectingGmail }] = useDisconnectGmailMutation();
  const [syncGmailN8n, { isLoading: isSyncingGmail }] = useSyncGmailN8nMutation();
  const [updateCalendarSettings, { isLoading: isSavingCalendar }] = useUpdateCalendarSettingsMutation();
  const { data: profilePicBlob } = useGetProfilePicQuery(undefined, { skip: !profile?.profile_pic_url });
  const [fetchProductDocFile] = useLazyGetProductDocFileQuery();

  const [fullName, setFullName] = useState("");
  const [profilePicFile, setProfilePicFile] = useState<File | null>(null);
  const [profilePicObjectUrl, setProfilePicObjectUrl] = useState<string>("");

  const [calendlySchedulingUrl, setCalendlySchedulingUrl] = useState("");
  const [defaultTimezone, setDefaultTimezone] = useState("UTC");
  const [defaultMeetingDuration, setDefaultMeetingDuration] = useState("30");

  const [calendarId, setCalendarId] = useState("primary");
  const [calendarTimezone, setCalendarTimezone] = useState("");
  const [calendarDuration, setCalendarDuration] = useState("30");

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  useEffect(() => {
    if (!profile) return;
    setFullName(profile.full_name ?? "");
  }, [profile]);

  useEffect(() => {
    if (!settings) return;
    setCalendlySchedulingUrl(settings.calendly_scheduling_url ?? "");
  }, [settings]);

  useEffect(() => {
    if (!outreachConfig) return;
    setDefaultTimezone(outreachConfig.default_timezone ?? "UTC");
    setDefaultMeetingDuration(String(outreachConfig.default_meeting_duration_minutes ?? 30));
  }, [outreachConfig]);

  useEffect(() => {
    if (!calendarStatus?.connected) return;
    setCalendarId(calendarStatus.calendar_id ?? "primary");
    setCalendarTimezone(calendarStatus.timezone ?? "");
    setCalendarDuration(String(calendarStatus.meeting_duration_minutes ?? 30));
  }, [calendarStatus]);

  useEffect(() => {
    const calendar = searchParams.get("calendar");
    if (calendar === "connected") {
      toast({ title: "Google Calendar connected", description: "You can now book meetings from inbox replies." });
    } else if (calendar === "error") {
      toast({
        title: "Google Calendar connection failed",
        description: "Try again or check OAuth redirect URI in Google Cloud Console.",
        variant: "destructive",
      });
    }

    const gmail = searchParams.get("gmail");
    if (gmail === "connected") {
      toast({
        title: "Gmail connected",
        description: gmailStatus?.n8n_synced
          ? "Inbound reply workflow is active in n8n."
          : "Gmail connected. Sync n8n if the workflow did not provision automatically.",
      });
    } else if (gmail === "error") {
      toast({
        title: "Gmail connection failed",
        description: "Try again or check OAuth redirect URI in Google Cloud Console.",
        variant: "destructive",
      });
    }
  }, [searchParams, gmailStatus?.n8n_synced]);

  const docs: ProductDoc[] = docsData?.items ?? [];

  useEffect(() => {
    if (!profilePicBlob) return;
    const url = URL.createObjectURL(profilePicBlob);
    setProfilePicObjectUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [profilePicBlob]);

  const viewProductDoc = async (docId: number) => {
    try {
      const blob = await fetchProductDocFile(docId).unwrap();
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 10_000);
    } catch {
      toast({ title: "Failed to load document", description: "Try again.", variant: "destructive" });
    }
  };

  const handleSaveProfile = async () => {
    const form = new FormData();
    form.append("full_name", fullName);
    if (profilePicFile) form.append("profile_pic", profilePicFile);
    try {
      await updateProfile(form).unwrap();
      toast({ title: "Profile updated", description: "Your profile changes were saved." });
      setProfilePicFile(null);
    } catch (err) {
      toast({
        title: "Profile update failed",
        description: "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSaveSettings = async () => {
    try {
      await updateSettings({ calendly_scheduling_url: calendlySchedulingUrl }).unwrap();
      const duration = parseInt(defaultMeetingDuration, 10);
      await updateOutreachConfig({
        default_timezone: defaultTimezone.trim() || "UTC",
        default_meeting_duration_minutes: Number.isFinite(duration) ? duration : 30,
      }).unwrap();
      toast({ title: "Settings updated", description: "Your config changes were saved." });
    } catch (err) {
      toast({
        title: "Settings update failed",
        description: "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleConnectGmail = async () => {
    try {
      const payload = await fetchGmailAuthUrl().unwrap();
      sessionStorage.setItem(GOOGLE_GMAIL_OAUTH_STATE_KEY, payload.state);
      window.location.href = payload.url;
    } catch {
      toast({
        title: "Could not start Gmail sign-in",
        description: "OAuth app credentials may be missing on the server.",
        variant: "destructive",
      });
    }
  };

  const handleDisconnectGmail = async () => {
    try {
      await disconnectGmail().unwrap();
      toast({ title: "Gmail disconnected", description: "n8n workflow and credential were removed." });
    } catch {
      toast({ title: "Gmail disconnect failed", variant: "destructive" });
    }
  };

  const handleSyncGmailN8n = async () => {
    try {
      const result = await syncGmailN8n().unwrap();
      if (result.n8n_synced) {
        toast({ title: "n8n synced", description: "Gmail credential and inbound workflow are ready." });
      } else {
        toast({
          title: "n8n sync incomplete",
          description: result.n8n_sync_error || "Check N8N_API_KEY on the server.",
          variant: "destructive",
        });
      }
    } catch {
      toast({ title: "n8n sync failed", variant: "destructive" });
    }
  };

  const handleConnectCalendar = async () => {
    try {
      const payload = await fetchCalendarAuthUrl().unwrap();
      sessionStorage.setItem(GOOGLE_CALENDAR_OAUTH_STATE_KEY, payload.state);
      window.location.href = payload.url;
    } catch {
      toast({
        title: "Could not start Google sign-in",
        description: "OAuth app credentials may be missing on the server.",
        variant: "destructive",
      });
    }
  };

  const handleDisconnectCalendar = async () => {
    try {
      await disconnectCalendar().unwrap();
      toast({ title: "Google Calendar disconnected" });
    } catch {
      toast({ title: "Disconnect failed", variant: "destructive" });
    }
  };

  const handleSaveCalendarSettings = async () => {
    const duration = parseInt(calendarDuration, 10);
    try {
      await updateCalendarSettings({
        calendar_id: calendarId.trim() || "primary",
        timezone: calendarTimezone.trim(),
        meeting_duration_minutes: Number.isFinite(duration) ? duration : 30,
      }).unwrap();
      toast({ title: "Calendar settings saved" });
    } catch {
      toast({ title: "Calendar settings update failed", variant: "destructive" });
    }
  };

  const handleUploadProducts = async () => {
    if (!selectedFiles.length) {
      toast({ title: "No files selected", description: "Choose one or more files first.", variant: "destructive" });
      return;
    }

    const form = new FormData();
    for (const f of selectedFiles) form.append("files", f);

    try {
      await uploadProductDocs(form).unwrap();
      toast({ title: "Docs uploaded", description: "Ingestion is triggered automatically." });
      setSelectedFiles([]);
    } catch (err) {
      toast({
        title: "Upload failed",
        description: "Please try again.",
        variant: "destructive",
      });
    }
  };

  const isLoading = profileLoading || settingsLoading || configLoading || calendarLoading || gmailLoading || docsLoading;
  if (isLoading) {
    return (
      <ScrollArea className="flex-1">
        <div className="p-8 max-w-5xl mx-auto space-y-6">
          <Skeleton className="h-10 w-64" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-3">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
            <div className="space-y-3">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
            <div className="space-y-3">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          </div>
        </div>
      </ScrollArea>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div className="p-8 bg-background">
        <div className="max-w-5xl mx-auto flex flex-col gap-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="text-slate-100 text-4xl font-black leading-tight tracking-tight">Settings</h1>
              <p className="text-slate-500 text-lg mt-2">Manage your profile, config, and product documentation.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1">
              <CardHeader>
                <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
                  <span className="material-symbols-outlined text-sm">person</span>
                  <span>Profile</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 overflow-hidden flex items-center justify-center">
                    {profilePicObjectUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={profilePicObjectUrl} alt="Profile" className="w-full h-full object-cover" />
                    ) : (
                      <span className="text-primary font-bold">U</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="text-slate-100 font-bold">{profile?.full_name || "User"}</div>
                    <div className="text-primary text-xs truncate">{profile?.email || ""}</div>
                  </div>
                </div>

                <div>
                  <Label htmlFor="fullName">Full name</Label>
                  <Input id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </div>

                <div>
                  <Label htmlFor="profilePic">Profile picture</Label>
                  <Input
                    id="profilePic"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setProfilePicFile(e.target.files?.[0] ?? null)}
                  />
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleSaveProfile} disabled={isSavingProfile}>
                    {isSavingProfile ? "Saving…" : "Save Profile"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
                  <span className="material-symbols-outlined text-sm">tune</span>
                  <span>Configs</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="calendlySchedulingUrl">Calendly scheduling URL</Label>
                  <Input
                    id="calendlySchedulingUrl"
                    type="url"
                    value={calendlySchedulingUrl}
                    onChange={(e) => setCalendlySchedulingUrl(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="defaultTimezone">Default timezone (global)</Label>
                    <Input
                      id="defaultTimezone"
                      value={defaultTimezone}
                      onChange={(e) => setDefaultTimezone(e.target.value)}
                      placeholder="UTC"
                    />
                  </div>
                  <div>
                    <Label htmlFor="defaultMeetingDuration">Default meeting length (minutes)</Label>
                    <Input
                      id="defaultMeetingDuration"
                      type="number"
                      min={15}
                      max={180}
                      value={defaultMeetingDuration}
                      onChange={(e) => setDefaultMeetingDuration(e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleSaveSettings} disabled={isSavingSettings || isSavingOutreachConfig}>
                    {isSavingSettings || isSavingOutreachConfig ? "Saving…" : "Save Configs"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
                <span className="material-symbols-outlined text-sm">mail</span>
                <span>Gmail (n8n inbound)</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {!gmailStatus?.oauth_app_configured ? (
                <p className="text-slate-500 text-sm">
                  Server OAuth is not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in
                  server/.env.
                </p>
              ) : !gmailStatus?.n8n_configured ? (
                <p className="text-slate-500 text-sm">
                  n8n API is not configured. Create an API key in n8n (Settings → API) and set N8N_API_KEY in
                  server/.env, then restart outreach.
                </p>
              ) : gmailStatus?.connected ? (
                <>
                  <div className="text-slate-300 text-sm">
                    Connected as <span className="text-slate-100 font-medium">{gmailStatus.google_email}</span>
                  </div>
                  <div className="text-slate-500 text-sm space-y-1">
                    <div>
                      n8n:{" "}
                      {gmailStatus.n8n_synced ? (
                        <span className="text-primary">workflow active</span>
                      ) : gmailStatus.n8n_configured ? (
                        <span className="text-amber-400">connected but not synced</span>
                      ) : (
                        <span className="text-amber-400">API key not configured</span>
                      )}
                    </div>
                    {gmailStatus.n8n_sync_error ? (
                      <div className="text-red-400 text-xs">{gmailStatus.n8n_sync_error}</div>
                    ) : null}
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    <Button variant="ghost" onClick={handleDisconnectGmail} disabled={isDisconnectingGmail}>
                      {isDisconnectingGmail ? "Disconnecting…" : "Disconnect"}
                    </Button>
                    {gmailStatus.n8n_configured && !gmailStatus.n8n_synced ? (
                      <Button onClick={handleSyncGmailN8n} disabled={isSyncingGmail}>
                        {isSyncingGmail ? "Syncing…" : "Sync to n8n"}
                      </Button>
                    ) : null}
                  </div>
                </>
              ) : (
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <p className="text-slate-500 text-sm">
                    Connect Gmail to poll unread replies via n8n and auto-draft responses. Each user gets their own n8n
                    workflow.
                  </p>
                  <Button onClick={handleConnectGmail} disabled={!gmailStatus?.n8n_configured}>
                    Connect Gmail
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
                <span className="material-symbols-outlined text-sm">event</span>
                <span>Google Calendar</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {!calendarStatus?.oauth_app_configured ? (
                <p className="text-slate-500 text-sm">
                  Server OAuth is not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in
                  server/.env.
                </p>
              ) : calendarStatus?.connected ? (
                <>
                  <div className="text-slate-300 text-sm">
                    Connected as <span className="text-slate-100 font-medium">{calendarStatus.google_email}</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="calendarId">Calendar ID</Label>
                      <Input
                        id="calendarId"
                        value={calendarId}
                        onChange={(e) => setCalendarId(e.target.value)}
                        placeholder="primary"
                      />
                    </div>
                    <div>
                      <Label htmlFor="calendarTimezone">Timezone (override)</Label>
                      <Input
                        id="calendarTimezone"
                        value={calendarTimezone}
                        onChange={(e) => setCalendarTimezone(e.target.value)}
                        placeholder={defaultTimezone || "UTC"}
                      />
                    </div>
                    <div>
                      <Label htmlFor="calendarDuration">Meeting length (minutes)</Label>
                      <Input
                        id="calendarDuration"
                        type="number"
                        min={15}
                        max={180}
                        value={calendarDuration}
                        onChange={(e) => setCalendarDuration(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    <Button variant="ghost" onClick={handleDisconnectCalendar} disabled={isDisconnecting}>
                      {isDisconnecting ? "Disconnecting…" : "Disconnect"}
                    </Button>
                    <Button onClick={handleSaveCalendarSettings} disabled={isSavingCalendar}>
                      {isSavingCalendar ? "Saving…" : "Save Calendar Settings"}
                    </Button>
                  </div>
                </>
              ) : (
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <p className="text-slate-500 text-sm">
                    Connect your Google account to let the scheduling agent create calendar events when leads confirm a
                    time.
                  </p>
                  <Button onClick={handleConnectCalendar}>Connect Google Calendar</Button>
                </div>
              )}
            </CardContent>
          </Card>

          <PersonaManager />

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
                <span className="material-symbols-outlined text-sm">description</span>
                <span>Products</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                <div>
                  <Label htmlFor="productDocsUpload">Upload product docs</Label>
                  <Input
                    id="productDocsUpload"
                    type="file"
                    multiple
                    accept=".md,.txt,text/plain,text/markdown"
                    onChange={(e) => setSelectedFiles(Array.from(e.target.files ?? []))}
                  />
                </div>
                <div className="flex justify-end">
                  <Button onClick={handleUploadProducts} disabled={isUploadingDocs}>
                    {isUploadingDocs ? "Uploading…" : "Upload & Ingest"}
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                <div className="text-sm font-bold text-slate-300">Uploaded files</div>
                {docs.length === 0 ? (
                  <div className="text-slate-500">No product docs uploaded yet.</div>
                ) : (
                  <div className="divide-y divide-primary/10">
                    {docs.map((doc) => (
                      <div key={doc.id} className="py-3 flex items-center justify-between gap-3">
                        <div className="min-w-0">
                          <div className="text-slate-100 font-medium truncate">{doc.filename}</div>
                          <div className="text-slate-500 text-xs">{new Date(doc.uploaded_at).toLocaleString()}</div>
                        </div>
                        <Button variant="ghost" onClick={() => viewProductDoc(doc.id)} className="text-primary font-bold whitespace-nowrap">
                          View
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ScrollArea>
  );
}

