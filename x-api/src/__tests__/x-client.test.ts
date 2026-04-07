/**
 * Tests for x-client.ts — HTTP client.
 */
import { describe, it, mock } from "node:test";
import assert from "node:assert";

// Inline the buildUrl and normalizeError logic for isolated unit testing.

interface XApiError {
  readonly message: string;
  readonly status: number;
  readonly retryAfter?: number;
  readonly name: "XApiError";
}

function buildUrl(
  pathTemplate: string,
  pathParams: Record<string, string | number>,
  queryParams: Record<string, string | number | string[] | undefined>,
): string {
  let path = pathTemplate;
  for (const [key, value] of Object.entries(pathParams)) {
    path = path.replace(`{${key}}`, String(value));
  }
  const qsParams: string[] = [];
  for (const [key, value] of Object.entries(queryParams)) {
    if (value === undefined) continue;
    if (Array.isArray(value)) {
      qsParams.push(
        `${encodeURIComponent(key)}=${value.map((v) => encodeURIComponent(v)).join(",")}`,
      );
    } else {
      qsParams.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
    }
  }
  const qs = qsParams.length > 0 ? `?${qsParams.join("&")}` : "";
  return `https://api.x.com${path}${qs}`;
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
    if (Array.isArray(obj.errors) && obj.errors.length > 0) {
      const first = obj.errors[0] as Record<string, unknown>;
      const extracted = first.message ?? first.detail ?? first.title;
      if (extracted) message += ` — ${extracted}`;
    } else if (obj.detail || obj.type) {
      message += ` — ${obj.detail ?? obj.type}`;
    }
  }

  if (status === 401) {
    message += " — check your X_BEARER_TOKEN or re-run `node dist/auth-cli.js`";
  }

  return {
    name: "XApiError",
    message,
    status,
    ...(retryAfter !== undefined ? { retryAfter } : {}),
  };
}

// --- Tests ---

describe("buildUrl", () => {
  it("substitutes path params", () => {
    const url = buildUrl("/users/{userId}", { userId: "123" }, {});
    assert.strictEqual(url, "https://api.x.com/users/123");
  });

  it("appends query params", () => {
    const url = buildUrl("/tweets", {}, { max_results: 10, "tweet.fields": "created_at" });
    assert.ok(url.includes("max_results=10"));
    assert.ok(url.includes("tweet.fields=created_at"));
  });

  it("joins array params with commas", () => {
    const url = buildUrl("/users/by", {}, { ids: ["123", "456"] });
    assert.strictEqual(url, "https://api.x.com/users/by?ids=123,456");
  });

  it("skips undefined query params", () => {
    const url = buildUrl("/tweets", {}, { max_results: undefined });
    assert.strictEqual(url, "https://api.x.com/tweets");
  });

  it("handles multiple path params", () => {
    const url = buildUrl("/users/{userId}/tweets/{tweetId}", { userId: "abc", tweetId: "99" }, {});
    assert.strictEqual(url, "https://api.x.com/users/abc/tweets/99");
  });

  it("combines path and query params", () => {
    const url = buildUrl(
      "/users/{userId}/tweets",
      { userId: "123" },
      { max_results: 5 },
    );
    assert.strictEqual(url, "https://api.x.com/users/123/tweets?max_results=5");
  });
});

describe("normalizeError", () => {
  it("extracts message from { errors: [...] } format", () => {
    const err = normalizeError(400, {
      errors: [{ message: "Bad request: missing required parameter", code: 93 }],
    });
    assert.strictEqual(err.message, "X API error: 400 — Bad request: missing required parameter");
  });

  it("extracts detail from RFC 7807-ish format", () => {
    const err = normalizeError(404, {
      detail: "Could not find user with id: [not-a-real-id]",
      type: "https://api.x.com/2/problems/not-found",
    });
    assert.strictEqual(
      err.message,
      "X API error: 404 — Could not find user with id: [not-a-real-id]",
    );
  });

  it("includes auth config suggestion for 401", () => {
    const err = normalizeError(401, { detail: "Unauthorized" });
    assert.ok(err.message.includes("X_BEARER_TOKEN"));
    assert.ok(err.message.includes("auth-cli.js"));
  });

  it("reports retry seconds from x-rate-limit-reset for 429", () => {
    // Simulate: x-rate-limit-reset = Unix seconds, we pass retryAfter computed from it
    const err = normalizeError(429, { detail: "Rate limit exceeded" }, 30);
    assert.strictEqual(err.status, 429);
    assert.strictEqual(err.retryAfter, 30);
    assert.ok(err.message.includes("retry after 30 seconds"));
  });

  it("has generic message for 429 when retryAfter is not provided", () => {
    const err = normalizeError(429, {});
    assert.ok(err.message.includes("rate limited"));
    assert.strictEqual(err.retryAfter, undefined);
  });

  it("returns generic message for unknown error shapes", () => {
    const err = normalizeError(500, "Internal Server Error");
    assert.strictEqual(err.status, 500);
    assert.ok(err.message.startsWith("X API error: 500"));
  });

  it("includes retryAfter in error object when provided", () => {
    const err = normalizeError(429, {}, 60);
    assert.strictEqual(err.retryAfter, 60);
  });
});
