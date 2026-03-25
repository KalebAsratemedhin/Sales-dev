"use client";

import { useEffect, useMemo, useState } from "react";
import { useDispatch } from "react-redux";

import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { DatePicker } from "@/components/ui/DatePicker";
import { toast } from "@/components/ui/use-toast";
import { useGetSettingsQuery } from "@/store/authApi";
import { authApi } from "@/store/authApi";
import { leadsApi } from "@/store/leadsApi";
import { useStartProfileSyncJobMutation, useLazyGetSyncJobQuery } from "@/store/linkedinApi";

function parseIsoDate(s: string): Date | undefined {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec((s || "").trim());
  if (!m) return undefined;
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  if (Number.isNaN(d.getTime())) return undefined;
  return d;
}

function toIsoDate(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function startOfToday(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

export function LinkedInSyncRange() {
  const dispatch = useDispatch();
  const { data: settings, isLoading: loadingSettings } = useGetSettingsQuery();
  const [startJob, { isLoading: starting }] = useStartProfileSyncJobMutation();
  const [getJob] = useLazyGetSyncJobQuery();

  const today = useMemo(() => startOfToday(), []);
  const minDate = useMemo(() => {
    const raw = settings?.linkedin_last_sync;
    return raw ? parseIsoDate(raw) : undefined;
  }, [settings?.linkedin_last_sync]);

  const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (!settings) return;
    const from = minDate ?? today;
    setStartDate(from);
    setEndDate(today);
  }, [settings, minDate, today]);

  const disabledStart = useMemo(() => {
    return [
      { after: today },
    ];
  }, [today]);

  const disabledEnd = useMemo(() => {
    const minEnd = startDate;
    return [
      ...(minEnd ? [{ before: minEnd }] : []),
      { after: today },
    ];
  }, [startDate, today]);

  const pollUntilDone = async (jobId: number) => {
    if (polling) return;
    setPolling(true);
    try {
      for (let i = 0; i < 600; i += 1) {
        const job = await getJob(jobId, true).unwrap();
        if (job.status === "succeeded") return job;
        if (job.status === "failed") throw new Error(job.error || "Sync failed.");
        await new Promise((r) => setTimeout(r, 2000));
      }
      throw new Error("Timed out waiting for sync to finish.");
    } finally {
      setPolling(false);
    }
  };

  const onSync = async () => {
    if (!startDate || !endDate) {
      toast({ title: "Select start and end dates", variant: "destructive" });
      return;
    }
    if (endDate > today) {
      toast({ title: "End date cannot be in the future", variant: "destructive" });
      return;
    }
    if (startDate > endDate) {
      toast({ title: "Start date must be before end date", variant: "destructive" });
      return;
    }

    try {
      const { job_id } = await startJob({
        start_date: toIsoDate(startDate),
        end_date: toIsoDate(endDate),
      }).unwrap();

      toast({ title: "LinkedIn sync started", description: "We’ll notify you when it’s finished." });

      const result = await pollUntilDone(job_id);
      if (!result) return;

      dispatch(leadsApi.util.invalidateTags([{ type: "Leads", id: "LIST" }]));
      dispatch(authApi.util.invalidateTags(["Settings"]));

      toast({
        title: "LinkedIn sync complete",
        description: `Created ${result.created}, updated ${result.updated}.`,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Sync failed. Check logs.";
      toast({ title: "LinkedIn sync failed", description: msg, variant: "destructive" });
    }
  };

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-primary font-bold text-xs tracking-wider uppercase">
            <span className="material-symbols-outlined text-sm">sync</span>
            <span>Sync LinkedIn</span>
          </div>
          <div className="text-xs text-slate-400">
            Last sync:{" "}
            <span className="text-slate-200">{settings?.linkedin_last_sync || "Never"}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="flex flex-col gap-1">
            <div className="text-xs font-bold text-slate-400">From</div>
            <DatePicker
              value={startDate}
              onChange={(d) => {
                setStartDate(d);
                if (d && endDate && endDate < d) setEndDate(d);
              }}
              disabled={disabledStart}
              className="w-[180px]"
              placeholder="Start date"
            />
          </div>
          <div className="flex flex-col gap-1">
            <div className="text-xs font-bold text-slate-400">To</div>
            <DatePicker
              value={endDate}
              onChange={setEndDate}
              disabled={disabledEnd}
              className="w-[180px]"
              placeholder="End date"
            />
          </div>
          <div className="flex-1" />
          <Button onClick={onSync} disabled={loadingSettings || starting || polling}>
            {starting || polling ? "Syncing…" : "Start sync"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

