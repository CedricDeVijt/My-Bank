import { config } from "../config";

const API_BASE_URL = config.API_BASE_URL;
const pendingRequests = new Map<string, Promise<unknown>>();

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function performRequest<T>(
  path: string,
  init: RequestInit & { jsonBody?: unknown; idempotencyKey?: string } = {},
) {
  const { jsonBody, idempotencyKey, headers, ...requestInit } = init;
  const requestHeaders = new Headers(headers ?? {});

  if (idempotencyKey) {
    requestHeaders.set("Idempotency-Key", idempotencyKey);
  }

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

export async function requestJson<T>(
  path: string,
  init: RequestInit & { jsonBody?: unknown; idempotencyKey?: string } = {},
) {
  const { jsonBody, idempotencyKey, headers, ...requestInit } = init;
  const method = requestInit.method || "GET";

  // Create a request signature for deduplication
  const requestSignature = `${method}:${path}:${idempotencyKey}`;

  // If this exact request is already in flight, return the same promise
  if (pendingRequests.has(requestSignature)) {
    return pendingRequests.get(requestSignature) as Promise<T>;
  }

  // Create and store the promise
  const promise = performRequest<T>(path, {
    ...requestInit,
    jsonBody,
    idempotencyKey,
    headers,
  });

  pendingRequests.set(requestSignature, promise);

  // Clean up after request completes (success or failure)
  promise.finally(() => pendingRequests.delete(requestSignature));

  return promise;
}

export function generateIdempotencyKey(): string {
  return crypto.randomUUID();
}
