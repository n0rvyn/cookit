import { build } from "esbuild";

const shared = {
  bundle: true,
  platform: "node",
  format: "esm",
  target: "node20",
  outdir: "dist",
  sourcemap: true,
};

await build({
  ...shared,
  entryPoints: ["src/server.ts", "src/auth-cli.ts"],
});
