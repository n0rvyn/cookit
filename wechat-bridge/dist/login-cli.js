#!/usr/bin/env node
/**
 * CLI entry point for WeChat bridge login.
 * Usage: wechat-bridge login [--api-base-url URL] [--channel-id ID] [--route-tag TAG]
 */
import { startWeixinLoginWithQr, waitForWeixinLogin } from "./login-qr.js";
import { saveConfig, loadConfig, DEFAULT_API_BASE_URL, DEFAULT_CHANNEL_ID } from "./config.js";
function parseArgs(args) {
    const result = {};
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg.startsWith("--") && i + 1 < args.length) {
            const key = arg.slice(2);
            result[key] = args[++i];
        }
    }
    return result;
}
async function login(opts) {
    // Check if already logged in
    const existing = loadConfig(opts.channelId);
    if (existing && !opts.force) {
        console.log(`Already logged in for channel "${opts.channelId}" (account: ${existing.accountId}).`);
        console.log("Use --force to re-login, or delete ~/.adam/wechat/ to reset.");
        return;
    }
    console.log(`Starting WeChat QR login (API: ${opts.apiBaseUrl})...`);
    const qrResult = await startWeixinLoginWithQr({
        apiBaseUrl: opts.apiBaseUrl,
        routeTag: opts.routeTag,
    });
    if (!qrResult.qrcodeUrl) {
        console.error("Failed to get QR code:", qrResult.message);
        process.exit(1);
    }
    // Display QR code URL — user can open in browser or use a QR terminal renderer
    console.log("\nScan this QR code with WeChat:");
    console.log(`  ${qrResult.qrcodeUrl}`);
    console.log("\nWaiting for scan...");
    const waitResult = await waitForWeixinLogin({
        sessionKey: qrResult.sessionKey,
        apiBaseUrl: opts.apiBaseUrl,
        routeTag: opts.routeTag,
        timeoutMs: 300_000, // 5 minutes
    });
    if (!waitResult.connected) {
        console.error("Login failed:", waitResult.message);
        process.exit(1);
    }
    // Persist credentials
    saveConfig(opts.channelId, {
        botToken: waitResult.botToken,
        accountId: waitResult.accountId,
        baseUrl: waitResult.baseUrl || opts.apiBaseUrl,
        userId: waitResult.userId,
        createdAt: Date.now(),
    });
    console.log(`\nConnected! Credentials saved for channel "${opts.channelId}".`);
    console.log("You can now use: claude --channels wechat-bridge");
}
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    if (command !== "login") {
        console.log("Usage: wechat-bridge login [--force] [--api-base-url URL] [--channel-id ID] [--route-tag TAG]");
        process.exit(command === "--help" || command === "-h" ? 0 : 1);
    }
    const rawArgs = args.slice(1);
    const hasForce = rawArgs.includes("--force");
    const opts = parseArgs(rawArgs.filter((a) => a !== "--force"));
    await login({
        apiBaseUrl: opts["api-base-url"] || process.env.WECHAT_API_BASE_URL || DEFAULT_API_BASE_URL,
        channelId: opts["channel-id"] || process.env.WECHAT_CHANNEL_ID || DEFAULT_CHANNEL_ID,
        routeTag: opts["route-tag"] || process.env.WECHAT_ROUTE_TAG,
        force: hasForce,
    });
}
main().catch((err) => {
    console.error("Fatal:", err);
    process.exit(1);
});
//# sourceMappingURL=login-cli.js.map