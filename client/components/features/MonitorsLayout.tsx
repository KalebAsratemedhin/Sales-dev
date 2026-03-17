"use client";

import { ScrollArea } from "@/components/ui/ScrollArea";

type StatCard = {
  label: string;
  value: string;
  sub: string;
  subColor?: "green" | "red" | "primary" | "muted";
  icon: string;
  borderLeft?: boolean;
};

type SequenceRow = {
  id: string;
  icon: string;
  iconColor?: "primary" | "red";
  name: string;
  sector: string;
  loadPct: number;
  loadColor?: "primary" | "red";
  velocity: string;
  stability: string;
  stabilityColor?: "green" | "primary" | "red";
};

const LOG_LINES = [
  { time: "14:22:01", level: "INFO", color: "text-green-500", msg: "Node cluster 4 initialization successful." },
  { time: "14:22:04", level: "SCAN", color: "text-primary", msg: "Searching domain: tech-innovators.io" },
  { time: "14:22:05", level: "SCAN", color: "text-primary", msg: "Identified 42 new targets in sector-7." },
  { time: "14:22:09", level: "WARN", color: "text-red-500", msg: "Rate limit approaching on LinkedIn API." },
  { time: "14:22:12", level: "SEND", color: "text-green-500", msg: "Sequence 'A1' delivered to user@domain.com" },
  { time: "14:22:15", level: "SCAN", color: "text-primary", msg: "Data normalization in progress..." },
  { time: "14:22:18", level: "DEBUG", color: "text-slate-400", msg: "Buffer flushed. 0ms latency." },
  { time: "14:22:20", level: "INFO", color: "text-green-500", msg: "Automatic backup completed." },
  { time: "14:22:22", level: "SYSTEM", color: "text-primary italic animate-pulse", msg: "Listening for incoming hooks..._" },
];

const DEFAULT_STATS: StatCard[] = [
  { label: "Active Scans", value: "1,284", sub: "+12.4% FROM PREVIOUS HOUR", subColor: "green", icon: "radar" },
  { label: "Reach Rate", value: "92.4%", sub: "OPTIMAL PERFORMANCE", subColor: "green", icon: "target" },
  { label: "Avg Latency", value: "142", sub: "+5% DEGRADATION DETECTED", subColor: "red", icon: "speed", borderLeft: true },
  { label: "Success Tokens", value: "8.2k", sub: "BURST MODE ACTIVE", subColor: "primary", icon: "token" },
];

const DEFAULT_SEQUENCES: SequenceRow[] = [
  { id: "OUT-7729-X", icon: "radar", name: "OUT-7729-X", sector: "Enterprise SaaS / US-EAST", loadPct: 75, velocity: "12.5 msg/s", stability: "NOMINAL", stabilityColor: "green" },
  { id: "SCAN-BK-04", icon: "satellite_alt", name: "SCAN-BK-04", sector: "FinTech / APAC-SOUTH", loadPct: 50, velocity: "4.2 msg/s", stability: "SCALING", stabilityColor: "primary" },
  { id: "CRIT-PATH-01", icon: "emergency_home", iconColor: "red", name: "CRIT-PATH-01", sector: "Healthcare / EU-WEST", loadPct: 92, loadColor: "red", velocity: "48.9 msg/s", stability: "THROTTLED", stabilityColor: "red" },
];

interface MonitorsLayoutProps {
  title: string;
  titleHighlight?: string;
  stats?: StatCard[];
  sequences?: SequenceRow[];
}

const subColorClasses = {
  green: "text-green-500",
  red: "text-red-500",
  primary: "text-primary",
  muted: "text-slate-500",
};

const stabilityColorClasses = {
  green: "text-green-500",
  primary: "text-primary",
  red: "text-red-500",
};

export function MonitorsLayout({
  title,
  titleHighlight = "Monitors",
  stats = DEFAULT_STATS,
  sequences = DEFAULT_SEQUENCES,
}: MonitorsLayoutProps) {
  return (
    <ScrollArea className="flex-1">
      <div className="p-8 space-y-8">
        {/* Stat cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((card) => (
            <div
              key={card.label}
              className={`bg-primary/5 border border-primary/20 p-6 rounded relative overflow-hidden group ${card.borderLeft ? "border-l-4 border-l-red-500" : ""}`}
            >
              <div className="absolute right-0 top-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                <span className="material-symbols-outlined text-6xl">{card.icon}</span>
              </div>
              <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-1">
                {card.label}
              </p>
              <h3 className="text-3xl font-bold text-slate-100">
                {card.value}
                {card.label === "Avg Latency" && (
                  <span className="text-sm font-normal text-slate-500 ml-1">ms</span>
                )}
              </h3>
              <div
                className={`mt-4 flex items-center gap-2 text-xs font-bold ${card.subColor ? subColorClasses[card.subColor] : "text-slate-500"}`}
              >
                <span className="material-symbols-outlined text-sm">trending_up</span>
                <span>{card.sub}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Topology + Logs */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-background/40 border border-primary/20 rounded p-6">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-sm font-bold uppercase tracking-widest text-primary flex items-center gap-2">
                <span className="material-symbols-outlined text-lg">monitoring</span>
                Outreach Network Topology
              </h3>
              <div className="flex gap-2">
                <span className="px-2 py-1 rounded bg-primary/10 border border-primary/30 text-[10px] text-primary font-bold">
                  LIVE
                </span>
                <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-[10px] text-slate-400 font-bold">
                  HD-SCAN
                </span>
              </div>
            </div>
            <div className="h-64 w-full bg-slate-900/50 rounded border border-primary/10 relative overflow-hidden flex items-center justify-center">
              <div
                className="absolute inset-0 opacity-20 pointer-events-none"
                style={{
                  backgroundImage: "radial-gradient(circle at 2px 2px, #f5a30a 1px, transparent 0)",
                  backgroundSize: "24px 24px",
                }}
              />
              <svg className="absolute inset-0 w-full h-full opacity-40" viewBox="0 0 800 300">
                <path d="M100,150 Q250,50 400,150 T700,150" fill="none" stroke="#f5a30a" strokeDasharray="4 4" strokeWidth="1" />
                <path d="M50,100 Q300,250 550,100 T750,200" fill="none" stroke="#f5a30a" strokeDasharray="2 6" strokeWidth="1" />
                <circle className="animate-pulse" cx="100" cy="150" fill="#f5a30a" r="4" />
                <circle cx="400" cy="150" fill="#f5a30a" r="6" />
                <circle cx="700" cy="150" fill="#f5a30a" r="4" />
              </svg>
              <div className="absolute bottom-4 left-4 text-[10px] text-primary/60 font-mono">
                COORD_X: 42.192
                <br />
                COORD_Y: -71.201
                <br />
                STATUS: ESTABLISHED
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] uppercase text-slate-400 font-bold">
                  <span>Payload Health</span>
                  <span className="text-primary">98%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[98%]" style={{ boxShadow: "0 0 8px #f5a30a" }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] uppercase text-slate-400 font-bold">
                  <span>Proxy Rotation</span>
                  <span className="text-primary">64%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[64%]" />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] uppercase text-slate-400 font-bold">
                  <span>Thread Load</span>
                  <span className="text-red-500">89%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[89%]" />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-background/60 border border-primary/20 rounded flex flex-col min-h-[350px]">
            <div className="p-4 border-b border-primary/20 bg-primary/5 shrink-0">
              <h3 className="text-sm font-bold uppercase tracking-widest text-primary flex items-center gap-2">
                <span className="material-symbols-outlined text-lg">terminal</span>
                Real-time Logs
              </h3>
            </div>
            <ScrollArea className="flex-1 min-h-0">
            <div className="p-4 font-mono text-[11px] space-y-2">
              {LOG_LINES.map((line, i) => (
                <div key={i} className="flex gap-2 flex-wrap">
                  <span className="text-slate-500">[{line.time}]</span>
                  <span className={line.color}>{line.level}:</span>
                  <span className="text-slate-300">{line.msg}</span>
                </div>
              ))}
            </div>
            </ScrollArea>
            <div className="p-4 border-t border-primary/10 shrink-0">
              <div className="relative">
                <span className="absolute left-2 top-1/2 -translate-y-1/2 text-primary text-xs font-bold">
                  &gt;
                </span>
                <input
                  type="text"
                  className="w-full bg-transparent border border-primary/20 rounded pl-6 pr-4 py-1.5 text-xs font-mono focus:ring-0 focus:border-primary text-primary placeholder:text-slate-500"
                  placeholder="Execute command..."
                  aria-label="Command"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Sequences table */}
        <div className="bg-background/40 border border-primary/20 rounded overflow-hidden">
          <div className="p-6 border-b border-primary/20 flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-widest text-primary">
              Priority Outreach Sequences
            </h3>
            <button type="button" className="text-xs text-primary font-bold hover:underline flex items-center gap-1">
              VIEW ALL SYSTEMS
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-primary/5 text-[10px] uppercase font-bold tracking-widest text-slate-400 border-b border-primary/10">
                <tr>
                  <th className="px-6 py-4">Monitor ID</th>
                  <th className="px-6 py-4">Target Sector</th>
                  <th className="px-6 py-4">Current Load</th>
                  <th className="px-6 py-4">Velocity</th>
                  <th className="px-6 py-4">Stability</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-primary/5">
                {sequences.map((row) => (
                  <tr key={row.id} className="hover:bg-primary/5 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span
                          className={`material-symbols-outlined text-lg ${row.iconColor === "red" ? "text-red-500" : "text-primary"}`}
                        >
                          {row.icon}
                        </span>
                        <span className="text-sm font-bold text-slate-200">{row.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">{row.sector}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${row.loadColor === "red" ? "bg-red-500" : "bg-primary"}`}
                            style={{ width: `${row.loadPct}%` }}
                          />
                        </div>
                        <span
                          className={`text-[10px] font-bold ${row.loadColor === "red" ? "text-red-500" : ""}`}
                        >
                          {row.loadPct}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-primary">{row.velocity}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`flex items-center gap-1 text-[10px] font-bold ${row.stabilityColor ? stabilityColorClasses[row.stabilityColor] : ""}`}
                      >
                        <span
                          className={`size-1.5 rounded-full ${
                            row.stabilityColor === "green"
                              ? "bg-green-500"
                              : row.stabilityColor === "red"
                                ? "bg-red-500"
                                : "bg-primary animate-pulse"
                          }`}
                        />
                        {row.stability}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button type="button" className="text-slate-400 hover:text-primary transition-colors">
                        <span className="material-symbols-outlined text-lg">more_vert</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </ScrollArea>
  );
}
