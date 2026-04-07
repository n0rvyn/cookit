#!/usr/bin/env node

// src/auth-cli.ts
import http from "node:http";

// src/auth/oauth2.ts
import crypto from "node:crypto";

// src/auth/store.ts
import fs from "node:fs";
import path from "node:path";
import { homedir } from "node:os";
var TOKEN_DIR = path.join(homedir(), ".x-mcp");
function tokenPath() {
  return path.join(TOKEN_DIR, "tokens.json");
}
function saveTokens(tokens) {
  fs.mkdirSync(TOKEN_DIR, { recursive: true });
  fs.writeFileSync(tokenPath(), JSON.stringify(tokens, null, 2), "utf-8");
}

// src/auth/oauth2.ts
var TOKEN_ENDPOINT = "https://api.x.com/2/oauth2/token";
function generateCodeVerifier() {
  return crypto.randomBytes(64).toString("base64url");
}
function generateCodeChallenge(verifier) {
  return crypto.createHash("sha256").update(verifier).digest("base64url");
}
function getClientId() {
  const id = process.env["X_CLIENT_ID"];
  if (!id) {
    process.stderr.write("X_CLIENT_ID environment variable is required for OAuth2 mode.\n");
    process.exit(1);
  }
  return id;
}
async function exchangeCode(code, codeVerifier, redirectUri) {
  const clientId = getClientId();
  const resp = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      code_verifier: codeVerifier,
      client_id: clientId,
      redirect_uri: redirectUri
    })
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token exchange failed: ${resp.status} ${body}`);
  }
  const json = await resp.json();
  const tokens = {
    access_token: json.access_token,
    refresh_token: json.refresh_token,
    expires_at: Date.now() + json.expires_in * 1e3,
    scope: json.scope
  };
  saveTokens(tokens);
  return tokens;
}
var REFRESH_WINDOW_MS = 5 * 60 * 1e3;

// src/auth-cli.ts
import { homedir as homedir2 } from "node:os";
import path2 from "node:path";
import { parse as parseUrl } from "node:url";
var CALLBACK_PORT = 8739;
var CALLBACK_PATH = "/callback";
var TIMEOUT_MS = 5 * 60 * 1e3;
var REDIRECT_URI = `http://localhost:${CALLBACK_PORT}${CALLBACK_PATH}`;
var SCOPES = [
  "tweet.read",
  "tweet.write",
  "users.read",
  "offline.access",
  "dm.read",
  "dm.write",
  "list.read",
  "list.write",
  "bookmark.read",
  "bookmark.write",
  "like.read",
  "like.write",
  "follows.read",
  "follows.write",
  "space.read",
  "mute.read",
  "mute.write",
  "block.read",
  "block.write"
].join(" ");
function requireClientId() {
  const id = process.env["X_CLIENT_ID"];
  if (!id) {
    console.error("X_CLIENT_ID environment variable is required.");
    process.exit(1);
  }
  return id;
}
async function waitForCallback(timeoutMs) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const parsed = parseUrl(req.url ?? "", true);
      if (parsed.pathname !== CALLBACK_PATH) {
        res.writeHead(404);
        res.end("Not found");
        return;
      }
      const code = parsed.query.code;
      const error = parsed.query.error;
      clearTimeout(timer);
      server.close();
      if (error) {
        reject(new Error(`OAuth error: ${error}`));
        return;
      }
      if (!code) {
        reject(new Error("No authorization code received."));
        return;
      }
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(`
        <html>
          <body style="font-family: sans-serif; text-align: center; padding: 2rem;">
            <h2>Authorization successful!</h2>
            <p>You can close this window and return to the terminal.</p>
          </body>
        </html>
      `);
      resolve(code);
    });
    server.listen(CALLBACK_PORT, () => {
    });
    const timer = setTimeout(() => {
      server.close();
      reject(new Error("Timeout waiting for OAuth callback (5 minutes)."));
    }, timeoutMs);
  });
}
async function main() {
  const clientId = requireClientId();
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  const state = Math.random().toString(36).slice(2);
  const authParams = new URLSearchParams({
    response_type: "code",
    client_id: clientId,
    redirect_uri: REDIRECT_URI,
    scope: SCOPES,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
    state
  });
  const authUrl = `https://twitter.com/i/oauth2/authorize?${authParams.toString()}`;
  console.log("X API OAuth2 Authorization\n");
  console.log("1. Open this URL in your browser:\n");
  console.log(`   ${authUrl}
`);
  console.log("2. Authorize the application.");
  console.log("3. You will be redirected back here automatically.\n");
  try {
    const { execFile } = await import("node:child_process");
    execFile("open", [authUrl], () => {
    });
  } catch {
  }
  console.log("Waiting for callback...\n");
  const code = await waitForCallback(TIMEOUT_MS).catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  });
  console.log("Exchanging authorization code for tokens...\n");
  try {
    const tokens = await exchangeCode(code, codeVerifier, REDIRECT_URI);
    saveTokens(tokens);
    const tokenFile = path2.join(homedir2(), ".x-mcp", "tokens.json");
    console.log(`Success! Tokens saved to: ${tokenFile}`);
    console.log(`
You can now start the MCP server with: node dist/server.js`);
    console.log("Set X_AUTH_MODE=oauth2 in your environment to use OAuth2 authentication.\n");
  } catch (err) {
    console.error(`Token exchange failed: ${err}`);
    process.exit(1);
  }
}
main().catch((err) => {
  console.error(`Fatal: ${err}`);
  process.exit(1);
});
//# sourceMappingURL=auth-cli.js.map
