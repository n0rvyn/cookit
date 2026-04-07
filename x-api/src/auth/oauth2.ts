/**
 * OAuth2 PKCE authentication for X API.
 */
import crypto from "node:crypto";
import { loadTokens, saveTokens } from "./store.js";
import type { OAuth2Tokens } from "../types.js";

const TOKEN_ENDPOINT = "https://api.x.com/2/oauth2/token";

// --- PKCE helpers ---

export function generateCodeVerifier(): string {
  return crypto.randomBytes(64).toString("base64url");
}

export function generateCodeChallenge(verifier: string): string {
  return crypto.createHash("sha256").update(verifier).digest("base64url");
}

// --- Token management ---

function getClientId(): string {
  const id = process.env["X_CLIENT_ID"];
  if (!id) {
    process.stderr.write("X_CLIENT_ID environment variable is required for OAuth2 mode.\n");
    process.exit(1);
  }
  return id;
}

export function getBearerToken(): string {
  const token = process.env["X_BEARER_TOKEN"];
  if (!token) {
    process.stderr.write(
      "X_BEARER_TOKEN environment variable is required for Bearer Token mode.\n",
    );
    process.exit(1);
  }
  return token;
}

export async function refreshAccessToken(refreshToken: string): Promise<OAuth2Tokens> {
  const clientId = getClientId();
  const resp = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: refreshToken,
      client_id: clientId,
    }),
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token refresh failed: ${resp.status} ${body}`);
  }

  const json = await resp.json() as {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    scope: string;
  };

  const tokens: OAuth2Tokens = {
    access_token: json.access_token,
    refresh_token: json.refresh_token ?? refreshToken,
    expires_at: Date.now() + json.expires_in * 1000,
    scope: json.scope,
  };
  saveTokens(tokens);
  return tokens;
}

export async function exchangeCode(
  code: string,
  codeVerifier: string,
  redirectUri: string,
): Promise<OAuth2Tokens> {
  const clientId = getClientId();
  const resp = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      code_verifier: codeVerifier,
      client_id: clientId,
      redirect_uri: redirectUri,
    }),
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token exchange failed: ${resp.status} ${body}`);
  }

  const json = await resp.json() as {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    scope: string;
  };

  const tokens: OAuth2Tokens = {
    access_token: json.access_token,
    refresh_token: json.refresh_token,
    expires_at: Date.now() + json.expires_in * 1000,
    scope: json.scope,
  };
  saveTokens(tokens);
  return tokens;
}

const REFRESH_WINDOW_MS = 5 * 60 * 1000; // 5 minutes before expiry

export async function getValidAccessToken(): Promise<string> {
  const tokens = loadTokens();
  if (!tokens) {
    process.stderr.write(
      "No tokens found. Run `node dist/auth-cli.js` to authenticate first.\n",
    );
    process.exit(1);
  }

  // Auto-refresh if within 5 minutes of expiry
  if (Date.now() >= tokens.expires_at - REFRESH_WINDOW_MS) {
    const refreshed = await refreshAccessToken(tokens.refresh_token);
    return refreshed.access_token;
  }

  return tokens.access_token;
}

export function applyOAuth2Auth(headers: Headers, accessToken: string): void {
  headers.set("Authorization", `Bearer ${accessToken}`);
}
