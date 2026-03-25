/**
 * Token persistence and configuration for wechat-bridge.
 * Stores/loads WeChat session credentials to ~/.adam/wechat/.
 */
import fs from "node:fs";
import path from "node:path";
import { homedir } from "node:os";
export const DEFAULT_API_BASE_URL = "https://ilinkai.weixin.qq.com";
export const DEFAULT_CHANNEL_ID = "default";
export const DEFAULT_PERMISSION_TIMEOUT_MS = 120_000;
const WECHAT_CONFIG_DIR = path.join(homedir(), ".adam", "wechat");
function configPath(channelId) {
    return path.join(WECHAT_CONFIG_DIR, `${channelId}.json`);
}
export function loadConfig(channelId) {
    try {
        const raw = fs.readFileSync(configPath(channelId), "utf-8");
        const parsed = JSON.parse(raw);
        if (!parsed.botToken || !parsed.baseUrl)
            return null;
        return parsed;
    }
    catch {
        return null;
    }
}
export function saveConfig(channelId, config) {
    fs.mkdirSync(WECHAT_CONFIG_DIR, { recursive: true });
    fs.writeFileSync(configPath(channelId), JSON.stringify(config, null, 2), "utf-8");
}
/** Load sync buf for getUpdates long-poll state persistence. */
export function loadSyncBuf(channelId) {
    try {
        return fs.readFileSync(path.join(WECHAT_CONFIG_DIR, `${channelId}.sync`), "utf-8");
    }
    catch {
        return "";
    }
}
/** Save sync buf after each successful getUpdates poll. */
export function saveSyncBuf(channelId, buf) {
    fs.mkdirSync(WECHAT_CONFIG_DIR, { recursive: true });
    fs.writeFileSync(path.join(WECHAT_CONFIG_DIR, `${channelId}.sync`), buf, "utf-8");
}
//# sourceMappingURL=config.js.map