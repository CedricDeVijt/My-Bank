export function AuthTab({mode, setMode}: { mode: "login" | "register"; setMode: (m: "login" | "register") => void }) {
    return (
        <div className="inline-flex rounded-full border border-white/10 bg-white/5 p-1 shadow-inner shadow-black/20">
            <button
                type="button"
                aria-pressed={mode === "login"}
                onClick={() => setMode("login")}
                className={`rounded-full px-5 py-2 text-sm font-semibold transition duration-200 ${
                    mode === "login"
                        ? "bg-amber-300 text-slate-950 shadow-md shadow-amber-300/30"
                        : "text-slate-300 hover:text-white"
                }`}
            >
                Login
            </button>

            <button
                type="button"
                aria-pressed={mode === "register"}
                onClick={() => setMode("register")}
                className={`rounded-full px-5 py-2 text-sm font-semibold transition duration-200 ${
                    mode === "register"
                        ? "bg-amber-300 text-slate-950 shadow-md shadow-amber-300/30"
                        : "text-slate-300 hover:text-white"
                }`}
            >
                Register
            </button>
        </div>
    );
}