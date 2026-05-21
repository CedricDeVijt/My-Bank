import { config } from "../config";
import type { Account, AccountCreate } from "../types";
import { ApiError, loadTokens } from "./auth";

const API_BASE_URL = config.API_BASE_URL;

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

type AccountListResponse = {
  accounts: Account[];
};

export async function listAccounts() {
  const tokens = loadTokens();

  if (!tokens?.access_token) {
    throw new ApiError("No active session found.", 401);
  }

  const response = await requestJson<AccountListResponse>("/api/v1/accounts", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${tokens.access_token}`,
    },
  });

  return response.accounts;
}

export async function createAccount(payload: AccountCreate) {
  const tokens = loadTokens();

  if (!tokens?.access_token) {
    throw new ApiError("No active session found.", 401);
  }

  return requestJson<Account>("/api/v1/accounts", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${tokens.access_token}`,
    },
    jsonBody: payload,
  });
}
