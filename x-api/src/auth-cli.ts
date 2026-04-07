#!/usr/bin/env node
/**
 * X API OAuth2 PKCE Authorization CLI.
 * Usage: node dist/auth-cli.js
 */
import http from "node:http";
import { generateCodeVerifier, generateCodeChallenge, exchangeCode } from "./auth/oauth2.js";
import { saveTokens } from "./auth/store.js";
import { homedir } from "node:os";
import path from "node:path";
import { parse as parseUrl } from "node:url";

const CALLBACK_PORT = 8739;
const CALLBACK_PATH = "/callback";
const TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes
const REDIRECT_URI = `http://localhost:${CALLBACK_PORT}${CALLBACK_PATH}`;

// Scopes requested
const SCOPES = [
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
  "block.write",
].join(" ");

function requireClientId(): string {
  const id = process.env["X_CLIENT_ID"];
  if (!id) {
    console.error("X_CLIENT_ID environment variable is required.");
    process.exit(1);
  }
  return id;
}

async function waitForCallback(timeoutMs: number): Promise<string> {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const parsed = parseUrl(req.url ?? "", true);
      if (parsed.pathname !== CALLBACK_PATH) {
        res.writeHead(404);
        res.end("Not found");
        return;
      }

      const code = parsed.query.code as string | undefined;
      const error = parsed.query.error as string | undefined;

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
      // ready
    });

    const timer = setTimeout(() => {
      server.close();
      reject(new Error("Timeout waiting for OAuth callback (5 minutes)."));
    }, timeoutMs);
  });
}

async function main(): Promise<void> {
  const clientId = requireClientId();

  // Generate PKCE params
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  const state = Math.random().toString(36).slice(2);

  // Build authorization URL
  const authParams = new URLSearchParams({
    response_type: "code",
    client_id: clientId,
    redirect_uri: REDIRECT_URI,
    scope: SCOPES,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
    state,
  });

  const authUrl = `https://twitter.com/i/oauth2/authorize?${authParams.toString()}`;

  console.log("X API OAuth2 Authorization\n");
  console.log("1. Open this URL in your browser:\n");
  console.log(`   ${authUrl}\n`);
  console.log("2. Authorize the application.");
  console.log("3. You will be redirected back here automatically.\n");

  // Attempt to open browser (best-effort)
  try {
    const { execFile } = await import("node:child_process");
    execFile("open", [authUrl], () => {});
  } catch {
    // Browser open not available on this platform
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

    const tokenFile = path.join(homedir(), ".x-mcp", "tokens.json");
    console.log(`Success! Tokens saved to: ${tokenFile}`);
    console.log(`\nYou can now start the MCP server with: node dist/server.js`);
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
