import {useState} from "react";
import type * as React from "react";
import {useNavigate} from "react-router-dom";

import {
    ApiError,
    isTokenResponse,
    loadTokens,
    loginUser,
    registerUser,
    saveTokens,
} from "../services/auth";
import type {UserCreate, UserLogin} from "../types";

import {AuthLeft} from "../components/auth/AuthLeft";
import {AuthPanel} from "../components/auth/AuthPanel";
import {AuthTabs} from "../components/auth/AuthTabs";
import {AuthAlerts} from "../components/auth/AuthAlerts";
import {LoginForm} from "../components/auth/LoginForm";
import {RegisterForm} from "../components/auth/RegisterForm";

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

export function LoginPage() {
    const navigate = useNavigate();
    const [mode, setMode] = useState<AuthMode>("login");
    const [loginForm, setLoginForm] = useState<UserLogin>(initialLoginForm);
    const [registerForm, setRegisterForm] = useState<UserCreate>(
        initialRegisterForm,
    );
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(() =>
        loadTokens()
            ? "You already have a saved session. Sign in again to refresh it."
            : null,
    );
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
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
        } catch (caughtError) {
            setError(
                caughtError instanceof ApiError
                    ? caughtError.message
                    : "Unable to log in right now. Please try again.",
            );
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setMessage(null);

        try {
            const response = await registerUser(registerForm);
            setMessage(`Account created for ${response.email}. You can now log in.`);
            setMode("login");
            setLoginForm({email: registerForm.email, password: ""});
            setRegisterForm(initialRegisterForm);
        } catch (caughtError) {
            setError(
                caughtError instanceof ApiError
                    ? caughtError.message
                    : "Unable to create your account right now. Please try again.",
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-[#071827] text-slate-100">
            <div className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
                <AuthLeft/>

                <AuthPanel>
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <h2 className="sr-only">Authentication panel</h2>
                        </div>
                        <AuthTabs mode={mode} setMode={setMode}/>
                    </div>

                    <AuthAlerts message={message} error={error}/>

                    {mode === "login" ? (
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

                    <p className="mt-6 text-sm leading-6 text-slate-400">
                        Need to switch menus? Use the tabs above to move between login and
                        account creation at any time.
                    </p>
                </AuthPanel>
            </div>
        </main>
    );
}
