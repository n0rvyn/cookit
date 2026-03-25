import type { WeChatBridgeConfig } from "./config.js";
export interface PermissionRequest {
    requestId: string;
    toolName: string;
    description: string;
    inputPreview: string;
}
/**
 * Format and send a permission request to WeChat.
 */
export declare function sendPermissionRequest(req: PermissionRequest, config: WeChatBridgeConfig, timeoutMs: number): Promise<void>;
/**
 * Parse a WeChat reply into a permission verdict.
 * Accepts: "yes XXXXX", "no XXXXX", "y XXXXX", "n XXXXX",
 * Chinese: "是 XXXXX", "否 XXXXX", "允许 XXXXX", "拒绝 XXXXX"
 */
export declare function parsePermissionReply(text: string): {
    requestId: string;
    behavior: "allow" | "deny";
} | null;
/**
 * Check if a pending permission has timed out.
 * Returns 'deny' if timed out, null if still waiting.
 */
export declare function checkPermissionTimeout(requestId: string): "deny" | null;
/**
 * Get all pending permission request IDs (for timeout sweep).
 */
export declare function getPendingRequestIds(): string[];
/**
 * Sweep all timed-out permissions. Returns requestIds that timed out.
 */
export declare function sweepTimeouts(): string[];
