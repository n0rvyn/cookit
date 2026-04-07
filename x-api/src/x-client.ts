/**
 * X API HTTP client — builds URLs, executes requests, normalizes errors.
 */
import type { AuthMode, ToolMeta } from "./types.js";
import { getBearerToken } from "./auth/oauth2.js";
import { getValidAccessToken } from "./auth/oauth2.js";

const X_API_BASE = "https://api.x.com";

// --- URL builder ---

export function buildUrl(
  pathTemplate: string,
  pathParams: Record<string, string | number>,
  queryParams: Record<string, string | number | string[] | undefined>,
): string {
  let path = pathTemplate;

  // Substitute path params
  for (const [key, value] of Object.entries(pathParams)) {
    path = path.replace(`{${key}}`, String(value));
  }

  // Build query string
  const qsParams: string[] = [];
  for (const [key, value] of Object.entries(queryParams)) {
    if (value === undefined) continue;
    if (Array.isArray(value)) {
      qsParams.push(`${encodeURIComponent(key)}=${value.map((v) => encodeURIComponent(v)).join(",")}`);
    } else {
      qsParams.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
    }
  }

  const qs = qsParams.length > 0 ? `?${qsParams.join("&")}` : "";
  return `${X_API_BASE}${path}${qs}`;
}

// --- Request executor ---

export interface RequestArgs {
  pathParams?: Record<string, string | number>;
  queryParams?: Record<string, string | number | string[] | undefined>;
  body?: Record<string, unknown>;
}

export interface RequestResult {
  data: unknown;
  status: number;
}

export async function executeRequest(
  meta: ToolMeta,
  args: RequestArgs,
  authMode: AuthMode,
): Promise<RequestResult> {
  const { pathParams = {}, queryParams = {}, body } = args;

  const url = buildUrl(meta.pathTemplate, pathParams, queryParams);

  const headers = new Headers();
  headers.set("Content-Type", "application/json");
  headers.set("Accept", "application/json");

  if (authMode === "bearer") {
    const token = getBearerToken();
    headers.set("Authorization", `Bearer ${token}`);
  } else {
    const token = await getValidAccessToken();
    headers.set("Authorization", `Bearer ${token}`);
  }

  const init: RequestInit = {
    method: meta.method,
    headers,
  };

  if (body && meta.method !== "GET" && meta.method !== "DELETE") {
    init.body = JSON.stringify(body);
  }

  const resp = await fetch(url, init);
  const status = resp.status;

  let data: unknown;
  try {
    data = await resp.json();
  } catch {
    data = await resp.text();
  }

  // Error normalization
  if (!resp.ok) {
    const retryAfter = status === 429
      ? Math.ceil((Number(resp.headers.get("x-rate-limit-reset")) * 1000 - Date.now()) / 1000)
      : undefined;
    const err = normalizeError(status, data, retryAfter);
    throw err;
  }

  return { data, status };
}

// --- Error normalization ---

export interface XApiError {
  readonly message: string;
  readonly status: number;
  readonly retryAfter?: number;
  readonly name: "XApiError";
}

function normalizeError(status: number, data: unknown, retryAfter?: number): XApiError {
  let message = `X API error: ${status}`;
  if (retryAfter !== undefined && retryAfter > 0) {
    message += ` — retry after ${retryAfter} seconds`;
  } else if (status === 429) {
    message += " (rate limited)";
  }

  if (typeof data === "object" && data !== null) {
    const obj = data as Record<string, unknown>;

    // { errors: [...] } format
    if (Array.isArray(obj.errors) && obj.errors.length > 0) {
      const first = obj.errors[0] as Record<string, unknown>;
      const extracted = first.message ?? first.detail ?? first.title;
      if (extracted) message += ` — ${extracted}`;
    }
    // { detail, type } format (RFC 7807-ish)
    else if (obj.detail || obj.type) {
      message += ` — ${obj.detail ?? obj.type}`;
    }
  }

  if (status === 401) {
    message += " — check your X_BEARER_TOKEN or re-run `node dist/auth-cli.js`";
  }

  const err: XApiError = {
    name: "XApiError",
    message,
    status,
    ...(retryAfter !== undefined ? { retryAfter } : {}),
  };
  return err;
}
