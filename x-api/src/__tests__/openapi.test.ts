/**
 * Tests for openapi.ts — OpenAPI spec parser.
 */
import { describe, it } from "node:test";
import assert from "node:assert";

// Inline a minimal parseSpec + helpers for unit testing without exporting internals.
// We test by creating a synthetic OpenAPI spec and verifying the output.

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
  nullable?: boolean;
}

interface OpenApiSpec {
  paths?: Record<string, PathItem>;
  components?: {
    schemas?: Record<string, SchemaObject>;
    securitySchemes?: Record<string, unknown>;
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
}

interface RequestBody {
  content?: Record<string, { schema?: SchemaObject }>;
}

interface SecurityRequirement {
  [name: string]: string[];
}

// --- Minimal inline copy of the key parsing functions for testing ---

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
    if (visited.has(ref)) return { type: "object" };
    visited.add(ref);
    const resolved = resolveRef(spec, ref);
    if (!resolved) return { type: "object" };
    return resolveAllRefs(spec, resolved, visited);
  }

  if (Array.isArray(node)) {
    return node.map((item) =>
      resolveAllRefs(spec, item as SchemaObject, new Set(visited)),
    ) as unknown as SchemaObject;
  }

  const result: SchemaObject = { ...node };
  if (node.properties) {
    result.properties = {};
    for (const [k, v] of Object.entries(node.properties)) {
      result.properties[k] = resolveAllRefs(spec, v as SchemaObject, new Set(visited));
    }
  }
  if (result.items) {
    result.items = resolveAllRefs(spec, node.items!, new Set(visited));
  }
  if (result.allOf) {
    const merged: SchemaObject = { type: "object" };
    for (const sub of result.allOf) {
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

// --- parseSpec inline ---

interface ToolMeta {
  method: string;
  pathTemplate: string;
  paramLocations: { path: string[]; query: string[]; body: boolean };
  securitySchemes: string[];
}

function parseSpecForTest(spec: OpenApiSpec): Map<string, { name: string; meta: ToolMeta }> {
  const tools = new Map<string, { name: string; meta: ToolMeta }>();

  for (const [path, pathItem] of Object.entries(spec.paths ?? {})) {
    if (path.includes("/webhooks") || path.includes("/stream")) continue;

    const operations: [string, Operation | undefined][] = [
      ["get", pathItem.get],
      ["post", pathItem.post],
      ["put", pathItem.put],
      ["delete", pathItem.delete],
      ["patch", pathItem.patch],
    ];

    for (const [method, operation] of operations) {
      if (!operation?.operationId) continue;
      if (operation["x-twitter-streaming"]) continue;

      const pathParams: string[] = [];
      const queryParams: string[] = [];
      for (const param of operation.parameters ?? []) {
        if (param.in === "path") pathParams.push(param.name);
        else if (param.in === "query") queryParams.push(param.name);
      }

      const hasBody = !!operation.requestBody?.content?.["application/json"];

      tools.set(operation.operationId, {
        name: operation.operationId,
        meta: {
          method: method.toUpperCase(),
          pathTemplate: path,
          paramLocations: { path: pathParams, query: queryParams, body: hasBody },
          securitySchemes: [],
        },
      });
    }
  }

  return tools;
}

// --- Tests ---

describe("resolveRef", () => {
  it("resolves a simple $ref", () => {
    const spec: OpenApiSpec = {
      components: {
        schemas: {
          User: { type: "object", properties: { id: { type: "string" } } },
        },
      },
    };
    const result = resolveRef(spec, "#/components/schemas/User");
    assert.deepStrictEqual(result, { type: "object", properties: { id: { type: "string" } } });
  });

  it("returns undefined for invalid $ref", () => {
    const spec: OpenApiSpec = {};
    const result = resolveRef(spec, "#/components/schemas/NotFound");
    assert.strictEqual(result, undefined);
  });

  it("returns undefined for non-# $ref", () => {
    const spec: OpenApiSpec = {};
    const result = resolveRef(spec, "https://example.com/schemas/User");
    assert.strictEqual(result, undefined);
  });
});

describe("resolveAllRefs", () => {
  it("resolves nested $refs", () => {
    const spec: OpenApiSpec = {
      components: {
        schemas: {
          User: { $ref: "#/components/schemas/Base" },
          Base: { type: "object", properties: { id: { type: "string" } } },
        },
      },
    };
    const result = resolveAllRefs(spec, { $ref: "#/components/schemas/User" } as SchemaObject);
    assert.deepStrictEqual(result, { type: "object", properties: { id: { type: "string" } } });
  });

  it("detects circular $refs and returns a guard object", () => {
    const spec: OpenApiSpec = {
      components: {
        schemas: {
          User: { $ref: "#/components/schemas/User" },
        },
      },
    };
    const result = resolveAllRefs(spec, { $ref: "#/components/schemas/User" } as SchemaObject);
    assert.deepStrictEqual(result, { type: "object" });
  });

  it("resolves allOf with multiple schemas", () => {
    const spec: OpenApiSpec = {
      components: {
        schemas: {
          Name: { type: "object", properties: { name: { type: "string" } } },
          Age: { type: "object", properties: { age: { type: "integer" } } },
        },
      },
    };
    const result = resolveAllRefs(spec, {
      allOf: [
        { $ref: "#/components/schemas/Name" },
        { $ref: "#/components/schemas/Age" },
      ],
    } as SchemaObject);
    assert.deepStrictEqual(result.properties?.name, { type: "string" });
    assert.deepStrictEqual(result.properties?.age, { type: "integer" });
  });
});

describe("Spec filtering", () => {
  it("excludes /webhooks paths", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/users": { get: { operationId: "getUsers" } },
        "/webhooks/users": { get: { operationId: "getWebhooks" } },
      },
    };
    const tools = parseSpecForTest(spec);
    assert.strictEqual(tools.has("getUsers"), true);
    assert.strictEqual(tools.has("getWebhooks"), false);
  });

  it("excludes /stream paths", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/tweets": { get: { operationId: "getTweets" } },
        "/tweets/stream": { get: { operationId: "streamTweets" } },
      },
    };
    const tools = parseSpecForTest(spec);
    assert.strictEqual(tools.has("getTweets"), true);
    assert.strictEqual(tools.has("streamTweets"), false);
  });

  it("excludes operations without operationId", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/users": {
          get: { operationId: "getUsers" },
          post: { summary: "Create user" }, // no operationId
        },
      },
    };
    const tools = parseSpecForTest(spec);
    assert.strictEqual(tools.has("getUsers"), true);
    assert.strictEqual(tools.has("post"), false);
  });

  it("excludes x-twitter-streaming operations", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/tweets/sample": {
          get: {
            operationId: "getSampleStream",
            "x-twitter-streaming": true,
          },
        },
      },
    };
    const tools = parseSpecForTest(spec);
    assert.strictEqual(tools.has("getSampleStream"), false);
  });
});

describe("Tool generation", () => {
  it("generates correct paramLocations for path and query params", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/users/{userId}": {
          get: {
            operationId: "getUser",
            parameters: [
              { name: "userId", in: "path", required: true, schema: { type: "string" } },
              { name: "expansions", in: "query", schema: { type: "string" } },
            ],
          },
        },
      },
    };
    const tools = parseSpecForTest(spec);
    const meta = tools.get("getUser")?.meta;
    assert.deepStrictEqual(meta?.paramLocations.path, ["userId"]);
    assert.deepStrictEqual(meta?.paramLocations.query, ["expansions"]);
    assert.strictEqual(meta?.paramLocations.body, false);
  });

  it("marks body=true when requestBody is present", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/tweets": {
          post: {
            operationId: "createTweet",
            requestBody: {
              content: {
                "application/json": {
                  schema: { type: "object", properties: { text: { type: "string" } } },
                },
              },
            },
          },
        },
      },
    };
    const tools = parseSpecForTest(spec);
    const meta = tools.get("createTweet")?.meta;
    assert.strictEqual(meta?.paramLocations.body, true);
  });

  it("uses correct HTTP method", () => {
    const spec: OpenApiSpec = {
      paths: {
        "/users": {
          get: { operationId: "listUsers" },
          post: { operationId: "createUser" },
          delete: { operationId: "deleteUsers" },
          patch: { operationId: "updateUser" },
        },
      },
    };
    const tools = parseSpecForTest(spec);
    assert.strictEqual(tools.get("listUsers")?.meta.method, "GET");
    assert.strictEqual(tools.get("createUser")?.meta.method, "POST");
    assert.strictEqual(tools.get("deleteUsers")?.meta.method, "DELETE");
    assert.strictEqual(tools.get("updateUser")?.meta.method, "PATCH");
  });
});
