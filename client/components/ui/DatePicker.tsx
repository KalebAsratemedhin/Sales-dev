"use client";

import * as React from "react";
import { format } from "date-fns";
import type { Matcher } from "react-day-picker";

import { Button } from "@/components/ui/Button";
import { Calendar } from "@/components/ui/Calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/Popover";
import { cn } from "@/lib/utils";

export function DatePicker({
  value,
  onChange,
  disabled,
  placeholder = "Pick a date",
  className,
}: {
  value: Date | undefined;
  onChange: (d: Date | undefined) => void;
  disabled?: Matcher | Matcher[];
  placeholder?: string;
  className?: string;
}) {
  const hasValue = Boolean(value);
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="secondary"
          className={cn(
            "w-full justify-start gap-2 px-3",
            hasValue && "border-primary/40 bg-primary/5 text-slate-100 hover:bg-primary/10",
            className
          )}
        >
          <span className={cn(!hasValue ? "text-slate-400" : "text-slate-100")}>
            {value ? format(value, "yyyy-MM-dd") : placeholder}
          </span>
          <span className="material-symbols-outlined ml-auto text-sm">calendar_month</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-2">
        <Calendar
          mode="single"
          selected={value}
          onSelect={onChange}
          disabled={disabled}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  );
}

