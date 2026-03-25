"use client";

import { useEffect, useState } from "react";
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
import type { ProductDoc } from "@/types";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { Skeleton } from "@/components/ui/Skeleton";
import { toast } from "@/components/ui/use-toast";

export default function SettingsPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const { data: settings, isLoading: settingsLoading } = useGetSettingsQuery();
  const { data: docsData, isLoading: docsLoading } = useGetProductDocsQuery();

  const [updateProfile, { isLoading: isSavingProfile }] = useUpdateProfileMutation();
  const [updateSettings, { isLoading: isSavingSettings }] = useUpdateSettingsMutation();
  const [uploadProductDocs, { isLoading: isUploadingDocs }] = useUploadProductDocsMutation();
  const { data: profilePicBlob } = useGetProfilePicQuery(undefined, { skip: !profile?.profile_pic_url });
  const [fetchProductDocFile] = useLazyGetProductDocFileQuery();

  const [fullName, setFullName] = useState("");
  const [profilePicFile, setProfilePicFile] = useState<File | null>(null);
  const [profilePicObjectUrl, setProfilePicObjectUrl] = useState<string>("");

  const [linkedinProfileUrl, setLinkedinProfileUrl] = useState("");
  const [calendlySchedulingUrl, setCalendlySchedulingUrl] = useState("");

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  useEffect(() => {
    if (!profile) return;
    setFullName(profile.full_name ?? "");
  }, [profile]);

  useEffect(() => {
    if (!settings) return;
    setLinkedinProfileUrl(settings.linkedin_profile_url ?? "");
    setCalendlySchedulingUrl(settings.calendly_scheduling_url ?? "");
  }, [settings]);

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
      await updateSettings({ linkedin_profile_url: linkedinProfileUrl, calendly_scheduling_url: calendlySchedulingUrl }).unwrap();
      toast({ title: "Settings updated", description: "Your config changes were saved." });
    } catch (err) {
      toast({
        title: "Settings update failed",
        description: "Please try again.",
        variant: "destructive",
      });
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

  const isLoading = profileLoading || settingsLoading || docsLoading;
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
                  <Label htmlFor="linkedinProfileUrl">LinkedIn profile URL</Label>
                  <Input
                    id="linkedinProfileUrl"
                    type="url"
                    value={linkedinProfileUrl}
                    onChange={(e) => setLinkedinProfileUrl(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="linkedinLastSync">LinkedIn last sync</Label>
                  <Input
                    id="linkedinLastSync"
                    value={settings?.linkedin_last_sync ? settings.linkedin_last_sync : "Never"}
                    disabled
                    className="cursor-not-allowed opacity-80"
                  />
                </div>
                <div>
                  <Label htmlFor="calendlySchedulingUrl">Calendly scheduling URL</Label>
                  <Input
                    id="calendlySchedulingUrl"
                    type="url"
                    value={calendlySchedulingUrl}
                    onChange={(e) => setCalendlySchedulingUrl(e.target.value)}
                  />
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleSaveSettings} disabled={isSavingSettings}>
                    {isSavingSettings ? "Saving…" : "Save Configs"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

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

