export declare const DEFAULT_API_BASE_URL = "https://ilinkai.weixin.qq.com";
export declare const DEFAULT_CHANNEL_ID = "default";
export declare const DEFAULT_PERMISSION_TIMEOUT_MS = 120000;
export interface WeChatBridgeConfig {
    botToken: string;
    accountId: string;
    baseUrl: string;
    userId: string;
    routeTag?: string;
    createdAt: number;
}
export declare function loadConfig(channelId: string): WeChatBridgeConfig | null;
export declare function saveConfig(channelId: string, config: WeChatBridgeConfig): void;
/** Load sync buf for getUpdates long-poll state persistence. */
export declare function loadSyncBuf(channelId: string): string;
/** Save sync buf after each successful getUpdates poll. */
export declare function saveSyncBuf(channelId: string, buf: string): void;
