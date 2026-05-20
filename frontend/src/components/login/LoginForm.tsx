import type { FormEvent, Dispatch, SetStateAction } from "react";
import type { UserLogin } from "../../types";

export function LoginForm({
  loginForm,
  setLoginForm,
  onSubmit,
  loading,
}: {
  loginForm: UserLogin;
  setLoginForm: Dispatch<SetStateAction<UserLogin>>;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void | Promise<void>;
  loading: boolean;
}) {
  return (
    <form autoComplete="on" onSubmit={onSubmit}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col">
          <label htmlFor="login-email">email address</label>
          <input
            id="login-email"
            name="email"
            type="email"
            autoComplete="username"
            inputMode="email"
            required
            placeholder="you@example.com"
            className="bg-white/5 p-1 rounded-md"
            value={loginForm.email}
            onChange={(event) =>
              setLoginForm((current) => ({
                ...current,
                email: event.target.value,
              }))
            }
          />
        </div>

        <div className="flex flex-col">
          <label htmlFor="login-password">password</label>
          <input
            id="login-password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            placeholder="**********"
            className="bg-white/5 p-1 rounded-md"
            value={loginForm.password}
            onChange={(event) =>
              setLoginForm((current) => ({
                ...current,
                password: event.target.value,
              }))
            }
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center rounded-2xl bg-amber-300 px-4 py-3 font-semibold text-slate-950 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </div>
    </form>
  );
}
