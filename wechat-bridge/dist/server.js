#!/usr/bin/env node
/**
 * WeChat Bridge MCP Channel Server.
 * Bridges WeChat messages to Claude Code sessions via --channels protocol.
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ListToolsRequestSchema, CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { createProtocol } from "./protocol.js";
import { loadConfig, loadSyncBuf, saveSyncBuf, DEFAULT_CHANNEL_ID, DEFAULT_PERMISSION_TIMEOUT_MS } from "./config.js";
import { getUpdates, sendMessage as apiSendMessage } from "./api.js";
import { MessageType, MessageState, MessageItemType } from "./types.js";
import { sendPermissionRequest, parsePermissionReply, sweepTimeouts, } from "./permission.js";
// --- Config ---
const channelId = process.env.WECHAT_CHANNEL_ID || DEFAULT_CHANNEL_ID;
const permissionTimeoutMs = Number(process.env.WECHAT_PERMISSION_TIMEOUT_MS) || DEFAULT_PERMISSION_TIMEOUT_MS;
// Startup validation
function requireConfig() {
    const cfg = loadConfig(channelId);
    if (!cfg) {
        process.stderr.write(`No WeChat session found for channel "${channelId}". Run 'wechat-bridge login' first.\n`);
        process.exit(1);
    }
    return cfg;
}
const config = requireConfig();
// --- MCP Server ---
const server = new Server({ name: "wechat-bridge", version: "1.0.0" }, {
    capabilities: {
        tools: {},
        experimental: {
            "claude/channel": {},
            "claude/channel/permission": {},
        },
    },
    instructions: 'WeChat messages arrive as <channel source="wechat-bridge" ...>. ' +
        "Use the reply tool to send messages back to the WeChat user.",
});
const protocol = createProtocol(server);
// --- Permission request handler ---
protocol.onPermissionRequest(async (params) => {
    await sendPermissionRequest({
        requestId: params.request_id,
        toolName: params.tool_name,
        description: params.description,
        inputPreview: params.input_preview,
    }, config, permissionTimeoutMs);
});
// --- Reply tool ---
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        {
            name: "reply",
            description: "Send a message back to the WeChat user",
            inputSchema: {
                type: "object",
                properties: {
                    text: { type: "string", description: "The message to send" },
                },
                required: ["text"],
            },
        },
    ],
}));
server.setRequestHandler(CallToolRequestSchema, async (req) => {
    if (req.params.name === "reply") {
        const { text } = req.params.arguments;
        await sendReply(text, config);
        return { content: [{ type: "text", text: "sent" }] };
    }
    throw new Error(`Unknown tool: ${req.params.name}`);
});
// --- WeChat message polling ---
async function startPolling(cfg, signal) {
    let getUpdatesBuf = loadSyncBuf(channelId);
    let consecutiveFailures = 0;
    const MAX_FAILURES = 3;
    const BACKOFF_MS = 30_000;
    const RETRY_MS = 2_000;
    while (!signal?.aborted) {
        try {
            // Sweep permission timeouts
            const timedOut = sweepTimeouts();
            for (const requestId of timedOut) {
                await protocol.sendPermissionVerdict(requestId, "deny");
                process.stderr.write(`Permission ${requestId} timed out, auto-denied.\n`);
            }
            const resp = await getUpdates({
                baseUrl: cfg.baseUrl,
                token: cfg.botToken,
                routeTag: cfg.routeTag,
                get_updates_buf: getUpdatesBuf,
            });
            // Check for API errors
            const isApiError = (resp.ret !== undefined && resp.ret !== 0) ||
                (resp.errcode !== undefined && resp.errcode !== 0);
            if (isApiError) {
                consecutiveFailures++;
                process.stderr.write(`getUpdates API error: ret=${resp.ret} errcode=${resp.errcode}\n`);
                await sleep(consecutiveFailures >= MAX_FAILURES ? BACKOFF_MS : RETRY_MS);
                if (consecutiveFailures >= MAX_FAILURES)
                    consecutiveFailures = 0;
                continue;
            }
            consecutiveFailures = 0;
            // Persist sync buf
            if (resp.get_updates_buf) {
                getUpdatesBuf = resp.get_updates_buf;
                saveSyncBuf(channelId, getUpdatesBuf);
            }
            // Process messages
            for (const msg of resp.msgs ?? []) {
                await processInbound(msg, cfg);
            }
        }
        catch (err) {
            consecutiveFailures++;
            process.stderr.write(`getUpdates error: ${err}\n`);
            await sleep(consecutiveFailures >= MAX_FAILURES ? BACKOFF_MS : RETRY_MS);
            if (consecutiveFailures >= MAX_FAILURES)
                consecutiveFailures = 0;
        }
    }
}
async function processInbound(msg, cfg) {
    // Extract text content
    let content = "";
    for (const item of msg.item_list ?? []) {
        if (item.type === 1 && item.text_item?.text) {
            content += item.text_item.text;
        }
        if (item.type === 3 && item.voice_item?.text && !content) {
            content = item.voice_item.text;
        }
    }
    if (!content)
        return;
    // Sender gating: only accept permission verdicts from the authenticated user
    const isAuthenticatedUser = msg.from_user_id === cfg.userId;
    if (isAuthenticatedUser) {
        // Check if this is a permission reply
        const verdict = parsePermissionReply(content);
        if (verdict) {
            await protocol.sendPermissionVerdict(verdict.requestId, verdict.behavior);
            return;
        }
    }
    // Regular message — push to Claude Code session
    await protocol.sendChannelMessage(content, {
        sender: msg.from_user_id ?? "unknown",
        timestamp: String(msg.create_time_ms ?? Date.now()),
    });
}
// --- Helpers ---
async function sendReply(text, cfg) {
    await apiSendMessage({
        baseUrl: cfg.baseUrl,
        token: cfg.botToken,
        routeTag: cfg.routeTag,
        body: {
            msg: {
                from_user_id: "",
                to_user_id: cfg.userId,
                client_id: `wb-reply-${Date.now()}`,
                message_type: MessageType.BOT,
                message_state: MessageState.FINISH,
                item_list: [{ type: MessageItemType.TEXT, text_item: { text } }],
            },
        },
    });
}
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
// --- Shutdown ---
const pollAbort = new AbortController();
function shutdown() {
    process.stderr.write("wechat-bridge: shutting down\n");
    pollAbort.abort();
    server.close().catch(() => { });
    process.exit(0);
}
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
// --- Main ---
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    process.stderr.write(`wechat-bridge: connected (channel=${channelId})\n`);
    // Start polling concurrently — runs alongside MCP message handling
    void startPolling(config, pollAbort.signal);
}
main().catch((err) => {
    process.stderr.write(`Fatal: ${err}\n`);
    process.exit(1);
});
//# sourceMappingURL=server.js.map