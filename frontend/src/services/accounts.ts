import { requestJson, ApiError, generateIdempotencyKey } from "./http";
import type { Account, AccountCreate } from "../types";
import { loadTokens } from "./auth";

type AccountListResponse = {
  accounts: Account[];
};

// Store idempotency keys for in-flight requests
let createAccountIdempotencyKey: string | null = null;

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

  // Reuse existing key if request is in flight, otherwise generate new one
  if (!createAccountIdempotencyKey) {
    createAccountIdempotencyKey = generateIdempotencyKey();
  }

  try {
    return await requestJson<Account>("/api/v1/accounts", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tokens.access_token}`,
      },
      jsonBody: payload,
      idempotencyKey: createAccountIdempotencyKey,
    });
  } finally {
    // Clear the key after request completes
    createAccountIdempotencyKey = null;
  }
}
