import type {FormEvent} from "react";
import {useNavigate} from "react-router-dom";
import {useState} from "react";

import {ApiError, isTokenResponse, loadTokens, loginUser, registerUser, saveTokens} from "../../services/auth";
import type {UserCreate, UserLogin} from "../../types";
import {AuthTab} from "./AuthTab";
import {LoginForm} from "./LoginForm";
import {RegisterForm} from "./RegisterForm";

type AuthMode = "login" | "register";

const initialLoginForm: UserLogin = {
    email: "",
    password: "",
};

const initialRegisterForm: UserCreate = {
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
};

export function AuthPanel() {
    const navigate = useNavigate();
    const [authMode, setAuthMode] = useState<AuthMode>("login");
    const [loginForm, setLoginForm] = useState<UserLogin>(initialLoginForm);
    const [registerForm, setRegisterForm] = useState<UserCreate>(initialRegisterForm);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(() =>
        loadTokens()
            ? "You already have a saved session. Sign in again to refresh it."
            : null,
    );
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setMessage(null);

        try {
            const response = await loginUser(loginForm);

            if (isTokenResponse(response)) {
                saveTokens(response);
            }

            setMessage("Login successful. Redirecting to your dashboard...");
            navigate("/home");
        } catch (caughtError: unknown) {
            const errorMessage =
                caughtError instanceof ApiError
                    ? caughtError.message
                    : "Unable to log in right now. Please try again.";

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setMessage(null);

        try {
            const response = await registerUser(registerForm);
            setMessage(`Account created for ${response.email}. You can now log in.`);
            setAuthMode("login");
            setLoginForm({email: registerForm.email, password: ""});
            setRegisterForm(initialRegisterForm);
        } catch (caughtError: unknown) {
            const errorMessage =
                caughtError instanceof ApiError
                    ? caughtError.message
                    : "Unable to create your account right now. Please try again.";

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="w-full max-w-md rounded-3xl border border-white/10 bg-slate-950/70 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur">
            <div className="mb-6 space-y-2 text-center">
                <h1 className="text-3xl font-semibold text-white">
                    {authMode === "login" ? "Welcome back" : "Create your account"}
                </h1>
                <p className="text-sm leading-6 text-slate-400">
                    {authMode === "login"
                        ? "Sign in to access your dashboard and manage your finances."
                        : "Set up your profile to start tracking accounts and transactions."}
                </p>
            </div>

            <div className="mb-6 flex justify-center">
                <AuthTab mode={authMode} setMode={setAuthMode} />
            </div>

            <div className="mb-4 space-y-3">
                {message ? (
                    <p className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
                        {message}
                    </p>
                ) : null}
                {error ? (
                    <p className="rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
                        {error}
                    </p>
                ) : null}
            </div>

            {authMode === "login" ? (
                <LoginForm
                    loginForm={loginForm}
                    setLoginForm={setLoginForm}
                    onSubmit={handleLogin}
                    loading={loading}
                />
            ) : (
                <RegisterForm
                    registerForm={registerForm}
                    setRegisterForm={setRegisterForm}
                    onSubmit={handleRegister}
                    loading={loading}
                />
            )}
        </section>
    );
}