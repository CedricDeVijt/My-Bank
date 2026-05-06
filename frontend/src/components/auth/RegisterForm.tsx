import type React from "react";
import type { UserCreate } from "../../types";

export function RegisterForm({
  registerForm,
  setRegisterForm,
  onSubmit,
  loading,
}: {
  registerForm: UserCreate;
  setRegisterForm: React.Dispatch<React.SetStateAction<UserCreate>>;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  loading: boolean;
}) {
  return (
    <form className="mt-8 space-y-5" onSubmit={onSubmit}>
      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor="first-name" className="mb-2 block text-sm font-medium text-slate-200">
            First name
          </label>
          <input
            id="first-name"
            type="text"
            autoComplete="given-name"
            required
            value={registerForm.first_name}
            onChange={(event) => setRegisterForm((current) => ({ ...current, first_name: event.target.value }))}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
            placeholder="Jane"
          />
        </div>

        <div>
          <label htmlFor="last-name" className="mb-2 block text-sm font-medium text-slate-200">
            Last name
          </label>
          <input
            id="last-name"
            type="text"
            autoComplete="family-name"
            required
            value={registerForm.last_name}
            onChange={(event) => setRegisterForm((current) => ({ ...current, last_name: event.target.value }))}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
            placeholder="Doe"
          />
        </div>
      </div>

      <div>
        <label htmlFor="register-email" className="mb-2 block text-sm font-medium text-slate-200">
          Email address
        </label>
        <input
          id="register-email"
          type="email"
          autoComplete="email"
          required
          value={registerForm.email}
          onChange={(event) => setRegisterForm((current) => ({ ...current, email: event.target.value }))}
          className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
          placeholder="you@example.com"
        />
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor="register-password" className="mb-2 block text-sm font-medium text-slate-200">
            Password
          </label>
          <input
            id="register-password"
            type="password"
            autoComplete="new-password"
            minLength={12}
            required
            value={registerForm.password}
            onChange={(event) => setRegisterForm((current) => ({ ...current, password: event.target.value }))}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
            placeholder="At least 12 characters"
          />
        </div>

        <div>
          <label htmlFor="date-of-birth" className="mb-2 block text-sm font-medium text-slate-200">
            Date of birth
          </label>
          <input
            id="date-of-birth"
            type="date"
            required
            value={registerForm.date_of_birth}
            onChange={(event) => setRegisterForm((current) => ({ ...current, date_of_birth: event.target.value }))}
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-amber-300 focus:ring-2 focus:ring-amber-300/20"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="flex w-full items-center justify-center rounded-2xl bg-amber-300 px-4 py-3 font-semibold text-slate-950 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {loading ? "Creating account..." : "Create account"}
      </button>
    </form>
  );
}

