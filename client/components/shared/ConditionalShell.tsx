"use client";

import { usePathname } from "next/navigation";
import { AppShell } from "./AppShell";

const PUBLIC_PATHS = ["/", "/sign-in", "/sign-up"];

export function ConditionalShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isPublic = PUBLIC_PATHS.includes(pathname);

  if (isPublic) return <>{children}</>;
  return <AppShell>{children}</AppShell>;
}
