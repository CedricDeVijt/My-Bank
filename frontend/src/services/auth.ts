import type {
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
} from "../types";

import {config} from "../config";

const API_BASE_URL = config.API_BASE_URL;

class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

async function requestJson<T>(path: string, body: unknown, init?: RequestInit) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(init?.headers ?? {}),
        },
        body: JSON.stringify(body),
        ...init,
    });

    if (!response.ok) {
        const fallbackMessage = `${response.status} ${response.statusText}`;
        const errorText = await response.text();

        if (!errorText) {
            throw new ApiError(fallbackMessage, response.status);
        }

        let errorMessage = errorText.trim();
        try {
            const errorPayload = JSON.parse(errorText) as {
                detail?: Array<{ msg?: string }> | string;
            };
            if (typeof errorPayload.detail === "string") {
                errorMessage = errorPayload.detail;
            } else {
                const firstMessage = errorPayload.detail?.[0]?.msg;
                if (firstMessage) {
                    errorMessage = firstMessage;
                }
            }
        } catch {
            // Keep the raw text if the body is not JSON.
        }

        throw new ApiError(errorMessage || fallbackMessage, response.status);
    }

    if (response.status === 204) {
        return undefined as T;
    }

    const responseText = await response.text();
    if (!responseText) {
        return undefined as T;
    }

    return JSON.parse(responseText) as T;
}

export function loginUser(payload: UserLogin) {
    return requestJson<TokenResponse | Record<string, unknown>>(
        "/api/v1/auth/login",
        payload,
    );
}

export function registerUser(payload: UserCreate) {
    return requestJson<UserResponse>("/api/v1/auth/register", payload);
}

export function isTokenResponse(value: unknown): value is TokenResponse {
    return (
        typeof value === "object" &&
        value !== null &&
        "access_token" in value &&
        "refresh_token" in value
    );
}

export function saveTokens(tokens: TokenResponse) {
    localStorage.setItem("my-bank.tokens", JSON.stringify(tokens));
}

export function loadTokens() {
    const raw = localStorage.getItem("my-bank.tokens");
    if (!raw) {
        return null;
    }

    try {
        return JSON.parse(raw) as TokenResponse;
    } catch {
        return null;
    }
}

export {ApiError};




