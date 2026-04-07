/**
 * X API OpenAPI spec parser — converts the X API spec into MCP tool definitions.
 */
import type { ToolMeta } from "./types.js";

const OPENAPI_SPEC_URL = "https://api.twitter.com/2/openapi.json";
const X_API_BASE = "https://api.x.com";

// --- Types for OpenAPI spec structure ---

interface OpenApiSpec {
  paths?: Record<string, PathItem>;
  components?: {
    schemas?: Record<string, SchemaObject>;
    securitySchemes?: Record<string, SecurityScheme>;
  };
  security?: SecurityRequirement[];
}

interface PathItem {
  get?: Operation;
  post?: Operation;
  put?: Operation;
  delete?: Operation;
  patch?: Operation;
}

interface Operation {
  operationId?: string;
  summary?: string;
  description?: string;
  parameters?: Parameter[];
  requestBody?: RequestBody;
  security?: SecurityRequirement[];
  "x-twitter-streaming"?: unknown;
}

interface Parameter {
  name: string;
  in: "path" | "query" | "header" | "cookie";
  required?: boolean;
  schema?: SchemaObject;
  description?: string;
  style?: string;
  explode?: boolean;
}

interface RequestBody {
  content?: Record<string, MediaType>;
}

interface MediaType {
  schema?: SchemaObject;
}

interface SchemaObject {
  type?: string;
  format?: string;
  properties?: Record<string, SchemaObject>;
  items?: SchemaObject;
  enum?: unknown[];
  required?: string[];
  $ref?: string;
  description?: string;
  allOf?: SchemaObject[];
  oneOf?: SchemaObject[];
  anyOf?: SchemaObject[];
  nullable?: boolean;
}

interface SecurityScheme {
  type: string;
  scheme?: string;
  bearerFormat?: string;
  flows?: Record<string, OAuthFlow>;
  name?: string;
  in?: string;
}

interface OAuthFlow {
  authorizationUrl?: string;
  tokenUrl?: string;
  scopes?: Record<string, string>;
  refreshUrl?: string;
}

interface SecurityRequirement {
  [name: string]: string[];
}

// --- $ref resolution ---

function resolveRef(spec: OpenApiSpec, $ref: string): SchemaObject | undefined {
  if (!$ref.startsWith("#/")) return undefined;
  const parts = $ref.slice(2).split("/");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let node: any = spec;
  for (const part of parts) {
    node = node?.[part];
  }
  return node as SchemaObject | undefined;
}

function resolveAllRefs(
  spec: OpenApiSpec,
  node: SchemaObject,
  visited = new Set<string>(),
): SchemaObject {
  if (!node || typeof node !== "object") return node;

  if (node.$ref) {
    const ref = node.$ref as string;
    if (visited.has(ref)) return { type: "object" }; // cycle guard
    visited.add(ref);
    const resolved = resolveRef(spec, ref);
    if (!resolved) return { type: "object" };
    return resolveAllRefs(spec, resolved, visited);
  }

  if (Array.isArray(node)) {
    return node.map((item) => resolveAllRefs(spec, item as SchemaObject, new Set(visited))) as unknown as SchemaObject;
  }

  const result: SchemaObject = { ...node };
  if (node.properties) {
    result.properties = {};
    for (const [k, v] of Object.entries(node.properties)) {
      result.properties[k] = resolveAllRefs(spec, v as SchemaObject, new Set(visited));
    }
  }
  if (node.items) {
    result.items = resolveAllRefs(spec, node.items, new Set(visited));
  }
  if (node.allOf) {
    const merged: SchemaObject = { type: "object" };
    for (const sub of node.allOf) {
      const resolved = resolveAllRefs(spec, sub, new Set(visited));
      if (resolved.properties) {
        merged.properties = { ...(merged.properties ?? {}), ...resolved.properties };
      }
      if (resolved.required) {
        merged.required = [...(merged.required ?? []), ...resolved.required];
      }
    }
    return merged;
  }
  return result;
}

// --- Schema to JSON Schema conversion ---

function schemaToJsonSchema(spec: OpenApiSpec, schema?: SchemaObject): SchemaObject {
  if (!schema) return { type: "object" };
  const resolved = resolveAllRefs(spec, schema);
  return jsonSchemaFromResolved(resolved);
}

function jsonSchemaFromResolved(schema: SchemaObject): SchemaObject {
  if (!schema || typeof schema !== "object") return { type: "object" };

  const result: SchemaObject = {};

  if (schema.type) result.type = schema.type;
  if (schema.format) result.format = schema.format;
  if (schema.description) result.description = schema.description;
  if (schema.nullable) result.nullable = true;

  if (schema.enum) {
    result.enum = schema.enum;
  }

  if (schema.items) {
    result.items = jsonSchemaFromResolved(schema.items);
  }

  if (schema.properties) {
    result.properties = {};
    for (const [k, v] of Object.entries(schema.properties)) {
      result.properties[k] = jsonSchemaFromResolved(v);
    }
  }

  if (schema.required) {
    result.required = schema.required;
  }

  return result;
}

// --- Main parser ---

export async function fetchOpenApiSpec(): Promise<OpenApiSpec> {
  process.stderr.write(`Fetching OpenAPI spec from ${OPENAPI_SPEC_URL}...\n`);
  const resp = await fetch(OPENAPI_SPEC_URL);
  if (!resp.ok) {
    process.stderr.write(
      `Failed to fetch OpenAPI spec: ${resp.status} ${resp.statusText}\n` +
      `URL: ${OPENAPI_SPEC_URL}\n` +
      `Check your network connection and the URL. Exiting.\n`,
    );
    process.exit(1);
  }
  return resp.json() as Promise<OpenApiSpec>;
}

interface ParsedTool {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, SchemaObject>;
    required?: string[];
  };
}

export function parseSpec(spec: OpenApiSpec): Map<string, { tool: ParsedTool; meta: ToolMeta }> {
  const tools = new Map<string, { tool: ParsedTool; meta: ToolMeta }>();

  // Parse allowlist from env
  const allowlistRaw = process.env["X_API_TOOL_ALLOWLIST"];
  const allowlist = allowlistRaw
    ? new Set(allowlistRaw.split(",").map((s) => s.trim()).filter(Boolean))
    : null;

  for (const [path, pathItem] of Object.entries(spec.paths ?? {})) {
    // Exclude streaming, webhook, and stream paths
    if (
      path.includes("/webhooks") ||
      path.includes("/stream") ||
      path.includes("/2/:stream"))
    {
      continue;
    }

    for (const [method, operation] of Object.entries(extractOperations(pathItem))) {
      if (!operation?.operationId) continue;
      if (operation["x-twitter-streaming"]) continue;

      if (allowlist && !allowlist.has(operation.operationId)) {
        continue;
      }

      const { inputSchema, paramLocations } = buildInputSchema(spec, operation, path);

      const toolDef: ParsedTool = {
        name: operation.operationId,
        description:
          operation.description ??
          operation.summary ??
          `X API ${method.toUpperCase()} ${path}`,
        inputSchema,
      };

      const meta: ToolMeta = {
        method: method.toUpperCase() as ToolMeta["method"],
        pathTemplate: path,
        paramLocations,
        securitySchemes: extractSecurity(operation, spec),
      };

      tools.set(operation.operationId, { tool: toolDef, meta });
    }
  }

  process.stderr.write(`Parsed ${tools.size} tools from OpenAPI spec.\n`);
  return tools;
}

function extractOperations(pathItem: PathItem): Record<string, Operation | undefined> {
  return {
    get: pathItem.get,
    post: pathItem.post,
    put: pathItem.put,
    delete: pathItem.delete,
    patch: pathItem.patch,
  };
}

function buildInputSchema(
  spec: OpenApiSpec,
  operation: Operation,
  path: string,
): {
  inputSchema: { type: "object"; properties: Record<string, SchemaObject>; required?: string[] };
  paramLocations: ToolMeta["paramLocations"];
} {
  const properties: Record<string, SchemaObject> = {};
  const required: string[] = [];
  const pathParams: string[] = [];
  const queryParams: string[] = [];
  let hasBody = false;

  for (const param of operation.parameters ?? []) {
    const paramSchema = param.schema ? schemaToJsonSchema(spec, param.schema) : { type: "string" };

    if (param.required) required.push(param.name);
    properties[param.name] = {
      description: param.description,
      ...paramSchema,
    };

    if (param.in === "path") pathParams.push(param.name);
    else if (param.in === "query") queryParams.push(param.name);
  }

  // Request body
  const bodyContent = operation.requestBody?.content?.["application/json"];
  if (bodyContent?.schema) {
    hasBody = true;
    const bodySchema = schemaToJsonSchema(spec, bodyContent.schema);
    // Inline body properties rather than a single "body" object, to give MCP clients
    // direct access to the request body fields
    if (bodySchema.properties) {
      for (const [k, v] of Object.entries(bodySchema.properties)) {
        properties[k] = v as SchemaObject;
        if (bodySchema.required?.includes(k)) required.push(k);
      }
    }
  }

  return {
    inputSchema: {
      type: "object",
      properties,
      ...(required.length > 0 ? { required } : {}),
    },
    paramLocations: {
      path: pathParams,
      query: queryParams,
      body: hasBody,
    },
  };
}

function extractSecurity(operation: Operation, spec: OpenApiSpec): string[] {
  const sec = operation.security ?? spec.security ?? [];
  return sec.flatMap((s) => Object.keys(s));
}
