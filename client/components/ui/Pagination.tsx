"use client";

type PaginationProps = {
  page: number;
  totalPages: number;
  total: number;
  from: number;
  to: number;
  onPageChange: (page: number) => void;
  label?: string;
};

export function Pagination({
  page,
  totalPages,
  total,
  from,
  to,
  onPageChange,
  label = "items",
}: PaginationProps) {
  if (total === 0) return null;

  const pages = Array.from({ length: Math.min(3, totalPages) }, (_, i) => page - 1 + i).filter(
    (p) => p >= 1 && p <= totalPages
  );

  return (
    <div className="px-4 sm:px-6 py-4 border-t border-primary/10 bg-primary/5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs text-slate-500 font-medium">
      <p>
        Showing {from} to {to} of {total} {label}
      </p>
      {totalPages > 1 ? (
        <div className="flex gap-2 self-end sm:self-auto">
          <button
            type="button"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="size-8 flex items-center justify-center rounded border border-primary/20 bg-background hover:text-primary transition-colors disabled:opacity-50 disabled:pointer-events-none"
            aria-label="Previous page"
          >
            <span className="material-symbols-outlined text-sm">chevron_left</span>
          </button>
          {pages.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => onPageChange(p)}
              className={`size-8 flex items-center justify-center rounded font-bold transition-colors ${
                p === page
                  ? "bg-primary text-primary-foreground"
                  : "border border-primary/20 bg-background hover:text-primary"
              }`}
            >
              {p}
            </button>
          ))}
          <button
            type="button"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="size-8 flex items-center justify-center rounded border border-primary/20 bg-background hover:text-primary transition-colors disabled:opacity-50 disabled:pointer-events-none"
            aria-label="Next page"
          >
            <span className="material-symbols-outlined text-sm">chevron_right</span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
