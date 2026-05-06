import type React from "react";

export function AuthPanel({ children }: { children: React.ReactNode }) {
  return (
    <section className="flex items-center justify-center bg-slate-900 px-6 py-14 sm:px-10 lg:px-16">
      <div className="w-full max-w-lg rounded-3xl border border-white/8 bg-slate-950/90 p-6 shadow-2xl shadow-amber-950/20 backdrop-blur sm:p-8">
        {children}
      </div>
    </section>
  );
}

