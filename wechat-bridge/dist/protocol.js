import { z } from "zod";
// --- V1: Current experimental protocol ---
const CHANNEL_NOTIFICATION = "notifications/claude/channel";
const PERMISSION_REQUEST_NOTIFICATION = "notifications/claude/channel/permission_request";
const PERMISSION_VERDICT_NOTIFICATION = "notifications/claude/channel/permission";
const PermissionRequestSchema = z.object({
    method: z.literal(PERMISSION_REQUEST_NOTIFICATION),
    params: z.object({
        request_id: z.string(),
        tool_name: z.string(),
        description: z.string(),
        input_preview: z.string(),
    }),
});
export class McpChannelProtocolV1 {
    server;
    constructor(server) {
        this.server = server;
    }
    async sendChannelMessage(content, meta) {
        await this.server.notification({
            method: CHANNEL_NOTIFICATION,
            params: { content, meta },
        });
    }
    async sendPermissionVerdict(requestId, behavior) {
        await this.server.notification({
            method: PERMISSION_VERDICT_NOTIFICATION,
            params: { request_id: requestId, behavior },
        });
    }
    onPermissionRequest(handler) {
        this.server.setNotificationHandler(PermissionRequestSchema, async ({ params }) => {
            await handler(params);
        });
    }
}
// --- Factory ---
/**
 * Create the appropriate protocol adapter for the given MCP server.
 * Currently only V1 (experimental) exists; future versions can be added here.
 */
export function createProtocol(server) {
    return new McpChannelProtocolV1(server);
}
//# sourceMappingURL=protocol.js.map