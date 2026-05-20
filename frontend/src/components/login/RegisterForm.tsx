import type { FormEvent, Dispatch, SetStateAction } from "react";
import type { UserCreate } from "../../types";

export function RegisterForm({
  registerForm,
  setRegisterForm,
  onSubmit,
  loading,
}: {
  registerForm: UserCreate;
  setRegisterForm: Dispatch<SetStateAction<UserCreate>>;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void | Promise<void>;
  loading: boolean;
}) {
  return (
    <form autoComplete="on" onSubmit={onSubmit}>
      <div className="flex flex-col gap-4">
        <label htmlFor="register-first-name">first name</label>
        <input
          id="register-first-name"
          name="first_name"
          type="text"
          autoComplete="given-name"
          required
          placeholder="John"
          className="bg-white/5 p-1 rounded-md"
          value={registerForm.first_name}
          onChange={(event) =>
            setRegisterForm((current) => ({
              ...current,
              first_name: event.target.value,
            }))
          }
        />

        <label htmlFor="register-last-name">last name</label>
        <input
          id="register-last-name"
          name="last_name"
          type="text"
          autoComplete="family-name"
          required
          placeholder="Doe"
          className="bg-white/5 p-1 rounded-md mt-1"
          value={registerForm.last_name}
          onChange={(event) =>
            setRegisterForm((current) => ({
              ...current,
              last_name: event.target.value,
            }))
          }
        />

        <label htmlFor="register-dob">date of birth</label>
        <input
          id="register-dob"
          name="date_of_birth"
          type="date"
          autoComplete="bday"
          required
          className="bg-white/5 p-1 rounded-md mt-1"
          value={registerForm.date_of_birth}
          onChange={(event) =>
            setRegisterForm((current) => ({
              ...current,
              date_of_birth: event.target.value,
            }))
          }
        />

        <label htmlFor="register-email">email address</label>
        <input
          id="register-email"
          name="email"
          type="email"
          autoComplete="username"
          inputMode="email"
          required
          placeholder="you@example.com"
          className="bg-white/5 p-1 rounded-md"
          value={registerForm.email}
          onChange={(event) =>
            setRegisterForm((current) => ({
              ...current,
              email: event.target.value,
            }))
          }
        />

        <label htmlFor="register-password">password</label>
        <input
          id="register-password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          placeholder="**********"
          className="bg-white/5 p-1 rounded-md"
          value={registerForm.password}
          onChange={(event) =>
            setRegisterForm((current) => ({
              ...current,
              password: event.target.value,
            }))
          }
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-amber-300 text-slate-950 font-semibold py-2 rounded-md hover:bg-amber-200 transition"
        >
          {loading ? "Creating account..." : "Register"}
        </button>
      </div>
    </form>
  );
}
