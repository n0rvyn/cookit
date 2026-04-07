/**
 * X API v2 MCP Server — shared types.
 */

export type AuthMode = "bearer" | "oauth2";

export interface OAuth2Tokens {
  access_token: string;
  refresh_token: string;
  expires_at: number; // Unix ms
  scope: string;
}

export interface ToolMeta {
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  pathTemplate: string;
  paramLocations: {
    path: string[];
    query: string[];
    body: boolean;
  };
  securitySchemes: string[];
}
