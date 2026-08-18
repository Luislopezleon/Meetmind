import { TopNav } from "@/components/TopNav";
import { DotGridBackground } from "@/components/DotGridBackground";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <DotGridBackground />
      <TopNav />
      {/* Dev banner */}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-full bg-[#111] border border-amber-500/20 shadow-lg">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
        <span className="text-[11px] text-amber-400/80">Development mode — data may be reset</span>
      </div>
      <main className="relative z-10 max-w-6xl mx-auto px-6 pt-28 pb-16">
        {children}
      </main>
    </>
  );
}
