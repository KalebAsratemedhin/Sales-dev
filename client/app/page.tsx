import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#120e08] text-slate-100 overflow-x-hidden font-sans">
      <div
        className="fixed inset-0 pointer-events-none opacity-30"
        style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, #393328 1px, transparent 0)",
          backgroundSize: "40px 40px",
        }}
      />
      {/* Nav */}
      <nav className="border-b border-primary/20 bg-[#120e08]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="size-8 bg-primary flex items-center justify-center rounded">
              <span className="material-symbols-outlined text-primary-foreground font-bold">psychology</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-slate-100 uppercase italic">SalesMind</h2>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <span className="text-xs font-medium uppercase tracking-widest text-slate-400">Architecture</span>
            <span className="text-xs font-medium uppercase tracking-widest text-slate-400">Docs</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/sign-in"
              className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded text-xs font-bold uppercase tracking-tighter transition-all"
            >
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="border border-primary/30 px-4 py-2 rounded text-xs font-bold uppercase tracking-tighter text-primary hover:bg-primary/10 transition-all"
            >
              Initiate Sequence
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <main className="relative min-h-[80vh] border-b border-primary/10">
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: "radial-gradient(circle at 1px 1px, #393328 1px, transparent 0)",
            backgroundSize: "40px 40px",
          }}
        />
        <div className="max-w-7xl mx-auto px-6 pt-16 pb-24 relative">
          <div className="grid grid-cols-12 gap-px bg-primary/10 border border-primary/20">
            <div className="col-span-12 lg:col-span-8 p-12 bg-[#120e08] flex flex-col justify-center relative overflow-hidden">
              <div className="absolute top-4 left-4 flex gap-2">
                <div className="w-2 h-2 rounded-full bg-primary/40" />
                <div className="w-2 h-2 rounded-full bg-primary/20" />
                <div className="w-2 h-2 rounded-full bg-primary/10" />
              </div>
              <h1 className="text-5xl md:text-7xl font-bold leading-[0.9] tracking-tighter uppercase mb-6">
                Autonomous <br />
                <span className="text-primary italic">SDR Orchestration</span>
              </h1>
              <p className="text-slate-400 max-w-xl text-lg font-light leading-relaxed">
                Moving beyond simple automation. SalesMind deploys persistent AI agents that research, strategize, and execute full-cycle outreach without human intervention.
              </p>
              <div className="mt-10 flex gap-4">
                <Link
                  href="/sign-up"
                  className="border border-primary/30 px-6 py-3 flex items-center gap-3 bg-primary/5 hover:bg-primary/10 transition-colors group"
                >
                  <span className="material-symbols-outlined text-primary group-hover:scale-110 transition-transform">bolt</span>
                  <span className="text-xs font-bold uppercase tracking-widest">Get Started</span>
                </Link>
                <Link
                  href="/sign-in"
                  className="border border-slate-700 px-6 py-3 flex items-center gap-3 hover:bg-slate-800 transition-colors group"
                >
                  <span className="material-symbols-outlined text-slate-400 group-hover:text-primary">terminal</span>
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-300">Sign In</span>
                </Link>
              </div>
            </div>
            <div className="col-span-12 lg:col-span-4 p-8 bg-[#2a241a]/30 flex flex-col justify-center border-l border-primary/10">
              <div className="bg-primary/10 p-6 rounded border border-primary/20">
                <p className="text-sm text-slate-300 leading-relaxed">
                  &quot;SalesMind agents research, personalize, and reach out at scale—so your team can focus on closing.&quot;
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Workflow phases */}
      <section className="bg-[#120e08] py-12 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-2 h-2 bg-primary rounded-full" />
            <h2 className="text-sm font-bold uppercase tracking-[0.3em] text-primary/80">How it works</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-0 border border-primary/20 bg-[#2a241a]/10 rounded-lg overflow-hidden">
            <div className="p-10 border-r border-primary/10 hover:bg-primary/5 transition-colors relative">
              <div className="mb-8 flex items-center gap-4">
                <div className="size-12 rounded-full border border-primary/30 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-2xl">travel_explore</span>
                </div>
                <div className="h-px flex-1 bg-linear-to-r from-primary/40 to-transparent" />
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tighter mb-4">Deep Research</h3>
              <p className="text-xs text-slate-400 font-light leading-relaxed mb-6 italic">Aggregating unstructured data from 50+ neural nodes including SEC filings, social graphs, and intent signals.</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60"><span className="size-1 bg-primary" /> Domain research</div>
                <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60"><span className="size-1 bg-primary" /> Intent signals</div>
              </div>
            </div>
            <div className="p-10 border-r border-primary/10 hover:bg-primary/5 transition-colors">
              <div className="mb-8 flex items-center gap-4">
                <div className="size-12 rounded-full border border-primary/30 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-2xl">psychology_alt</span>
                </div>
                <div className="h-px flex-1 bg-linear-to-r from-primary/40 to-transparent" />
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tighter mb-4">Neural Synthesis</h3>
              <p className="text-xs text-slate-400 font-light leading-relaxed mb-6 italic">Constructing hyper-personalized messaging architectures by mapping psychological profiles to business pain points.</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60"><span className="size-1 bg-primary" /> Persona mapping</div>
                <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60"><span className="size-1 bg-primary" /> Content optimization</div>
              </div>
            </div>
            <div className="p-10 hover:bg-primary/5 transition-colors">
              <div className="mb-8 flex items-center gap-4">
                <div className="size-12 rounded-full border border-primary/30 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-2xl">hub</span>
                </div>
                <div className="h-px flex-1 bg-linear-to-r from-primary/40 to-transparent" />
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tighter mb-4">Auto Execution</h3>
              <p className="text-xs text-slate-400 font-light leading-relaxed mb-6 italic">Multi-channel deployment synchronized with prospect activity windows for maximum conversion probability.</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60"><span className="size-1 bg-primary" /> Omni-channel routing</div>
                <div className="flex items-center gap-2 text-[10px] font-mono text-primary/60"><span className="size-1 bg-primary" /> Real-time pivot</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Continuous Loop Intelligence */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h3 className="text-xs font-bold text-primary tracking-[0.3em] uppercase mb-4">Neural Orchestration</h3>
            <h2 className="text-4xl font-bold mb-6">Continuous Loop Intelligence</h2>
            <p className="text-slate-400 text-lg leading-relaxed mb-8">
              Unlike standard sequencing tools, SalesMind operates in a recursive loop. Every response, bounce, and click is fed back into the agent&apos;s neural model to refine the next interaction.
            </p>
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 border border-primary/10 rounded bg-primary/5">
                <span className="material-symbols-outlined text-primary mt-1">visibility</span>
                <div>
                  <h4 className="font-bold text-sm uppercase">Unstructured Data Intake</h4>
                  <p className="text-xs text-slate-500">Crawls annual reports, podcasts, and social graphs for deep intent signals.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 border border-slate-800 rounded">
                <span className="material-symbols-outlined text-slate-400 mt-1">model_training</span>
                <div>
                  <h4 className="font-bold text-sm uppercase">Persona Synthesis</h4>
                  <p className="text-xs text-slate-500">Builds a unique messaging psychological profile for every individual prospect.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 border border-slate-800 rounded">
                <span className="material-symbols-outlined text-slate-400 mt-1">send</span>
                <div>
                  <h4 className="font-bold text-sm uppercase">Autonomous Delivery</h4>
                  <p className="text-xs text-slate-500">Executes the perfect message at the precise window of maximum impact.</p>
                </div>
              </div>
            </div>
          </div>
          {/* Flow diagram */}
          <div
            className="relative aspect-square border border-primary/20 bg-[#2a241a]/10 rounded-xl flex items-center justify-center p-8 overflow-hidden"
            style={{
              backgroundImage: "radial-gradient(circle at 1px 1px, #393328 1px, transparent 0)",
              backgroundSize: "40px 40px",
            }}
          >
            <div className="absolute inset-0 opacity-30 rounded-xl" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, #393328 1px, transparent 0)", backgroundSize: "40px 40px" }} />
            <div className="relative z-10 w-full h-full flex flex-col items-center justify-center gap-12">
              <div className="w-32 h-12 border-2 border-primary rounded flex items-center justify-center bg-[#120e08] font-mono text-[10px] uppercase font-bold text-primary shadow-[0_0_15px_rgba(245,163,10,0.3)]">
                Data Source
              </div>
              <div className="w-px h-12 bg-linear-to-b from-primary to-transparent" />
              <div className="relative">
                <div className="absolute -inset-4 bg-primary/20 rounded-full animate-pulse" />
                <div className="w-48 h-48 rounded-full border-2 border-primary border-dashed flex items-center justify-center bg-[#120e08]/80 backdrop-blur-sm relative z-10">
                  <span className="material-symbols-outlined text-5xl text-primary">psychology</span>
                </div>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
                  <span className="material-symbols-outlined text-xs">search</span>
                </div>
                <div className="absolute bottom-0 left-0 w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white">
                  <span className="material-symbols-outlined text-xs">mail</span>
                </div>
                <div className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white">
                  <span className="material-symbols-outlined text-xs">share</span>
                </div>
              </div>
              <div className="w-px h-12 bg-linear-to-t from-primary to-transparent" />
              <div className="w-32 h-12 border-2 border-primary/40 rounded flex items-center justify-center bg-[#120e08] font-mono text-[10px] uppercase font-bold text-slate-300">
                Pipeline
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Distributed Autonomous Presence */}
      <section className="border-t border-primary/20 bg-[#2a241a]/10 py-24 overflow-hidden relative">
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-xs font-bold text-primary tracking-[0.4em] uppercase mb-4">Global Infrastructure</h2>
            <h3 className="text-4xl font-bold">Distributed Autonomous Presence</h3>
          </div>
          <div className="relative bg-[#120e08] border border-primary/20 rounded-xl h-[500px] overflow-hidden">
            {/* Mock map background */}
            <div
              className="absolute inset-0 opacity-20 grayscale"
              style={{
                backgroundImage: "radial-gradient(circle at 20% 30%, #393328 0%, transparent 40%), radial-gradient(circle at 80% 70%, #393328 0%, transparent 40%), radial-gradient(circle at 50% 50%, #2a241a 0%, transparent 70%)",
                backgroundSize: "100% 100%",
              }}
            />
            <div
              className="absolute inset-0 opacity-30"
              style={{
                backgroundImage: "radial-gradient(circle at 1px 1px, #393328 1px, transparent 0)",
                backgroundSize: "32px 32px",
              }}
            />
            {/* Overlay data points */}
            <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-primary rounded-full animate-ping" />
            <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-primary rounded-full" />
            <div className="absolute top-1/3 left-1/2 w-2 h-2 bg-primary/60 rounded-full" />
            <div className="absolute bottom-1/4 right-1/3 w-3 h-3 bg-primary rounded-full animate-ping" />
            <div className="absolute bottom-1/4 right-1/3 w-3 h-3 bg-primary rounded-full" />
            {/* Floating sidebar */}
            <div className="absolute right-6 top-6 bottom-6 w-72 bg-[#120e08]/90 border border-primary/20 backdrop-blur-sm p-6 flex flex-col justify-end">
              <Link
                href="/sign-up"
                className="w-full border border-primary text-primary py-3 rounded text-xs font-bold uppercase tracking-widest hover:bg-primary hover:text-primary-foreground transition-all text-center block"
              >
                Scale Operations
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 py-24 relative">
        <div className="text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to deploy autonomous SDRs?</h2>
          <p className="text-slate-400 text-lg mb-8 max-w-xl mx-auto">Sign up to access the dashboard and connect your pipeline.</p>
          <Link
            href="/sign-up"
            className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded font-bold uppercase tracking-widest transition-all"
          >
            <span className="material-symbols-outlined">bolt</span>
            Get Started
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#120e08] border-t border-primary/20 py-12 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="size-6 bg-primary flex items-center justify-center rounded">
                <span className="material-symbols-outlined text-primary-foreground text-sm font-bold">psychology</span>
              </div>
              <span className="text-lg font-bold tracking-tight text-slate-100 uppercase italic">SalesMind</span>
            </div>
            <p className="text-[10px] font-mono text-slate-600">© SalesMind. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
