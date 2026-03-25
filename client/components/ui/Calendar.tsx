"use client";

import * as React from "react";
import { DayPicker, type DateRange, type Matcher } from "react-day-picker";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";

type CalendarProps = React.ComponentProps<typeof DayPicker> & {
  disabled?: Matcher | Matcher[];
};

/**
 * shadcn/ui-style Calendar wrapper.
 *
 * Note: shadcn/ui's Calendar is a styled wrapper around `react-day-picker`.
 * This component is the single place in the app that touches `react-day-picker`
 * directly; other UI should import this Calendar instead.
 */
export function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-1", className)}
      classNames={{
        months: "flex flex-col sm:flex-row gap-4",
        month: "space-y-2",
        month_caption: "relative flex items-center justify-center px-0",
        caption_label: "text-sm font-semibold text-slate-100",
        nav: "absolute inset-x-0 flex items-center justify-between",
        button_previous: cn(
          "h-8 w-8 inline-flex items-center justify-center rounded-md",
          "border border-primary/20 bg-primary/5 text-slate-200 hover:bg-primary/10"
        ),
        button_next: cn(
          "h-8 w-8 inline-flex items-center justify-center rounded-md",
          "border border-primary/20 bg-primary/5 text-slate-200 hover:bg-primary/10"
        ),
        chevron: "h-4 w-4",

        month_grid: "w-full border-collapse space-y-1",
        weekdays: "flex",
        weekday: "w-9 text-[10px] font-semibold text-slate-400",
        weeks: "flex flex-col",
        week: "flex w-full mt-1",

        day: "h-9 w-9 p-0 text-center text-sm relative",
        day_button: cn(
          "h-9 w-9 rounded-md transition-colors",
          "text-slate-100 hover:bg-primary/10",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
        ),

        selected: "bg-primary text-primary-foreground rounded-md hover:bg-primary/90",
        range_start: "bg-primary text-primary-foreground rounded-md",
        range_end: "bg-primary text-primary-foreground rounded-md",
        range_middle: "bg-primary/20 text-slate-100 rounded-md",
        today: "border border-primary/40",
        outside: "text-slate-600 opacity-50",
        disabled: "text-slate-600 opacity-40 hover:bg-transparent",
        ...classNames,
      }}
      components={{
        Chevron: ({ orientation, className: c, ...p }) =>
          orientation === "left" ? (
            <ChevronLeft className={cn("h-4 w-4", c)} {...p} />
          ) : (
            <ChevronRight className={cn("h-4 w-4", c)} {...p} />
          ),
      }}
      {...props}
    />
  );
}

export type { DateRange };

