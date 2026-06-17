"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  useDisconnectGoogleMutation,
  useGetGoogleStatusQuery,
  useLazyGetGoogleAuthUrlQuery,
  useSyncGoogleN8nMutation,
  useUpdateGoogleSettingsMutation,
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
import { Pagination } from "@/components/ui/Pagination";
import { DEFAULT_PAGE_SIZE, paginate } from "@/lib/pagination";
import { GOOGLE_OAUTH_STATE_KEY, GOOGLE_OAUTH_TOAST_KEY } from "@/lib/googleOAuth";

export default function SettingsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const { data: settings, isLoading: settingsLoading } = useGetSettingsQuery();
  const { data: outreachConfig, isLoading: configLoading } = useGetConfigQuery();
  const { data: googleStatus, isLoading: googleLoading } = useGetGoogleStatusQuery();
  const { data: docsData, isLoading: docsLoading } = useGetProductDocsQuery();

  const [updateProfile, { isLoading: isSavingProfile }] = useUpdateProfileMutation();
  const [updateSettings, { isLoading: isSavingSettings }] = useUpdateSettingsMutation();
  const [updateOutreachConfig, { isLoading: isSavingOutreachConfig }] = useUpdateConfigMutation();
  const [uploadProductDocs, { isLoading: isUploadingDocs }] = useUploadProductDocsMutation();
  const [fetchGoogleAuthUrl] = useLazyGetGoogleAuthUrlQuery();
  const [disconnectGoogle, { isLoading: isDisconnecting }] = useDisconnectGoogleMutation();
  const [syncGoogleN8n, { isLoading: isSyncingN8n }] = useSyncGoogleN8nMutation();
  const [updateGoogleSettings, { isLoading: isSavingGoogleSettings }] = useUpdateGoogleSettingsMutation();
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
  const [docsPage, setDocsPage] = useState(1);

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
    if (!googleStatus?.connected) return;
    setCalendarId(googleStatus.calendar_id ?? "primary");
    setCalendarTimezone(googleStatus.timezone ?? "");
    setCalendarDuration(String(googleStatus.meeting_duration_minutes ?? 30));
  }, [googleStatus]);

  useEffect(() => {
    const google = searchParams.get("google");
    if (!google) return;

    const toastKey = `${GOOGLE_OAUTH_TOAST_KEY}:${google}`;
    if (!sessionStorage.getItem(toastKey)) {
      sessionStorage.setItem(toastKey, "1");
      if (google === "connected") {
        toast({
          id: "google-oauth",
          title: "Google connected",
          description: "Gmail, Calendar, and inbound reply workflow are ready.",
        });
      } else if (google === "error") {
        toast({
          id: "google-oauth",
          title: "Google connection failed",
          description: "Try again or check OAuth redirect URI in Google Cloud Console.",
          variant: "destructive",
        });
      }
    }

    router.replace("/settings", { scroll: false });
  }, [searchParams, router]);

  const docs: ProductDoc[] = docsData?.items ?? [];
  const pagedDocs = useMemo(() => paginate(docs, docsPage, DEFAULT_PAGE_SIZE), [docs, docsPage]);

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

  const handleConnectGoogle = async () => {
    try {
      sessionStorage.removeItem(`${GOOGLE_OAUTH_TOAST_KEY}:connected`);
      sessionStorage.removeItem(`${GOOGLE_OAUTH_TOAST_KEY}:error`);
      const payload = await fetchGoogleAuthUrl().unwrap();
      sessionStorage.setItem(GOOGLE_OAUTH_STATE_KEY, payload.state);
      window.location.href = payload.url;
    } catch {
      toast({
        title: "Could not start Google sign-in",
        description: "OAuth app credentials or n8n API key may be missing on the server.",
        variant: "destructive",
      });
    }
  };

  const handleDisconnectGoogle = async () => {
    try {
      await disconnectGoogle().unwrap();
      toast({ title: "Google disconnected", description: "n8n workflow and credential were removed." });
    } catch {
      toast({ title: "Google disconnect failed", variant: "destructive" });
    }
  };

  const handleSyncGoogleN8n = async () => {
    try {
      const result = await syncGoogleN8n().unwrap();
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

  const handleSaveGoogleSettings = async () => {
    const duration = parseInt(calendarDuration, 10);
    try {
      await updateGoogleSettings({
        calendar_id: calendarId.trim() || "primary",
        timezone: calendarTimezone.trim(),
        meeting_duration_minutes: Number.isFinite(duration) ? duration : 30,
      }).unwrap();
      toast({ title: "Google settings saved" });
    } catch {
      toast({ title: "Google settings update failed", variant: "destructive" });
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

  const isLoading = profileLoading || settingsLoading || configLoading || googleLoading || docsLoading;
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
      <div className="p-4 sm:p-6 lg:p-8 bg-background">
        <div className="max-w-5xl mx-auto flex flex-col gap-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="text-slate-100 text-2xl sm:text-4xl font-black leading-tight tracking-tight">Settings</h1>
              <p className="text-slate-500 text-base sm:text-lg mt-2">Manage your profile, config, and product documentation.</p>
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
                <span className="material-symbols-outlined text-sm">account_circle</span>
                <span>Google</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {!googleStatus?.oauth_app_configured ? (
                <p className="text-slate-500 text-sm">
                  Server OAuth is not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in
                  server/.env.
                </p>
              ) : !googleStatus?.n8n_configured ? (
                <p className="text-slate-500 text-sm">
                  n8n API is not configured. Create an API key in n8n (Settings → API) and set N8N_API_KEY in
                  server/.env, then restart outreach.
                </p>
              ) : googleStatus?.connected ? (
                <>
                  <div className="text-slate-300 text-sm">
                    Connected as <span className="text-slate-100 font-medium">{googleStatus.google_email}</span>
                  </div>
                  <div className="text-slate-500 text-sm space-y-1">
                    <div>
                      Gmail send + Calendar: <span className="text-primary">active</span>
                    </div>
                    <div>
                      n8n inbound:{" "}
                      {googleStatus.n8n_synced ? (
                        <span className="text-primary">workflow active</span>
                      ) : (
                        <span className="text-amber-400">connected but not synced</span>
                      )}
                    </div>
                    {googleStatus.n8n_sync_error ? (
                      <div className="text-red-400 text-xs">{googleStatus.n8n_sync_error}</div>
                    ) : null}
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
                    <Button variant="ghost" onClick={handleDisconnectGoogle} disabled={isDisconnecting}>
                      {isDisconnecting ? "Disconnecting…" : "Disconnect"}
                    </Button>
                    {!googleStatus.n8n_synced ? (
                      <Button onClick={handleSyncGoogleN8n} disabled={isSyncingN8n}>
                        {isSyncingN8n ? "Syncing…" : "Sync to n8n"}
                      </Button>
                    ) : null}
                    <Button onClick={handleSaveGoogleSettings} disabled={isSavingGoogleSettings}>
                      {isSavingGoogleSettings ? "Saving…" : "Save Settings"}
                    </Button>
                  </div>
                </>
              ) : (
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <p className="text-slate-500 text-sm">
                    Connect Google once for Gmail send, inbound reply polling via n8n, and Calendar booking from inbox
                    replies.
                  </p>
                  <Button onClick={handleConnectGoogle} disabled={!googleStatus?.n8n_configured}>
                    Connect Google
                  </Button>
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
                  <>
                    <div className="divide-y divide-primary/10">
                      {pagedDocs.items.map((doc) => (
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
                    <Pagination
                      page={pagedDocs.currentPage}
                      totalPages={pagedDocs.totalPages}
                      total={pagedDocs.total}
                      from={pagedDocs.from}
                      to={pagedDocs.to}
                      onPageChange={setDocsPage}
                      label="files"
                    />
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ScrollArea>
  );
}

