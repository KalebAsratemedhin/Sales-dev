import { cn } from "@/lib/utils";
import { Slot } from "@radix-ui/react-slot";
import * as React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", className, children, asChild = false, ...props },
  ref
) {
  const base =
    "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 disabled:pointer-events-none disabled:opacity-50";
  const variants = {
    primary:
      "bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20",
    secondary:
      "border border-primary/20 bg-primary/5 text-slate-300 hover:bg-primary/10",
    ghost: "text-slate-400 hover:bg-primary/10 hover:text-primary",
  };
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      ref={ref}
      className={cn(base, variants[variant], className)}
      {...props}
    >
      {children}
    </Comp>
  );
});
