"use client";

import { useEffect, useState } from "react";
import { useGetConfigQuery, useUpdateConfigMutation } from "@/store/outreachConfigApi";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { ScrollArea } from "@/components/ui/ScrollArea";
import { Skeleton } from "@/components/ui/Skeleton";

export default function ConfigPage() {
  const { data: config, isLoading, error } = useGetConfigQuery();
  const [updateConfig, { isLoading: isUpdating }] = useUpdateConfigMutation();

  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [calendlyUrl, setCalendlyUrl] = useState("");
  const [productDocsPath, setProductDocsPath] = useState("");
  const [chromaCollection, setChromaCollection] = useState("");

  useEffect(() => {
    if (!config) return;
    setLinkedinUrl(config.linkedin_url ?? "");
    setCalendlyUrl(config.calendly_scheduling_url ?? "");
    setProductDocsPath(config.product_docs_path ?? "");
    setChromaCollection(config.chroma_collection_name ?? "product_docs");
  }, [config]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateConfig({
      linkedin_url: linkedinUrl,
      calendly_scheduling_url: calendlyUrl,
      product_docs_path: productDocsPath,
      chroma_collection_name: chromaCollection || "product_docs",
    });
  };

  if (isLoading) {
    return (
      <ScrollArea className="flex-1">
        <div className="p-8 max-w-4xl mx-auto space-y-6">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-5 w-96" />
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </div>
        </div>
      </ScrollArea>
    );
  }

  if (error) {
    return (
      <div className="flex-1 overflow-y-auto p-8">
        <h1 className="text-2xl font-bold text-slate-100">System Configuration</h1>
        <p className="text-red-400 mt-2">
          Failed to load config. Check API base URL (NEXT_PUBLIC_API_BASE_URL).
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div className="p-8 bg-background">
      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
            <span className="material-symbols-outlined text-sm">tune</span>
            <span>Core Settings</span>
          </div>
          <div className="flex flex-wrap justify-between items-end gap-6">
            <div className="flex-1 min-w-[300px]">
              <h1 className="text-slate-100 text-4xl lg:text-5xl font-black leading-tight tracking-tight mb-3">
                System Configuration
              </h1>
              <p className="text-slate-500 text-lg leading-relaxed">
                Manage your core workspace settings, outreach URLs, and integration options
                from a single interface.
              </p>
            </div>
            <Button
              type="submit"
              form="config-form"
              disabled={isUpdating}
              className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded font-bold shadow-lg shadow-primary/30 hover:brightness-110 transition-all"
            >
              <span className="material-symbols-outlined text-[20px]">save</span>
              {isUpdating ? "Saving…" : "Save All Changes"}
            </Button>
          </div>
        </div>

        <form id="config-form" onSubmit={handleSubmit} className="grid grid-cols-1 gap-6 mt-4">
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 lg:p-8">
            <h3 className="text-slate-100 text-xl font-bold mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">link</span>
              Outreach &amp; Integrations
            </h3>
            <div className="flex flex-col gap-6">
              <div>
                <Label
                  htmlFor="linkedin"
                  className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 block"
                >
                  LinkedIn URL
                </Label>
                <Input
                  id="linkedin"
                  type="url"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  className="w-full bg-background border border-primary/20 rounded px-4 py-2.5 text-slate-100 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <Label
                  htmlFor="calendly"
                  className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 block"
                >
                  Calendly scheduling URL
                </Label>
                <Input
                  id="calendly"
                  type="url"
                  value={calendlyUrl}
                  onChange={(e) => setCalendlyUrl(e.target.value)}
                  className="w-full bg-background border border-primary/20 rounded px-4 py-2.5 text-slate-100 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <Label
                  htmlFor="docs"
                  className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 block"
                >
                  Product docs path
                </Label>
                <Input
                  id="docs"
                  type="text"
                  value={productDocsPath}
                  onChange={(e) => setProductDocsPath(e.target.value)}
                  className="w-full bg-background border border-primary/20 rounded px-4 py-2.5 text-slate-100 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <Label
                  htmlFor="chroma"
                  className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 block"
                >
                  Chroma collection name
                </Label>
                <Input
                  id="chroma"
                  type="text"
                  value={chromaCollection}
                  onChange={(e) => setChromaCollection(e.target.value)}
                  className="w-full bg-background border border-primary/20 rounded px-4 py-2.5 text-slate-100 focus:ring-primary focus:border-primary"
                />
              </div>
            </div>
          </div>
        </form>
      </div>
      </div>
    </ScrollArea>
  );
}
