#!/usr/bin/env node
/**
 * X API v2 MCP Server.
 * Exposes X API v2 operations as MCP tools using the OpenAPI spec.
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ListToolsRequestSchema, CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

import { parseSpec, fetchOpenApiSpec } from "./openapi.js";
import { executeRequest, XApiError } from "./x-client.js";
import { loadTokens } from "./auth/store.js";
import { getBearerToken } from "./auth/oauth2.js";
import type { AuthMode, ToolMeta } from "./types.js";

// --- Config ---

const authMode = (process.env["X_AUTH_MODE"] ?? "bearer") as AuthMode;
const allowlistRaw = process.env["X_API_TOOL_ALLOWLIST"];

// --- Auth validation ---

function requireBearerToken(): string {
  try {
    return getBearerToken();
  } catch {
    process.stderr.write("X_BEARER_TOKEN environment variable is required for Bearer Token mode.\n");
    process.exit(1);
  }
}

function requireOAuth2Tokens(): void {
  const tokens = loadTokens();
  if (!tokens) {
    process.stderr.write(
      "No OAuth2 tokens found. Run `node dist/auth-cli.js` to authenticate first.\n",
    );
    process.exit(1);
  }
}

if (authMode === "bearer") {
  requireBearerToken();
} else {
  requireOAuth2Tokens();
}

// --- Fetch spec and build tool map ---

const spec = await fetchOpenApiSpec();
const toolMap = parseSpec(spec);

process.stderr.write(
  `x-api: ${toolMap.size} tools loaded (auth=${authMode})\n`,
);

// --- MCP Server ---

const server = new Server(
  { name: "x-api", version: "1.0.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: Array.from(toolMap.values()).map(({ tool }) => ({
    name: tool.name,
    description: tool.description,
    inputSchema: tool.inputSchema,
  })),
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const entry = toolMap.get(req.params.name);
  if (!entry) {
    return {
      content: [{ type: "text" as const, text: `Unknown tool: ${req.params.name}` }],
      isError: true,
    };
  }

  const { meta } = entry;
  const args = req.params.arguments as Record<string, unknown>;

  // Split args into path/query/body
  const pathParams: Record<string, string | number> = {};
  const queryParams: Record<string, string | number | string[] | undefined> = {};
  const body: Record<string, unknown> = {};

  for (const key of meta.paramLocations.path) {
    if (args[key] !== undefined) pathParams[key] = args[key] as string | number;
  }
  for (const key of meta.paramLocations.query) {
    queryParams[key] = args[key] as string | number | string[] | undefined;
  }
  if (meta.paramLocations.body) {
    // Collect remaining args as body fields
    const consumed = new Set([...meta.paramLocations.path, ...meta.paramLocations.query]);
    for (const [k, v] of Object.entries(args)) {
      if (!consumed.has(k)) body[k] = v;
    }
  }

  try {
    const result = await executeRequest(meta, { pathParams, queryParams, body }, authMode);
    return {
      content: [{ type: "text" as const, text: JSON.stringify(result.data, null, 2) }],
    };
  } catch (err) {
    const xErr = err as XApiError;
    const msg = xErr.message ?? String(err);
    return {
      content: [{ type: "text" as const, text: msg }],
      isError: true,
    };
  }
});

// --- Shutdown ---

function shutdown(): void {
  process.stderr.write("x-api: shutting down\n");
  server.close().catch(() => {});
  process.exit(0);
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

// --- Main ---

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  process.stderr.write(`Fatal: ${err}\n`);
  process.exit(1);
});
