/**
 * Bearer Token authentication for X API.
 */
import { getBearerToken } from "./oauth2.js";

export function applyBearerAuth(headers: Headers): void {
  const token = getBearerToken();
  headers.set("Authorization", `Bearer ${token}`);
}
