import type React from "react";
import type { UserLogin } from "../../types";

export function LoginForm({
  loginForm,
  setLoginForm,
  onSubmit,
  loading,
}: {
  loginForm: UserLogin;
  setLoginForm: React.Dispatch<React.SetStateAction<UserLogin>>;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  loading: boolean;
}) {
  return (
    <form className="mt-8 space-y-5" onSubmit={onSubmit}>
      <div>
        <label htmlFor="login-email" className="mb-2 block text-sm font-medium text-slate-200">
          Email address
        </label>
        <input
          id="login-email"
          type="email"
          autoComplete="email"
          required
          value={loginForm.email}
          onChange={(event) => setLoginForm((current) => ({ ...current, email: event.target.value }))}
          className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
          placeholder="you@example.com"
        />
      </div>

      <div>
        <label htmlFor="login-password" className="mb-2 block text-sm font-medium text-slate-200">
          Password
        </label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          required
          value={loginForm.password}
          onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
          className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
          placeholder="Your password"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="flex w-full items-center justify-center rounded-2xl bg-amber-300 px-4 py-3 font-semibold text-slate-950 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {loading ? "Signing in..." : "Login"}
      </button>
    </form>
  );
}

