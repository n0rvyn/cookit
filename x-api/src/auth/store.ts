/**
 * Token persistence for X API OAuth2.
 * Stores/loads tokens to ~/.x-mcp/tokens.json.
 */
import fs from "node:fs";
import path from "node:path";
import { homedir } from "node:os";
import type { OAuth2Tokens } from "../types.js";

const TOKEN_DIR = path.join(homedir(), ".x-mcp");

function tokenPath(): string {
  return path.join(TOKEN_DIR, "tokens.json");
}

export function loadTokens(): OAuth2Tokens | null {
  try {
    const raw = fs.readFileSync(tokenPath(), "utf-8");
    return JSON.parse(raw) as OAuth2Tokens;
  } catch {
    return null;
  }
}

export function saveTokens(tokens: OAuth2Tokens): void {
  fs.mkdirSync(TOKEN_DIR, { recursive: true });
  fs.writeFileSync(tokenPath(), JSON.stringify(tokens, null, 2), "utf-8");
}
