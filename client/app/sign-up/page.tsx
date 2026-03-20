"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { setTokens } from "@/lib/authStorage";
import { useRegisterMutation } from "@/store/authApi";
import { toast } from "@/components/ui/use-toast";
import type { ChangeEvent, FormEvent } from "react";

function findFirstString(value: unknown, depth = 0): string | null {
  if (depth > 4) return null;
  if (typeof value === "string") return value.trim() ? value : null;

  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findFirstString(item, depth + 1);
      if (found) return found;
    }
    return null;
  }

  if (value && typeof value === "object") {
    for (const v of Object.values(value as Record<string, unknown>)) {
      const found = findFirstString(v, depth + 1);
      if (found) return found;
    }
  }

  return null;
}

function extractBackendMessage(err: unknown): string | null {
  const data = (err as any)?.data;
  console.log("error extraction ", err)
  return (
    findFirstString(data?.email) ??
    findFirstString(data) ??
    (typeof (err as any)?.message === "string" ? (err as any).message : null) ??
    null
  );
}

export default function SignUpPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [register, { isLoading }] = useRegisterMutation();

  const toggleShowPassword = () => setShowPassword((p) => !p);
  const handleFullNameChange = (e: ChangeEvent<HTMLInputElement>) => setFullName(e.target.value);
  const handleEmailChange = (e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value);
  const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const tokens = await register({ full_name: fullName, email, password }).unwrap();
      setTokens({ access: tokens.access, refresh: tokens.refresh });
      router.push("/dashboard");
    } catch (err) {
      const backendMessage = extractBackendMessage(err) ?? "Sign up failed";
      toast({
        title: backendMessage,
        description: "Please check the fields and try again.",
        variant: "destructive",
      });
    }
  };

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
            </div>
            <form
              className="space-y-6"
              onSubmit={handleSubmit}
            >
              <div className="space-y-2">
                <label className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-slate-400">
                  <span>Full name</span>
                  <span className="text-primary/50">Required</span>
                </label>
                <div className="relative group">
                  <input
                    className="w-full bg-slate-950/50 border border-slate-800 text-slate-100 rounded focus:ring-1 focus:ring-primary focus:border-primary px-4 py-4 text-sm font-medium transition-all outline-none"
                    placeholder="Jane Doe"
                    type="text"
                    name="name"
                    value={fullName}
                    onChange={handleFullNameChange}
                    required
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                    <span className="material-symbols-outlined text-xl">fingerprint</span>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <label className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-slate-400">
                  <span>Email</span>
                  <span className="text-primary/50">Email</span>
                </label>
                <div className="relative group">
                  <input
                    className="w-full bg-slate-950/50 border border-slate-800 text-slate-100 rounded focus:ring-1 focus:ring-primary focus:border-primary px-4 py-4 text-sm font-medium transition-all outline-none"
                    placeholder="you@salesmind.io"
                    type="email"
                    name="email"
                    value={email}
                    onChange={handleEmailChange}
                    required
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                    <span className="material-symbols-outlined text-xl">alternate_email</span>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <label className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-slate-400">
                  <span>Password</span>
                  <span className="text-primary/50">Encrypted</span>
                </label>
                <div className="flex w-full items-stretch rounded overflow-hidden">
                  <input
                    className="flex-1 bg-slate-950/50 border border-slate-800 border-r-0 text-slate-100 rounded-l focus:ring-1 focus:ring-primary focus:border-primary px-4 py-4 text-sm font-medium transition-all outline-none"
                    placeholder="••••••••••••"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={password}
                    onChange={handlePasswordChange}
                    required
                  />
                  <button
                    type="button"
                    className="flex items-center justify-center px-4 bg-slate-950/50 border border-slate-800 border-l-0 text-slate-400 hover:text-primary transition-colors rounded-r"
                    onClick={toggleShowPassword}
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
                disabled={isLoading}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-4 rounded font-bold uppercase tracking-[0.2em] text-sm flex items-center justify-center gap-2 transition-all group disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <span>Generate Credentials</span>
                <span className="material-symbols-outlined text-lg group-hover:translate-x-1 transition-transform">bolt</span>
              </button>
            </form>
            <div className="mt-6 text-sm text-slate-500 text-center">
              Already have an account?{" "}
              <Link href="/sign-in" className="text-primary hover:underline font-bold">
                Log in
              </Link>
            </div>
          </div>
        </div>
      </main>

    </div> 
  );
}
