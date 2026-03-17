import { cn } from "@/lib/utils";

export function Label({
  htmlFor,
  className,
  children,
}: {
  htmlFor?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <label
      htmlFor={htmlFor}
      className={cn(
        "mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300",
        className
      )}
    >
      {children}
    </label>
  );
}
