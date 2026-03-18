"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SignUpPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="min-h-screen bg-[#120e08] text-slate-100 flex flex-col font-sans">
      <div
        className="fixed inset-0 pointer-events-none opacity-50"
        style={{
          backgroundImage: "radial-gradient(circle at 2px 2px, rgba(245, 163, 10, 0.05) 1px, transparent 0)",
          backgroundSize: "24px 24px",
        }}
      />
      <header className="flex items-center justify-between border-b border-primary/20 bg-[#120e08]/80 backdrop-blur-md px-6 md:px-10 py-4 sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex items-center justify-center size-10 bg-primary/10 border border-primary/30 rounded">
            <span className="material-symbols-outlined text-primary">terminal</span>
          </div>
          <div className="flex flex-col">
            <h2 className="text-slate-100 text-lg font-bold leading-tight tracking-tight uppercase">SalesMind</h2>
            <span className="text-[10px] text-primary font-bold tracking-[0.2em] uppercase">Protocol</span>
          </div>
        </Link>
        <div className="flex items-center gap-4">
          <Link
            href="/sign-in"
            className="flex items-center justify-center rounded border border-primary/20 h-10 px-4 text-slate-400 hover:bg-primary/5 transition-colors text-sm font-medium"
          >
            Log In
          </Link>
          <button type="button" className="flex size-10 items-center justify-center rounded border border-primary/20 bg-primary/5 text-primary" aria-label="Help">
            <span className="material-symbols-outlined text-xl">help_outline</span>
          </button>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4 md:p-8 relative z-10">
        <div className="w-full max-w-[520px] bg-slate-900/50 border border-primary/10 shadow-2xl overflow-hidden rounded-lg">
          <div className="h-1 w-full bg-slate-800">
            <div className="h-full bg-primary w-1/3" />
          </div>
          <div className="p-8 md:p-12">
            <div className="mb-10">
              <h1 className="text-slate-100 text-3xl font-black leading-tight tracking-tight uppercase mb-2">Initialize Account</h1>
              <p className="text-slate-500 text-sm font-medium border-l-2 border-primary pl-4 py-1 uppercase tracking-wider">Authentication Module v2.0.4</p>
            </div>
            <form
              className="space-y-6"
              onSubmit={(e) => {
                e.preventDefault();
                router.push("/dashboard");
              }}
            >
              <div className="space-y-2">
                <label className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-slate-400">
                  <span>Identity Label</span>
                  <span className="text-primary/50">Required</span>
                </label>
                <div className="relative group">
                  <input
                    className="w-full bg-slate-950/50 border border-slate-800 text-slate-100 rounded focus:ring-1 focus:ring-primary focus:border-primary px-4 py-4 text-sm font-medium transition-all outline-none"
                    placeholder="LEGAL FULL NAME"
                    type="text"
                    name="name"
                    required
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                    <span className="material-symbols-outlined text-xl">fingerprint</span>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <label className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-slate-400">
                  <span>Communication Node</span>
                  <span className="text-primary/50">Email</span>
                </label>
                <div className="relative group">
                  <input
                    className="w-full bg-slate-950/50 border border-slate-800 text-slate-100 rounded focus:ring-1 focus:ring-primary focus:border-primary px-4 py-4 text-sm font-medium transition-all outline-none"
                    placeholder="OPERATOR@NETWORK.COM"
                    type="email"
                    name="email"
                    required
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                    <span className="material-symbols-outlined text-xl">alternate_email</span>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <label className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-slate-400">
                  <span>Security Key</span>
                  <span className="text-primary/50">Encrypted</span>
                </label>
                <div className="flex w-full items-stretch rounded overflow-hidden">
                  <input
                    className="flex-1 bg-slate-950/50 border border-slate-800 border-r-0 text-slate-100 rounded-l focus:ring-1 focus:ring-primary focus:border-primary px-4 py-4 text-sm font-medium transition-all outline-none"
                    placeholder="••••••••••••"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    required
                  />
                  <button
                    type="button"
                    className="flex items-center justify-center px-4 bg-slate-950/50 border border-slate-800 border-l-0 text-slate-400 hover:text-primary transition-colors rounded-r"
                    onClick={() => setShowPassword((p) => !p)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <span className="material-symbols-outlined text-xl">{showPassword ? "visibility_off" : "visibility"}</span>
                  </button>
                </div>
                <div className="flex gap-1 mt-2">
                  <div className="h-1 flex-1 bg-primary" />
                  <div className="h-1 flex-1 bg-primary" />
                  <div className="h-1 flex-1 bg-primary/20" />
                  <div className="h-1 flex-1 bg-primary/20" />
                </div>
              </div>
              <div className="flex items-start gap-3 py-2">
                <div className="flex h-5 items-center">
                  <input
                    className="h-4 w-4 rounded border-slate-700 text-primary focus:ring-primary bg-transparent"
                    id="terms"
                    name="terms"
                    type="checkbox"
                    required
                  />
                </div>
                <div className="text-xs">
                  <label className="font-medium text-slate-400 uppercase tracking-tighter cursor-pointer" htmlFor="terms">
                    I accept the <a className="text-primary hover:underline" href="#">operational directives</a> and <a className="text-primary hover:underline" href="#">privacy protocols</a>.
                  </label>
                </div>
              </div>
              <button
                type="submit"
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-4 rounded font-bold uppercase tracking-[0.2em] text-sm flex items-center justify-center gap-2 transition-all group"
              >
                <span>Generate Credentials</span>
                <span className="material-symbols-outlined text-lg group-hover:translate-x-1 transition-transform">bolt</span>
              </button>
            </form>
            <div className="mt-8 pt-8 border-t border-primary/10 flex flex-col items-center gap-4">
              <p className="text-[10px] text-slate-500 uppercase tracking-[0.3em] font-bold">Or connect via</p>
              <div className="flex gap-4 w-full">
                <button
                  type="button"
                  className="flex-1 flex items-center justify-center gap-2 py-3 border border-slate-800 hover:border-primary/50 transition-colors rounded text-xs font-bold uppercase tracking-wider text-slate-300"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.9 3.34-2.12 4.41-1.18 1.04-3.04 1.94-6.32 1.94-5.26 0-9.61-4.26-9.61-9.52s4.35-9.52 9.61-9.52c3.04 0 5.4 1.12 7.14 2.76l2.36-2.36C19.18 1.04 16.08 0 12.48 0 5.58 0 0 5.58 0 12.5s5.58 12.5 12.5 12.5c3.75 0 6.58-1.25 8.75-3.52 2.21-2.21 2.92-5.32 2.92-7.82 0-.54-.04-1.05-.12-1.54h-11.57z" /></svg>
                  Kernel
                </button>
                <button
                  type="button"
                  className="flex-1 flex items-center justify-center gap-2 py-3 border border-slate-800 hover:border-primary/50 transition-colors rounded text-xs font-bold uppercase tracking-wider text-slate-300"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.43.372.82 1.102.82 2.222 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" /></svg>
                  Git
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="p-10 flex flex-col items-center justify-center text-center space-y-4 relative z-10">
        <div className="flex gap-8 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-600">
          <span className="hover:text-primary cursor-default">Status: Operational</span>
          <span className="hover:text-primary cursor-default">Node: US-EAST-1</span>
          <span className="hover:text-primary cursor-default">Encryption: AES-256</span>
        </div>
        <p className="text-xs text-slate-500">© SalesMind. All rights reserved.</p>
      </footer>
    </div>
  );
}
