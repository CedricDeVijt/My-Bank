import type {
  TokenResponse,
  UserCreate,
  UserLogin,
  UserResponse,
} from "../types";

import { ApiError, requestJson, generateIdempotencyKey } from "./http";

const AUTH_CHANGED_EVENT = "my-bank:auth-changed";

// Store idempotency keys for in-flight requests
let loginIdempotencyKey: string | null = null;
let registerIdempotencyKey: string | null = null;
let refreshTokenIdempotencyKey: string | null = null;

export async function loginUser(payload: UserLogin) {
  // Reuse existing key if request is in flight, otherwise generate new one
  if (!loginIdempotencyKey) {
    loginIdempotencyKey = generateIdempotencyKey();
  }

  try {
    return await requestJson<TokenResponse | Record<string, unknown>>(
      "/api/v1/auth/login",
      {
        method: "POST",
        jsonBody: payload,
        idempotencyKey: loginIdempotencyKey,
      },
    );
  } finally {
    // Clear the key after request completes
    loginIdempotencyKey = null;
  }
}

export async function registerUser(payload: UserCreate) {
  // Reuse existing key if request is in flight, otherwise generate new one
  if (!registerIdempotencyKey) {
    registerIdempotencyKey = generateIdempotencyKey();
  }

  try {
    return await requestJson<UserResponse>("/api/v1/auth/register", {
      method: "POST",
      jsonBody: payload,
      idempotencyKey: registerIdempotencyKey,
    });
  } finally {
    // Clear the key after request completes
    registerIdempotencyKey = null;
  }
}

export async function getCurrentUser() {
  // Ensure tokens are valid / refreshed before making the request
  const refreshed = await validateOrRefreshTokens();
  if (!refreshed) {
    throw new ApiError("No active session found.", 401);
  }

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
      // Reuse existing key if request is in flight, otherwise generate new one
      if (!refreshTokenIdempotencyKey) {
        refreshTokenIdempotencyKey = generateIdempotencyKey();
      }

      const newTokens = await requestJson<TokenResponse>(
        "/api/v1/auth/token/refresh",
        {
          method: "POST",
          jsonBody: { refresh_token: tokens.refresh_token },
          idempotencyKey: refreshTokenIdempotencyKey,
        },
      );
      saveTokens(newTokens);
      return newTokens;
    } catch {
      // Refresh failed, tokens are invalid
      clearTokens();
      return null;
    } finally {
      // Clear the key after request completes
      refreshTokenIdempotencyKey = null;
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
