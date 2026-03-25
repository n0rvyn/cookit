/**
 * iLink Bot HTTP API layer for wechat-bridge plugin.
 * Origin: Adam WeChat adapter → iLink Bot API.
 */
import crypto from "node:crypto";
const CHANNEL_VERSION = "1.0.0";
const DEFAULT_LONG_POLL_TIMEOUT_MS = 35_000;
const DEFAULT_API_TIMEOUT_MS = 15_000;
const DEFAULT_CONFIG_TIMEOUT_MS = 10_000;
export function buildBaseInfo() {
    return { channel_version: CHANNEL_VERSION };
}
function ensureTrailingSlash(url) {
    return url.endsWith("/") ? url : `${url}/`;
}
function randomWechatUin() {
    const uint32 = crypto.randomBytes(4).readUInt32BE(0);
    return Buffer.from(String(uint32), "utf-8").toString("base64");
}
function buildHeaders(opts) {
    const headers = {
        "Content-Type": "application/json",
        AuthorizationType: "ilink_bot_token",
        "Content-Length": String(Buffer.byteLength(opts.body, "utf-8")),
        "X-WECHAT-UIN": randomWechatUin(),
    };
    if (opts.token?.trim()) {
        headers.Authorization = `Bearer ${opts.token.trim()}`;
    }
    if (opts.routeTag) {
        headers.SKRouteTag = opts.routeTag;
    }
    return headers;
}
async function apiFetch(params) {
    const base = ensureTrailingSlash(params.baseUrl);
    const url = new URL(params.endpoint, base);
    const hdrs = buildHeaders({ token: params.token, routeTag: params.routeTag, body: params.body });
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), params.timeoutMs);
    try {
        const res = await fetch(url.toString(), {
            method: "POST",
            headers: hdrs,
            body: params.body,
            signal: controller.signal,
        });
        clearTimeout(t);
        const rawText = await res.text();
        if (!res.ok) {
            throw new Error(`${params.label} ${res.status}: ${rawText}`);
        }
        return rawText;
    }
    catch (err) {
        clearTimeout(t);
        throw err;
    }
}
export async function getUpdates(params) {
    const timeout = params.timeoutMs ?? DEFAULT_LONG_POLL_TIMEOUT_MS;
    try {
        const rawText = await apiFetch({
            baseUrl: params.baseUrl,
            endpoint: "ilink/bot/getupdates",
            body: JSON.stringify({
                get_updates_buf: params.get_updates_buf ?? "",
                base_info: buildBaseInfo(),
            }),
            token: params.token,
            routeTag: params.routeTag,
            timeoutMs: timeout,
            label: "getUpdates",
        });
        return JSON.parse(rawText);
    }
    catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
            return { ret: 0, msgs: [], get_updates_buf: params.get_updates_buf };
        }
        throw err;
    }
}
export async function sendMessage(params) {
    await apiFetch({
        baseUrl: params.baseUrl,
        endpoint: "ilink/bot/sendmessage",
        body: JSON.stringify({ ...params.body, base_info: buildBaseInfo() }),
        token: params.token,
        routeTag: params.routeTag,
        timeoutMs: params.timeoutMs ?? DEFAULT_API_TIMEOUT_MS,
        label: "sendMessage",
    });
}
export async function getConfig(params) {
    const rawText = await apiFetch({
        baseUrl: params.baseUrl,
        endpoint: "ilink/bot/getconfig",
        body: JSON.stringify({
            ilink_user_id: params.ilinkUserId,
            context_token: params.contextToken,
            base_info: buildBaseInfo(),
        }),
        token: params.token,
        routeTag: params.routeTag,
        timeoutMs: params.timeoutMs ?? DEFAULT_CONFIG_TIMEOUT_MS,
        label: "getConfig",
    });
    return JSON.parse(rawText);
}
export async function sendTyping(params) {
    await apiFetch({
        baseUrl: params.baseUrl,
        endpoint: "ilink/bot/sendtyping",
        body: JSON.stringify({ ...params.body, base_info: buildBaseInfo() }),
        token: params.token,
        routeTag: params.routeTag,
        timeoutMs: params.timeoutMs ?? DEFAULT_CONFIG_TIMEOUT_MS,
        label: "sendTyping",
    });
}
//# sourceMappingURL=api.js.map