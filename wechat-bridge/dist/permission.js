/**
 * Permission relay: format Claude Code tool approval requests as WeChat messages,
 * parse user replies, and track pending permissions with timeout.
 */
import { sendMessage as apiSendMessage } from "./api.js";
import { MessageType, MessageState, MessageItemType } from "./types.js";
const pendingPermissions = new Map();
let msgCounter = 0;
function generateClientId() {
    return `wb-perm-${Date.now()}-${++msgCounter}`;
}
/**
 * Format and send a permission request to WeChat.
 */
export async function sendPermissionRequest(req, config, timeoutMs) {
    pendingPermissions.set(req.requestId, {
        ...req,
        timestamp: Date.now(),
        timeoutMs,
    });
    const text = [
        `\u{1f510} Claude wants to: ${req.toolName}`,
        req.description,
        `Preview: ${req.inputPreview.slice(0, 200)}`,
        "",
        `Reply 'yes ${req.requestId}' or 'no ${req.requestId}'`,
    ].join("\n");
    await apiSendMessage({
        baseUrl: config.baseUrl,
        token: config.botToken,
        routeTag: config.routeTag,
        body: {
            msg: {
                from_user_id: "",
                to_user_id: config.userId,
                client_id: generateClientId(),
                message_type: MessageType.BOT,
                message_state: MessageState.FINISH,
                item_list: [{ type: MessageItemType.TEXT, text_item: { text } }],
            },
        },
    });
}
/**
 * Parse a WeChat reply into a permission verdict.
 * Accepts: "yes XXXXX", "no XXXXX", "y XXXXX", "n XXXXX",
 * Chinese: "是 XXXXX", "否 XXXXX", "允许 XXXXX", "拒绝 XXXXX"
 */
export function parsePermissionReply(text) {
    const trimmed = text.trim().toLowerCase();
    // Pattern: (yes|y|是|允许|no|n|否|拒绝) <requestId>
    // request_id format is not guaranteed — accept any non-whitespace token
    const match = trimmed.match(/^(yes|y|是|允许|no|n|否|拒绝)\s+(\S+)$/);
    if (!match)
        return null;
    const [, verdict, requestId] = match;
    const pending = pendingPermissions.get(requestId);
    if (!pending)
        return null;
    pendingPermissions.delete(requestId);
    const allow = ["yes", "y", "是", "允许"].includes(verdict);
    return { requestId, behavior: allow ? "allow" : "deny" };
}
/**
 * Check if a pending permission has timed out.
 * Returns 'deny' if timed out, null if still waiting.
 */
export function checkPermissionTimeout(requestId) {
    const pending = pendingPermissions.get(requestId);
    if (!pending)
        return null;
    if (Date.now() - pending.timestamp > pending.timeoutMs) {
        pendingPermissions.delete(requestId);
        return "deny";
    }
    return null;
}
/**
 * Get all pending permission request IDs (for timeout sweep).
 */
export function getPendingRequestIds() {
    return [...pendingPermissions.keys()];
}
/**
 * Sweep all timed-out permissions. Returns requestIds that timed out.
 */
export function sweepTimeouts() {
    const timedOut = [];
    for (const requestId of pendingPermissions.keys()) {
        if (checkPermissionTimeout(requestId) === "deny") {
            timedOut.push(requestId);
        }
    }
    return timedOut;
}
//# sourceMappingURL=permission.js.map