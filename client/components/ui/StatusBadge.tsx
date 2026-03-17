import { cn } from "@/lib/utils";

const statusStyles: Record<string, string> = {
  new: "bg-blue-400/10 text-blue-400 border-blue-400/20",
  researched: "bg-orange-400/10 text-orange-400 border-orange-400/20",
  emailed: "bg-primary/10 text-primary border-primary/20",
  replied: "bg-red-400/10 text-red-400 border-red-400/20",
  meeting_booked: "bg-emerald-400/10 text-emerald-400 border-emerald-400/20",
};

const statusLabels: Record<string, string> = {
  new: "Cold",
  researched: "Warm",
  emailed: "Contacted",
  replied: "Hot",
  meeting_booked: "Meeting",
};

export function StatusBadge({
  status,
  className,
}: {
  status: string;
  className?: string;
}) {
  const style = statusStyles[status] ?? "bg-slate-400/10 text-slate-400 border-slate-400/20";
  const label = statusLabels[status] ?? status.replace(/_/g, " ");
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        style,
        className
      )}
    >
      {label}
    </span>
  );
}
