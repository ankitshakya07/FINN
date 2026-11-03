import fs from "node:fs";

const pages = await fetch("http://127.0.0.1:9222/json/list").then((r) => r.json());
const target = pages.find((x) => x.type === "page" && x.url.includes("localhost:3000"));

if (!target) {
  console.error("No localhost:3000 page found in Chrome");
  process.exit(1);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.addEventListener("open", resolve, { once: true });
  ws.addEventListener("error", reject, { once: true });
});

let id = 0;
const pending = new Map();
ws.addEventListener("message", (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const p = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) p.reject(new Error(msg.error.message));
    else p.resolve(msg.result);
  }
});

function cdp(method, params = {}) {
  const callId = ++id;
  ws.send(JSON.stringify({ id: callId, method, params }));
  return new Promise((resolve, reject) => pending.set(callId, { resolve, reject }));
}

async function evaluate(expression) {
  const res = await cdp("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  return res.result?.value;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

await cdp("Runtime.enable");
await cdp("Page.enable");

// Reload page
await cdp("Page.reload", { ignoreCache: true });
await sleep(2500);

// Ensure #fundamentals is present and loaded
const exists = await evaluate("Boolean(document.getElementById('fundamentals'))");
console.log("Fundamentals section mounted:", exists);

// Wait for fundamentals data card
for (let i = 0; i < 20; i++) {
  const hasCard = await evaluate("Boolean(document.querySelector('.fund-company-card'))");
  if (hasCard) break;
  await sleep(500);
}

const companyTitle = await evaluate("document.querySelector('.company-title')?.textContent");
console.log("Loaded company:", companyTitle);

// Test across viewports and check overflow
const viewports = [
  ["desktop", 1440, 1100],
  ["tablet-768", 768, 1100],
  ["mobile-390", 390, 844],
];

for (const [name, w, h] of viewports) {
  await cdp("Emulation.setDeviceMetricsOverride", {
    width: w,
    height: h,
    deviceScaleFactor: 1,
    mobile: w < 600,
  });

  await evaluate("document.getElementById('fundamentals')?.scrollIntoView({ block: 'start' })");
  await sleep(600);

  // Remove nextjs dev portal for clean screenshot
  await evaluate("document.querySelector('nextjs-portal')?.remove()");

  const hasOverflow = await evaluate(
    "document.documentElement.scrollWidth > document.documentElement.clientWidth"
  );
  const clientWidth = await evaluate("document.documentElement.clientWidth");
  const scrollWidth = await evaluate("document.documentElement.scrollWidth");

  console.log(
    `${name} (${w}px): clientWidth=${clientWidth}, scrollWidth=${scrollWidth}, overflow=${hasOverflow}`
  );

  const screenshot = await cdp("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });

  fs.writeFileSync(
    `artifacts/fundamentals-${name}.png`,
    Buffer.from(screenshot.data, "base64")
  );
}

// Test Income statement tab
await evaluate("(()=>{ const btns = document.querySelectorAll('.statement-tab-btn'); for(const b of btns) { if(b.textContent.includes('Income')) { b.click(); break; } } })()");
await sleep(500);
const incomeScreenshot = await cdp("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
fs.writeFileSync("artifacts/fundamentals-income-mobile-390.png", Buffer.from(incomeScreenshot.data, "base64"));
console.log("Captured Income Statement mobile view");

// Test Ratios tab
await evaluate("(()=>{ const btns = document.querySelectorAll('.statement-tab-btn'); for(const b of btns) { if(b.textContent.includes('Ratios')) { b.click(); break; } } })()");
await sleep(500);
const ratiosScreenshot = await cdp("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
fs.writeFileSync("artifacts/fundamentals-ratios-mobile-390.png", Buffer.from(ratiosScreenshot.data, "base64"));
console.log("Captured Ratios & Trends mobile view");

ws.close();
console.log("CDP capture completed successfully.");
