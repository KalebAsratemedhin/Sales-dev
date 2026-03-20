"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { clearTokens, getAccessToken, getRefreshToken } from "@/lib/authStorage";
import { useMeQuery } from "@/store/authApi";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "dashboard" },
  { href: "/leads", label: "Leads", icon: "group" },
  { href: "/research", label: "Research", icon: "track_changes" },
  { href: "/outreach", label: "Outreach", icon: "send" },
  { href: "/inbox", label: "Inbox", icon: "inbox" },
  { href: "/settings", label: "Settings", icon: "settings" },
];

function getHeaderFromPath(pathname: string): { title: string; breadcrumb?: { href: string; label: string } } {
  if (pathname === "/dashboard") return { title: "Dashboard" };
  if (pathname === "/leads") return { title: "Leads" };
  if (pathname.startsWith("/leads/") && pathname !== "/leads") {
    return { title: "Lead Details", breadcrumb: { href: "/leads", label: "Leads" } };
  }
  if (pathname === "/research") return { title: "Research" };
  if (pathname === "/outreach") return { title: "Outreach" };
  if (pathname === "/inbox") return { title: "Inbox & Replies" };
  if (pathname === "/settings") return { title: "Settings" };
  return { title: "SalesMind" };
}

function NavIcon({ name }: { name: string }) {
  return (
    <span className="material-symbols-outlined text-[20px]" aria-hidden>
      {name}
    </span>
  );
}

function initials(fullName: string, email: string): string {
  const name = fullName?.trim() ?? "";
  if (name) {
    const parts = name.split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    if (parts[0].length >= 2) return parts[0].slice(0, 2).toUpperCase();
    return parts[0][0].toUpperCase();
  }
  if (email?.length >= 2) return email.slice(0, 2).toUpperCase();
  return "—";
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { title, breadcrumb } = getHeaderFromPath(pathname);

  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();

  const shouldSkipAuthFetch = !accessToken && !refreshToken;
  const { data: me, error: meError, isLoading: meLoading } = useMeQuery(undefined, {
    skip: shouldSkipAuthFetch,
  });

  const meStatus = (meError as any)?.status as number | undefined;

  useEffect(() => {
    if (shouldSkipAuthFetch) {
      router.replace("/");
      return;
    }
    if (meStatus === 401) {
      clearTokens();
      router.replace("/");
    }
  }, [meStatus, router, shouldSkipAuthFetch]);

  const displayName = me?.full_name || me?.email || "User";
  const avatarInitials = me ? initials(me.full_name ?? "", me.email ?? "") : "U";

  const [avatarMenuOpen, setAvatarMenuOpen] = useState(false);
  const avatarMenuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!avatarMenuOpen) return;

    function onDocClick(e: MouseEvent) {
      const target = e.target as Node | null;
      if (!target) return;
      if (avatarMenuRef.current && avatarMenuRef.current.contains(target)) return;
      setAvatarMenuOpen(false);
    }

    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [avatarMenuOpen]);

  const handleLogout = () => {
    clearTokens();
    setAvatarMenuOpen(false);
    router.replace("/");
  };

  const showAuthGate = shouldSkipAuthFetch || meLoading;
  const authGateBlocked = showAuthGate || meStatus === 401;
  const avatarMenuId = useMemo(() => `avatar-menu-${Math.random().toString(16).slice(2)}`, []);

  if (authGateBlocked) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 border-r border-primary/10 bg-background flex flex-col shrink-0">
        <div className="p-6 flex items-center gap-3">
          <div className="size-10 bg-primary flex items-center justify-center rounded-lg">
            <span className="material-symbols-outlined text-primary-foreground text-2xl font-bold" aria-hidden>
              psychology
            </span>
          </div>
          <div className="flex flex-col">
            <h1 className="text-slate-100 text-lg font-bold leading-none">SalesMind</h1>
            <p className="text-primary text-xs font-medium uppercase tracking-widest">Experimental</p>
          </div>
        </div>
        <nav className="flex-1 px-4 space-y-2 py-4">
          {navItems.map(({ href, label, icon }) => {
            const isActive =
              pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2 rounded cursor-pointer transition-colors ${
                  isActive
                    ? "bg-primary/20 text-primary"
                    : "text-slate-400 hover:bg-primary/10 hover:text-primary"
                }`}
              >
                <NavIcon name={icon} />
                <span className="text-sm font-medium">{label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-primary/10">
          <Link
            href="/leads"
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-3 rounded flex items-center justify-center gap-2 transition-transform active:scale-95"
          >
            <span className="material-symbols-outlined text-lg" aria-hidden>add_circle</span>
            <span>New Lead</span>
          </Link>
        </div>
      </aside>
      <div className="flex-1 flex flex-col overflow-hidden bg-background">
        {/* Single shared header */}
        <header className="h-16 border-b border-primary/10 flex items-center justify-between px-8 bg-background/80 backdrop-blur-md shrink-0">
          <div className="flex items-center gap-4">
            {breadcrumb ? (
              <div className="flex items-center gap-2 text-sm">
                <Link
                  href={breadcrumb.href}
                  className="text-slate-500 hover:text-primary transition-colors"
                >
                  {breadcrumb.label}
                </Link>
                <span className="material-symbols-outlined text-xs text-slate-500">chevron_right</span>
                <span className="text-primary font-medium">{title}</span>
              </div>
            ) : (
              <h2 className="text-xl font-bold tracking-tight text-slate-100">{title}</h2>
            )}
            <div className="relative w-64 hidden sm:block">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">
                search
              </span>
              <input
                type="search"
                className="w-full bg-primary/5 border border-primary/20 rounded-lg pl-10 pr-4 py-1.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="Search..."
                aria-label="Search"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              className="p-2 text-slate-500 hover:text-primary transition-colors"
              aria-label="Notifications"
            >
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <div className="h-8 w-px bg-primary/10" />
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-xs font-bold leading-none text-slate-100 truncate">{displayName}</p>
                <p className="text-[10px] text-primary truncate">{me?.email ?? "Sales"}</p>
              </div>
              <div className="relative">
                <button
                  type="button"
                  className="size-9 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-primary font-bold text-sm hover:bg-primary/30 transition-colors"
                  aria-haspopup="menu"
                  aria-expanded={avatarMenuOpen}
                  aria-controls={avatarMenuId}
                  onClick={() => setAvatarMenuOpen((v) => !v)}
                >
                  {avatarInitials}
                </button>

                {avatarMenuOpen && (
                  <div
                    id={avatarMenuId}
                    ref={avatarMenuRef}
                    role="menu"
                    aria-label="User menu"
                    className="absolute right-0 mt-2 w-44 rounded-lg border border-primary/20 bg-background/95 backdrop-blur-md shadow-lg overflow-hidden"
                  >
                    <button
                      type="button"
                      role="menuitem"
                      className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-primary/10 transition-colors"
                      onClick={handleLogout}
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 flex flex-col min-h-0">
          {children}
        </main>
      </div>
    </div>
  );
}
