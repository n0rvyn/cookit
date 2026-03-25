#!/usr/bin/env node

// src/login-qr.ts
import { randomUUID } from "node:crypto";
var ACTIVE_LOGIN_TTL_MS = 5 * 6e4;
var QR_LONG_POLL_TIMEOUT_MS = 35e3;
var DEFAULT_ILINK_BOT_TYPE = "3";
var activeLogins = /* @__PURE__ */ new Map();
function isLoginFresh(login2) {
  return Date.now() - login2.startedAt < ACTIVE_LOGIN_TTL_MS;
}
function purgeExpiredLogins() {
  for (const [id, login2] of activeLogins) {
    if (!isLoginFresh(login2)) {
      activeLogins.delete(id);
    }
  }
}
async function fetchQRCode(apiBaseUrl, botType, routeTag) {
  const base = apiBaseUrl.endsWith("/") ? apiBaseUrl : `${apiBaseUrl}/`;
  const url = new URL(`ilink/bot/get_bot_qrcode?bot_type=${encodeURIComponent(botType)}`, base);
  const headers = {};
  if (routeTag) {
    headers.SKRouteTag = routeTag;
  }
  const response = await fetch(url.toString(), { headers });
  if (!response.ok) {
    const body = await response.text().catch(() => "(unreadable)");
    throw new Error(`Failed to fetch QR code: ${response.status} ${response.statusText} body=${body}`);
  }
  return await response.json();
}
async function pollQRStatus(apiBaseUrl, qrcode, routeTag) {
  const base = apiBaseUrl.endsWith("/") ? apiBaseUrl : `${apiBaseUrl}/`;
  const url = new URL(`ilink/bot/get_qrcode_status?qrcode=${encodeURIComponent(qrcode)}`, base);
  const headers = {
    "iLink-App-ClientVersion": "1"
  };
  if (routeTag) {
    headers.SKRouteTag = routeTag;
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), QR_LONG_POLL_TIMEOUT_MS);
  try {
    const response = await fetch(url.toString(), { headers, signal: controller.signal });
    clearTimeout(timer);
    const rawText = await response.text();
    if (!response.ok) {
      throw new Error(`Failed to poll QR status: ${response.status} ${response.statusText}`);
    }
    return JSON.parse(rawText);
  } catch (err) {
    clearTimeout(timer);
    if (err instanceof Error && err.name === "AbortError") {
      return { status: "wait" };
    }
    throw err;
  }
}
async function startWeixinLoginWithQr(opts) {
  const sessionKey = opts.accountId || randomUUID();
  purgeExpiredLogins();
  const existing = activeLogins.get(sessionKey);
  if (!opts.force && existing && isLoginFresh(existing) && existing.qrcodeUrl) {
    return {
      qrcodeUrl: existing.qrcodeUrl,
      message: "QR code ready. Scan with WeChat.",
      sessionKey
    };
  }
  if (!opts.apiBaseUrl) {
    return {
      message: "No baseUrl configured for this WeChat channel.",
      sessionKey
    };
  }
  try {
    const botType = opts.botType || DEFAULT_ILINK_BOT_TYPE;
    const qrResponse = await fetchQRCode(opts.apiBaseUrl, botType, opts.routeTag);
    const login2 = {
      sessionKey,
      id: randomUUID(),
      qrcode: qrResponse.qrcode,
      qrcodeUrl: qrResponse.qrcode_img_content,
      startedAt: Date.now()
    };
    activeLogins.set(sessionKey, login2);
    return {
      qrcodeUrl: qrResponse.qrcode_img_content,
      message: "Scan the QR code with WeChat to connect.",
      sessionKey
    };
  } catch (err) {
    return {
      message: `Failed to start login: ${String(err)}`,
      sessionKey
    };
  }
}
var MAX_QR_REFRESH_COUNT = 3;
async function waitForWeixinLogin(opts) {
  const activeLogin = activeLogins.get(opts.sessionKey);
  if (!activeLogin) {
    return { connected: false, message: "No active login session. Start QR login first." };
  }
  if (!isLoginFresh(activeLogin)) {
    activeLogins.delete(opts.sessionKey);
    return { connected: false, message: "QR code expired. Please start again." };
  }
  const timeoutMs = Math.max(opts.timeoutMs ?? 48e4, 1e3);
  const deadline = Date.now() + timeoutMs;
  let qrRefreshCount = 1;
  while (Date.now() < deadline) {
    try {
      const statusResponse = await pollQRStatus(opts.apiBaseUrl, activeLogin.qrcode, opts.routeTag);
      activeLogin.status = statusResponse.status;
      switch (statusResponse.status) {
        case "wait":
          break;
        case "scaned":
          break;
        case "expired": {
          qrRefreshCount++;
          if (qrRefreshCount > MAX_QR_REFRESH_COUNT) {
            activeLogins.delete(opts.sessionKey);
            return { connected: false, message: "Login timeout: QR expired multiple times." };
          }
          try {
            const botType = opts.botType || DEFAULT_ILINK_BOT_TYPE;
            const qrResponse = await fetchQRCode(opts.apiBaseUrl, botType, opts.routeTag);
            activeLogin.qrcode = qrResponse.qrcode;
            activeLogin.qrcodeUrl = qrResponse.qrcode_img_content;
            activeLogin.startedAt = Date.now();
          } catch (refreshErr) {
            activeLogins.delete(opts.sessionKey);
            return { connected: false, message: `QR refresh failed: ${String(refreshErr)}` };
          }
          break;
        }
        case "confirmed": {
          if (!statusResponse.ilink_bot_id) {
            activeLogins.delete(opts.sessionKey);
            return { connected: false, message: "Login failed: server did not return bot ID." };
          }
          activeLogins.delete(opts.sessionKey);
          return {
            connected: true,
            botToken: statusResponse.bot_token,
            accountId: statusResponse.ilink_bot_id,
            baseUrl: statusResponse.baseurl,
            userId: statusResponse.ilink_user_id,
            message: "Connected to WeChat successfully!"
          };
        }
      }
    } catch (err) {
      activeLogins.delete(opts.sessionKey);
      return { connected: false, message: `Login failed: ${String(err)}` };
    }
    await new Promise((r) => setTimeout(r, 1e3));
  }
  activeLogins.delete(opts.sessionKey);
  return { connected: false, message: "Login timeout. Please try again." };
}

// src/config.ts
import fs from "node:fs";
import path from "node:path";
import { homedir } from "node:os";
var DEFAULT_API_BASE_URL = "https://ilinkai.weixin.qq.com";
var DEFAULT_CHANNEL_ID = "default";
var WECHAT_CONFIG_DIR = path.join(homedir(), ".adam", "wechat");
function configPath(channelId) {
  return path.join(WECHAT_CONFIG_DIR, `${channelId}.json`);
}
function loadConfig(channelId) {
  try {
    const raw = fs.readFileSync(configPath(channelId), "utf-8");
    const parsed = JSON.parse(raw);
    if (!parsed.botToken || !parsed.baseUrl) return null;
    return parsed;
  } catch {
    return null;
  }
}
function saveConfig(channelId, config) {
  fs.mkdirSync(WECHAT_CONFIG_DIR, { recursive: true });
  fs.writeFileSync(configPath(channelId), JSON.stringify(config, null, 2), "utf-8");
}

// src/login-cli.ts
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
  const existing = loadConfig(opts.channelId);
  if (existing && !opts.force) {
    console.log(`Already logged in for channel "${opts.channelId}" (account: ${existing.accountId}).`);
    console.log("Use --force to re-login, or delete ~/.adam/wechat/ to reset.");
    return;
  }
  console.log(`Starting WeChat QR login (API: ${opts.apiBaseUrl})...`);
  const qrResult = await startWeixinLoginWithQr({
    apiBaseUrl: opts.apiBaseUrl,
    routeTag: opts.routeTag
  });
  if (!qrResult.qrcodeUrl) {
    console.error("Failed to get QR code:", qrResult.message);
    process.exit(1);
  }
  console.log("\nScan this QR code with WeChat:");
  console.log(`  ${qrResult.qrcodeUrl}`);
  console.log("\nWaiting for scan...");
  const waitResult = await waitForWeixinLogin({
    sessionKey: qrResult.sessionKey,
    apiBaseUrl: opts.apiBaseUrl,
    routeTag: opts.routeTag,
    timeoutMs: 3e5
    // 5 minutes
  });
  if (!waitResult.connected) {
    console.error("Login failed:", waitResult.message);
    process.exit(1);
  }
  saveConfig(opts.channelId, {
    botToken: waitResult.botToken,
    accountId: waitResult.accountId,
    baseUrl: waitResult.baseUrl || opts.apiBaseUrl,
    userId: waitResult.userId,
    createdAt: Date.now()
  });
  console.log(`
Connected! Credentials saved for channel "${opts.channelId}".`);
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
    force: hasForce
  });
}
main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
//# sourceMappingURL=login-cli.js.map
