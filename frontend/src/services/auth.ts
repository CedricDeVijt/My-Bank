import type {
  TokenResponse,
  UserCreate,
  UserLogin,
  UserResponse,
} from "../types";

import { config } from "../config";

const API_BASE_URL = config.API_BASE_URL;
const AUTH_CHANGED_EVENT = "my-bank:auth-changed";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function requestJson<T>(
  path: string,
  init: RequestInit & { jsonBody?: unknown } = {},
) {
  const { jsonBody, headers, ...requestInit } = init;
  const requestHeaders = new Headers(headers ?? {});

  if (jsonBody !== undefined && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestInit,
    headers: requestHeaders,
    body: jsonBody === undefined ? undefined : JSON.stringify(jsonBody),
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
    {
      method: "POST",
      jsonBody: payload,
    },
  );
}

export function registerUser(payload: UserCreate) {
  return requestJson<UserResponse>("/api/v1/auth/register", {
    method: "POST",
    jsonBody: payload,
  });
}

export async function getCurrentUser() {
  const tokens = loadTokens();

  if (!tokens?.access_token) {
    throw new ApiError("No active session found.", 401);
  }

  return requestJson<UserResponse>("/api/v1/users/me", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${tokens.access_token}`,
    },
  });
}

export function isTokenResponse(value: unknown): value is TokenResponse {
  return (
    typeof value === "object" &&
    value !== null &&
    "access_token" in value &&
    "refresh_token" in value
  );
}

export function isTokenExpired(expiresIn: number, savedAt: number): boolean {
  const now = Date.now();
  const expirationTime = savedAt + expiresIn * 1000; // convert seconds to ms
  return now >= expirationTime;
}

export async function validateOrRefreshTokens(): Promise<TokenResponse | null> {
  const tokens = loadTokens();

  if (!tokens) {
    return null;
  }

  // If no saved_at timestamp, tokens are from an old format - clear them
  if (!tokens.saved_at) {
    clearTokens();
    return null;
  }

  // Check if access token is still valid
  if (!isTokenExpired(tokens.access_token_expires_in, tokens.saved_at)) {
    return tokens; // Access token is still valid
  }

  // Access token expired, try to refresh
  if (!isTokenExpired(tokens.refresh_token_expires_in, tokens.saved_at)) {
    try {
      const newTokens = await requestJson<TokenResponse>(
        "/api/v1/auth/refresh",
        {
          method: "POST",
          jsonBody: { refresh_token: tokens.refresh_token },
        },
      );
      saveTokens(newTokens);
      return newTokens;
    } catch {
      // Refresh failed, tokens are invalid
      clearTokens();
      return null;
    }
  }

  // Both tokens expired
  clearTokens();
  return null;
}

export function saveTokens(tokens: TokenResponse) {
  const tokensWithTimestamp = {
    ...tokens,
    saved_at: Date.now(),
  };
  localStorage.setItem("my-bank.tokens", JSON.stringify(tokensWithTimestamp));
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function clearTokens() {
  localStorage.removeItem("my-bank.tokens");
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
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

export { ApiError };
export { AUTH_CHANGED_EVENT };
