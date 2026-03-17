"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-1 items-center justify-center p-8">
      <div className="max-w-md text-center space-y-6">
        <span
          className="material-symbols-outlined text-5xl text-red-400"
          aria-hidden
        >
          error
        </span>
        <h2 className="text-xl font-bold text-slate-100">Something went wrong</h2>
        <p className="text-sm text-slate-500">
          An unexpected error occurred. You can try again or return to the dashboard.
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <Button onClick={reset}>Try again</Button>
          <a
            href="/"
            className="inline-flex items-center justify-center rounded border border-primary/20 bg-primary/5 px-4 py-2 text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
          >
            Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
