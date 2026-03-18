"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SignInPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="min-h-screen bg-[#120e08] text-slate-100 flex flex-col font-sans">
      <div
        className="fixed inset-0 pointer-events-none opacity-50"
        style={{
          backgroundImage: "radial-gradient(circle at 2px 2px, rgba(245, 163, 10, 0.05) 1px, transparent 0)",
          backgroundSize: "40px 40px",
        }}
      />
      <header className="relative z-10 w-full px-6 py-6 flex justify-between items-center border-b border-primary/10">
        <Link href="/" className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded border border-primary/20">
            <span className="material-symbols-outlined text-primary text-2xl">shield_lock</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-bold tracking-widest uppercase text-primary">SalesMind</span>
            <span className="text-[10px] text-slate-500 uppercase tracking-[0.2em]">Secure Access Protocol</span>
          </div>
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-xs font-medium text-slate-500 hidden sm:block">ENCRYPTED CONNECTION</span>
          <div className="size-2 rounded-full bg-primary animate-pulse shadow-[0_0_10px_rgba(245,163,10,0.5)]" />
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md bg-slate-900/40 backdrop-blur-xl border border-primary/20 rounded-lg shadow-[0_25px_50px_-12px_rgba(0,0,0,0.8)] overflow-hidden">
          <div className="h-1.5 w-full bg-primary/10">
            <div className="h-full w-1/3 bg-primary shadow-[0_0_15px_rgba(245,163,10,0.4)]" />
          </div>
          <div className="p-8 sm:p-12">
            <div className="mb-10 text-center">
              <h1 className="text-3xl font-bold tracking-tight text-slate-100 mb-2">Identify Yourself</h1>
              <p className="text-slate-500 text-sm">Enter credentials for secure access</p>
            </div>
            <form
              className="space-y-6"
              onSubmit={(e) => {
                e.preventDefault();
                router.push("/dashboard");
              }}
            >
              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase tracking-widest text-primary/70 ml-1">Identity UID</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="material-symbols-outlined text-slate-500 group-focus-within:text-primary transition-colors text-xl">alternate_email</span>
                  </div>
                  <input
                    className="block w-full pl-11 pr-4 py-4 bg-[#221c10]/50 border border-primary/10 rounded text-slate-100 placeholder:text-slate-700 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-sm font-medium"
                    placeholder="operator@salesmind.io"
                    type="email"
                    name="email"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-end px-1">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-primary/70">Access Key</label>
                  <Link href="#" className="text-[10px] font-bold uppercase tracking-widest text-slate-500 hover:text-primary transition-colors">Recovery</Link>
                </div>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="material-symbols-outlined text-slate-500 group-focus-within:text-primary transition-colors text-xl">lock</span>
                  </div>
                  <input
                    className="block w-full pl-11 pr-12 py-4 bg-[#221c10]/50 border border-primary/10 rounded text-slate-100 placeholder:text-slate-700 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-sm font-medium"
                    placeholder="••••••••••••"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-primary transition-colors"
                    onClick={() => setShowPassword((p) => !p)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <span className="material-symbols-outlined text-xl">{showPassword ? "visibility_off" : "visibility"}</span>
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-3 px-1">
                <input
                  className="w-4 h-4 bg-[#221c10] border-primary/20 rounded text-primary focus:ring-primary focus:ring-offset-[#221c10] transition-all"
                  id="mfa"
                  type="checkbox"
                  name="mfa"
                />
                <label className="text-xs text-slate-400 cursor-pointer" htmlFor="mfa">Require Multi-Factor Authentication</label>
              </div>
              <button
                type="submit"
                className="w-full py-4 bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-sm uppercase tracking-widest rounded-lg shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 group"
              >
                Establish Connection
                <span className="material-symbols-outlined text-lg group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </button>
            </form>
            <div className="mt-10 flex items-center justify-center gap-4 opacity-40">
              <div className="h-px w-8 bg-primary/30" />
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Security Clearance Required</span>
              <div className="h-px w-8 bg-primary/30" />
            </div>
          </div>
          <div className="px-8 py-4 bg-primary/5 border-t border-primary/10 flex justify-between items-center">
            <div className="flex gap-2">
              <div className="size-1.5 rounded-full bg-primary/40" />
              <div className="size-1.5 rounded-full bg-primary/40" />
              <div className="size-1.5 rounded-full bg-primary/40" />
            </div>
            <span className="text-[9px] text-slate-600 font-mono tracking-tighter uppercase">Protocol-v4.2.0-STABLE</span>
          </div>
        </div>
      </main>

      <footer className="p-8 flex flex-col sm:flex-row justify-between items-center gap-4 relative z-10">
        <div className="text-[10px] text-slate-500 uppercase tracking-widest">© SalesMind</div>
        <div className="flex gap-6">
          <Link href="#" className="text-[10px] text-slate-500 hover:text-primary transition-colors uppercase tracking-widest font-bold">Terms</Link>
          <Link href="#" className="text-[10px] text-slate-500 hover:text-primary transition-colors uppercase tracking-widest font-bold">Privacy</Link>
          <Link href="/" className="text-[10px] text-slate-500 hover:text-primary transition-colors uppercase tracking-widest font-bold">Home</Link>
        </div>
      </footer>
    </div>
  );
}
