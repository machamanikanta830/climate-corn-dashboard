import { copyFile, mkdir } from "node:fs/promises";
import { fileURLToPath, URL } from "node:url";

const source = fileURLToPath(new URL("../worker/index.js", import.meta.url));
const serverDirectory = fileURLToPath(new URL("../dist/server", import.meta.url));
const destination = fileURLToPath(
  new URL("../dist/server/index.js", import.meta.url)
);

await mkdir(serverDirectory, { recursive: true });
await copyFile(source, destination);
