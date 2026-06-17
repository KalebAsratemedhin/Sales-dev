"use client";

type BarChartItem = {
  label: string;
  value: number;
  colorClass: string;
};

export function HorizontalBarChart({
  items,
  emptyLabel = "No data yet",
}: {
  items: BarChartItem[];
  emptyLabel?: string;
}) {
  const max = Math.max(1, ...items.map((item) => item.value));
  const total = items.reduce((sum, item) => sum + item.value, 0);

  if (total === 0) {
    return <p className="text-slate-500 text-sm py-8 text-center">{emptyLabel}</p>;
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.label}>
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-300 font-medium">{item.label}</span>
            <span className="text-slate-500 font-bold">{item.value}</span>
          </div>
          <div className="h-2.5 bg-primary/10 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${item.colorClass}`}
              style={{ width: `${(item.value / max) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function GroupedActivityChart({
  data,
  emptyLabel = "No email activity in the last 7 days",
}: {
  data: { label: string; sent: number; received: number }[];
  emptyLabel?: string;
}) {
  const max = Math.max(1, ...data.flatMap((day) => [day.sent, day.received]));
  const hasActivity = data.some((day) => day.sent > 0 || day.received > 0);

  if (!hasActivity) {
    return <p className="text-slate-500 text-sm py-8 text-center">{emptyLabel}</p>;
  }

  return (
    <div>
      <div className="flex items-end gap-3 h-44 px-1">
        {data.map((day) => (
          <div key={day.label} className="flex-1 flex flex-col items-center gap-2 min-w-0">
            <div className="flex items-end justify-center gap-1 h-36 w-full">
              <div
                className="w-3 sm:w-4 bg-green-500/80 rounded-t transition-all"
                style={{ height: `${(day.sent / max) * 100}%`, minHeight: day.sent > 0 ? "4px" : 0 }}
                title={`${day.sent} sent`}
              />
              <div
                className="w-3 sm:w-4 bg-primary/80 rounded-t transition-all"
                style={{ height: `${(day.received / max) * 100}%`, minHeight: day.received > 0 ? "4px" : 0 }}
                title={`${day.received} received`}
              />
            </div>
            <span className="text-[10px] text-slate-500 font-medium truncate w-full text-center">
              {day.label}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-center gap-6 mt-4 text-xs">
        <div className="flex items-center gap-2">
          <span className="size-2.5 rounded-sm bg-green-500/80" />
          <span className="text-slate-400">Sent</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="size-2.5 rounded-sm bg-primary/80" />
          <span className="text-slate-400">Received</span>
        </div>
      </div>
    </div>
  );
}
