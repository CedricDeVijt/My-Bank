export function AuthTabs({ mode, setMode }: { mode: "login" | "register"; setMode: (m: "login" | "register") => void }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="text-sm uppercase tracking-[0.25em] text-amber-200">Authentication</p>
      </div>

      <div className="rounded-full border border-white/10 bg-white/5 p-1">
        <button
          type="button"
          aria-pressed={mode === "login"}
          onClick={() => setMode("login")}
          className={`rounded-full px-4 py-2 text-sm font-medium transition ${
            mode === "login" ? "bg-amber-300 text-slate-950" : "text-slate-300 hover:text-white"
          }`}
        >
          Login
        </button>
        <button
          type="button"
          aria-pressed={mode === "register"}
          onClick={() => setMode("register")}
          className={`rounded-full px-4 py-2 text-sm font-medium transition ${
            mode === "register" ? "bg-amber-300 text-slate-950" : "text-slate-300 hover:text-white"
          }`}
        >
          Create account
        </button>
      </div>
    </div>
  );
}


