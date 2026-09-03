// Generate IDAT-GPT PNG assets from web/public/logo.svg with sharp.
// Run from web/ (needs sharp from node_modules): SCRATCH=<dir> bun ../tools/rebrand/gen_assets.mjs
import sharp from "sharp";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const REPO = fileURLToPath(new URL("../..", import.meta.url)).replace(
  /[\\/]$/,
  ""
);
const PUB = `${REPO}/web/public`;
const STATIC = `${REPO}/backend/static/images`;
const markSvg = readFileSync(`${PUB}/logo.svg`);

// Match the dimensions of the assets being replaced.
const dims = {};
for (const f of [
  "logo.png",
  "logo-dark.png",
  "logotype.png",
  "logotype-dark.png",
]) {
  const m = await sharp(`${PUB}/${f}`).metadata();
  dims[f] = { w: m.width, h: m.height };
}
console.log("existing dims", dims);

function logotypeSvg(textColor) {
  // 64-high mark + wordmark; width sized for "IDAT-GPT" at 40px bold.
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 268 64" width="268" height="64">
    <svg x="0" y="0" width="64" height="64" viewBox="0 0 64 64" fill="none">${markSvg
      .toString()
      .replace(/<\?xml[^>]*>/, "")
      .replace(/<svg[^>]*>/, "")
      .replace(/<\/svg>\s*$/, "")}</svg>
    <text x="78" y="45" font-family="Segoe UI, Inter, Arial, Helvetica, sans-serif" font-size="38" font-weight="700" letter-spacing="-0.8" fill="${textColor}">IDAT-GPT</text>
  </svg>`;
}

const square = (size) =>
  sharp(markSvg, { density: 400 }).resize(size, size).png();
const wordmark = (color, h) =>
  sharp(Buffer.from(logotypeSvg(color)), { density: 400 })
    .resize({ height: h })
    .png();

const logoH = dims["logo.png"].h || 512;
const logoDarkH = dims["logo-dark.png"].h || logoH;
const typeH = dims["logotype.png"].h || 128;
const typeDarkH = dims["logotype-dark.png"].h || typeH;

await square(logoH).toFile(`${PUB}/logo.png`);
await square(logoDarkH).toFile(`${PUB}/logo-dark.png`);
await wordmark("#111827", typeH).toFile(`${PUB}/logotype.png`);
await wordmark("#F9FAFB", typeDarkH).toFile(`${PUB}/logotype-dark.png`);
await square(logoH).toFile(`${STATIC}/logo.png`);
await wordmark("#111827", typeH).toFile(`${STATIC}/logotype.png`);

// Favicon source frames; Pillow assembles the .ico.
for (const s of [16, 32, 48, 64, 128, 256]) {
  await square(s).toFile(`${process.env.SCRATCH}/favicon-${s}.png`);
}
// Preview sheet for visual check.
await wordmark("#111827", 128).toFile(
  `${process.env.SCRATCH}/preview-logotype.png`
);
await square(256).toFile(`${process.env.SCRATCH}/preview-mark.png`);
console.log("done");
