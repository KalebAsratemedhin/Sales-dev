"use client";

import type { ReactNode } from "react";
import { ScrollArea } from "@/components/ui/ScrollArea";

type StatCard = {
  label: string;
  value: string;
  sub: string;
  subColor?: "green" | "red" | "primary" | "muted";
  icon: string;
  borderLeft?: boolean;
};

interface MonitorsLayoutProps {
  title: string;
  titleHighlight?: string;
  stats?: StatCard[];
  isLoading?: boolean;
  children?: ReactNode;
}

const subColorClasses = {
  green: "text-green-500",
  red: "text-red-500",
  primary: "text-primary",
  muted: "text-slate-500",
};

export function MonitorsLayout({
  title,
  titleHighlight = "Monitors",
  stats = [],
  isLoading = false,
  children,
}: MonitorsLayoutProps) {
  return (
    <ScrollArea className="flex-1">
      <div className="p-4 sm:p-6 lg:p-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">
            {title}{" "}
            <span className="text-primary">{titleHighlight}</span>
          </h1>
        </div>

        {isLoading && <p className="text-slate-500 text-sm">Loading stats…</p>}

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
              <h3 className="text-3xl font-bold text-slate-100">{card.value}</h3>
              <div
                className={`mt-4 flex items-center gap-2 text-xs font-bold ${card.subColor ? subColorClasses[card.subColor] : "text-slate-500"}`}
              >
                <span>{card.sub}</span>
              </div>
            </div>
          ))}
        </div>

        {children}
      </div>
    </ScrollArea>
  );
}
