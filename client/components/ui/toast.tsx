"use client";

import * as React from "react";
import * as ToastPrimitives from "@radix-ui/react-toast";
import { cn } from "@/lib/utils";

export const ToastProvider = ToastPrimitives.Provider;
export const ToastViewport = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Viewport>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Viewport>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Viewport
    ref={ref}
    className={cn(
      "fixed top-0 z-50 flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]",
      className
    )}
    {...props}
  />
));
ToastViewport.displayName = ToastPrimitives.Viewport.displayName;

export function Toast({
  className,
  variant,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Root> & {
  variant?: "default" | "destructive";
}) {
  return (
    <ToastPrimitives.Root
      className={cn(
        "group pointer-events-auto relative flex w-full items-start justify-between gap-3 overflow-hidden rounded-lg border px-4 py-3 shadow-lg",
        "bg-slate-900/70 border-primary/20 text-slate-100 backdrop-blur",
        variant === "destructive" &&
          "bg-red-950/40 border-red-500/30 text-red-100",
        className
      )}
      {...props}
    />
  );
}

export const ToastTitle = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Title>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Title>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Title
    ref={ref}
    className={cn("text-sm font-semibold leading-none", className)}
    {...props}
  />
));
ToastTitle.displayName = ToastPrimitives.Title.displayName;

export const ToastDescription = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Description>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Description>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Description
    ref={ref}
    className={cn("text-sm leading-relaxed text-slate-300", className)}
    {...props}
  />
));
ToastDescription.displayName = ToastPrimitives.Description.displayName;

export const ToastClose = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Close>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Close>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Close
    ref={ref}
    className={cn(
      "absolute right-2 top-2 rounded-md p-1 opacity-70 transition-opacity",
      "group-hover:opacity-100 focus:outline-none focus:ring-1 focus:ring-primary",
      className
    )}
    {...props}
  >
    <span className="material-symbols-outlined text-lg">close</span>
  </ToastPrimitives.Close>
));
ToastClose.displayName = ToastPrimitives.Close.displayName;

