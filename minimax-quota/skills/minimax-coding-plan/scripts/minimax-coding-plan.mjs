#!/usr/bin/env node

import os from "node:os";
import process from "node:process";
import { execFileSync } from "node:child_process";

const DEFAULT_URL =
  "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains";

function main() {
  const args = parseArgs(process.argv.slice(2));
  const apiKey = args.apiKey ?? process.env.MINIMAX_API_KEY;
  const groupId = args.groupId ?? process.env.MINIMAX_GROUP_ID;
  const outputJson = args.json || process.env.MINIMAX_OUTPUT === "json";

  if (!apiKey) {
    fail(
      [
        "MINIMAX_API_KEY is required.",
        "Pass --api-key or set MINIMAX_API_KEY.",
        "Get your key from: https://platform.minimaxi.com/",
      ].join("\n"),
    );
  }

  const payload = fetchRemains(apiKey, groupId);

  if (!isSuccess(payload)) {
    const msg = payload?.base_resp?.status_msg || safeJson(payload);
    fail(`MiniMax API error: ${msg}`, 3);
  }

  if (outputJson) {
    process.stdout.write(`${safeJson(payload)}\n`);
    return;
  }

  printSummary(groupId, payload);
}

function parseArgs(argv) {
  const args = {
    apiKey: undefined,
    groupId: undefined,
    json: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];

    if (value === "--api-key") {
      args.apiKey = argv[index + 1];
      index += 1;
      continue;
    }

    if (value === "--group-id") {
      args.groupId = argv[index + 1];
      index += 1;
      continue;
    }

    if (value === "--json") {
      args.json = true;
      continue;
    }

    if (value === "--help" || value === "-h") {
      printHelp();
      process.exit(0);
    }

    fail(`Unknown argument: ${value}`);
  }

  return args;
}

function printHelp() {
  process.stdout.write(
    [
      "Usage: minimax-coding-plan.mjs [options]",
      "",
      "Options:",
      "  --api-key <key>   Override MINIMAX_API_KEY",
      "  --group-id <id>   Override MINIMAX_GROUP_ID",
      "  --json            Print raw JSON response",
      "",
      "Environment:",
      "  MINIMAX_API_KEY      Required; OpenAPI key from platform.minimaxi.com",
      "  MINIMAX_GROUP_ID     Optional; defaults to key's default group",
      "  MINIMAX_OUTPUT=json  Same as --json",
    ].join("\n"),
  );
}

function fetchRemains(apiKey, groupId) {
  const url = new URL(DEFAULT_URL);
  if (groupId) {
    url.searchParams.set("GroupId", groupId);
  }

  const command = [
    "-sS",
    "-m",
    "15",
    url.toString(),
    "-H",
    `Authorization: Bearer ${apiKey}`,
  ];

  let raw;
  try {
    raw = execFileSync("curl", command, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    });
  } catch (error) {
    const stderr = error.stderr ? String(error.stderr).trim() : "";
    fail(
      [
        "Failed to reach MiniMax remains endpoint.",
        stderr || String(error.message ?? error),
        "Check network, proxy, or DNS. The request has a 15s timeout.",
      ].join("\n"),
      5,
    );
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    fail(
      `Failed to parse MiniMax response as JSON.\n${String(error)}\n${raw}`,
      4,
    );
  }
}

function isSuccess(payload) {
  return payload?.base_resp?.status_code === 0;
}

function printSummary(groupId, payload) {
  const rows = Array.isArray(payload.model_remains) ? payload.model_remains : [];

  process.stdout.write(
    `MiniMax coding plan remains${groupId ? ` for GroupId ${groupId}` : ""}\n`,
  );
  process.stdout.write("model\tinterval\tweekly\n");

  for (const row of rows) {
    const interval = `${row.current_interval_usage_count}/${row.current_interval_total_count}`;
    const weekly = `${row.current_weekly_usage_count}/${row.current_weekly_total_count}`;
    process.stdout.write(`${row.model_name}\t${interval}\t${weekly}\n`);
  }
}

function safeJson(value) {
  return JSON.stringify(value, null, 2);
}

function fail(message, code = 1) {
  process.stderr.write(`${message}\n`);
  process.exit(code);
}

main();
