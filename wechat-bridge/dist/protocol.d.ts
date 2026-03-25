/**
 * Channel protocol adapter layer (DP-001 Option B).
 * Wraps MCP experimental notification names behind an interface so future
 * API changes only require adding a new protocol version class.
 */
import type { Server } from "@modelcontextprotocol/sdk/server/index.js";
export interface ChannelProtocol {
    /** Push a message from WeChat into the Claude Code session. */
    sendChannelMessage(content: string, meta?: Record<string, string>): Promise<void>;
    /** Return a permission verdict (allow/deny) to Claude Code. */
    sendPermissionVerdict(requestId: string, behavior: "allow" | "deny"): Promise<void>;
    /** Register a handler for incoming permission requests from Claude Code. */
    onPermissionRequest(handler: PermissionRequestHandler): void;
}
export interface PermissionRequestParams {
    request_id: string;
    tool_name: string;
    description: string;
    input_preview: string;
}
export type PermissionRequestHandler = (params: PermissionRequestParams) => void | Promise<void>;
export declare class McpChannelProtocolV1 implements ChannelProtocol {
    private server;
    constructor(server: Server);
    sendChannelMessage(content: string, meta?: Record<string, string>): Promise<void>;
    sendPermissionVerdict(requestId: string, behavior: "allow" | "deny"): Promise<void>;
    onPermissionRequest(handler: PermissionRequestHandler): void;
}
/**
 * Create the appropriate protocol adapter for the given MCP server.
 * Currently only V1 (experimental) exists; future versions can be added here.
 */
export declare function createProtocol(server: Server): ChannelProtocol;
