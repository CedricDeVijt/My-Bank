import { requestJson, ApiError, generateIdempotencyKey } from "./http";
import { loadTokens } from "./auth";

export interface TransactionCreatePayload {
  from_account_id: string;
  to_account_id: string;
  amount_cents: number;
}

export interface TransactionResponse {
  id: string;
  from_account_id: string;
  to_account_id: string;
  amount_cents: number;
  currency: string;
  status: string;
  failure_reason?: string | null;
  created_at: string;
  updated_at: string;
}

let createTransactionIdempotencyKey: string | null = null;

export async function createTransaction(payload: TransactionCreatePayload) {
  const tokens = loadTokens();

  if (!tokens?.access_token) {
    throw new ApiError("No active session found.", 401);
  }

  if (!createTransactionIdempotencyKey) {
    createTransactionIdempotencyKey = generateIdempotencyKey();
  }

  try {
    return await requestJson<TransactionResponse>("/api/v1/transactions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tokens.access_token}`,
      },
      jsonBody: payload,
      idempotencyKey: createTransactionIdempotencyKey,
    });
  } finally {
    createTransactionIdempotencyKey = null;
  }
}

export async function listTransactions(
  account_id?: string,
  skip = 0,
  limit = 50,
) {
  const tokens = loadTokens();

  if (!tokens?.access_token) {
    throw new ApiError("No active session found.", 401);
  }

  const params = new URLSearchParams();
  if (account_id) params.set("account_id", account_id);
  if (skip) params.set("skip", String(skip));
  if (limit) params.set("limit", String(limit));

  const path = `/api/v1/transactions${params.toString() ? `?${params.toString()}` : ""}`;

  return await requestJson<TransactionResponse[]>(path, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${tokens.access_token}`,
    },
  });
}
