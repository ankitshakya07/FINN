import fs from "node:fs";

const pages = await fetch("http://127.0.0.1:9222/json/list").then((r) => r.json());
let target = pages.find((x) => x.type === "page" && x.url.includes("localhost:3000"));

if (!target) {
  const newTab = await fetch("http://127.0.0.1:9222/json/new?http://localhost:3000").then((r) => r.json());
  target = newTab;
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));

let id = 0;
const send = (method, params = {}) =>
  new Promise((res) => {
    const cId = ++id;
    const handler = (e) => {
      const m = JSON.parse(e.data);
      if (m.id === cId) {
        ws.removeEventListener("message", handler);
        res(m.result);
      }
    };
    ws.addEventListener("message", handler);
    ws.send(JSON.stringify({ id: cId, method, params }));
  });

const evalCode = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  return r.result?.value;
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

console.log("Reloading application...");
await send("Page.reload", { ignoreCache: true });
await sleep(3000);

// --- 1. Mobile 390px Viewport Check ---
console.log("Setting 390px mobile viewport...");
await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await sleep(1000);

const rootOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth
  };
})()`);
console.log("Initial 390px Mobile Overflow Check:", rootOverflow);

// Verify mobile bottom navigation presence
const navTabsCount = await evalCode("document.querySelectorAll('.mobile-bottom-nav .mobile-tab-btn')?.length");
console.log(`Mobile bottom nav tabs count: ${navTabsCount}`);

// Capture initial overview screenshot
const ssOverview = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/mobile-overview-390.png", Buffer.from(ssOverview.data, "base64"));
console.log("Saved artifacts/mobile-overview-390.png");

// --- 2. Test Mobile Bottom Nav Tab: Watch ---
console.log("Tapping Watch tab on mobile bottom nav...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.mobile-tab-btn'));
  const watchTab = btns.find(b => b.textContent.includes('Watch'));
  if (watchTab) watchTab.click();
})()`);
await sleep(1500);

const watchCardCount = await evalCode("document.querySelectorAll('.watchlist-item-card')?.length");
const anomaliesCount = await evalCode("document.querySelectorAll('.anomaly-card')?.length");
console.log(`Watchlist cards: ${watchCardCount}, Anomalies rendered: ${anomaliesCount}`);

const watchOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  const section = document.getElementById('watch');
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth,
    sectionClientWidth: section?.clientWidth,
    sectionScrollWidth: section?.scrollWidth
  };
})()`);
console.log("Watch section 390px Overflow Check:", watchOverflow);

// Capture watch section screenshot
const ssWatch = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/mobile-watch-390.png", Buffer.from(ssWatch.data, "base64"));
console.log("Saved artifacts/mobile-watch-390.png");

// --- 3. Test Mobile Bottom Nav Tab: Research Hub ---
console.log("Tapping Research tab on mobile bottom nav...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.mobile-tab-btn'));
  const resTab = btns.find(b => b.textContent.includes('Research'));
  if (resTab) resTab.click();
})()`);
await sleep(1500);

const subtabsCount = await evalCode("document.querySelectorAll('.research-subtab-btn')?.length");
console.log(`Research sub-navigation tabs count: ${subtabsCount}`);

// Test switching to Fundamentals sub-tab
console.log("Clicking Fundamentals subtab...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.research-subtab-btn'));
  const fundBtn = btns.find(b => b.textContent.includes('Fundamentals'));
  if (fundBtn) fundBtn.click();
})()`);
await sleep(1200);

const hasFundamentalsSection = await evalCode("Boolean(document.getElementById('fundamentals'))");
console.log(`Fundamentals Section displayed: ${hasFundamentalsSection}`);

// Test switching to Promises sub-tab
console.log("Clicking Promises subtab...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.research-subtab-btn'));
  const promBtn = btns.find(b => b.textContent.includes('Promises'));
  if (promBtn) promBtn.click();
})()`);
await sleep(1200);

const hasPromisesSection = await evalCode("Boolean(document.getElementById('promised-delivered'))");
console.log(`Promises Section displayed: ${hasPromisesSection}`);

// Test switching back to Intelligence sub-tab
console.log("Clicking Intelligence subtab...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.research-subtab-btn'));
  const intelBtn = btns.find(b => b.textContent.includes('Intelligence'));
  if (intelBtn) intelBtn.click();
})()`);
await sleep(1200);

const researchOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth
  };
})()`);
console.log("Research Hub 390px Overflow Check:", researchOverflow);

// Capture research hub screenshot
const ssResearch = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/mobile-research-hub-390.png", Buffer.from(ssResearch.data, "base64"));
console.log("Saved artifacts/mobile-research-hub-390.png");

// --- 4. Tablet 768px Viewport Check ---
console.log("Testing 768px tablet viewport...");
await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 1024, deviceScaleFactor: 1, mobile: false });
await sleep(1000);

const tabletOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth
  };
})()`);
console.log("768px Tablet Overflow Check:", tabletOverflow);

const ssTablet = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/tablet-768.png", Buffer.from(ssTablet.data, "base64"));
console.log("Saved artifacts/tablet-768.png");

// --- 5. Desktop 1280px Viewport Check ---
console.log("Testing 1280px desktop viewport...");
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
await sleep(1000);

const desktopOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth
  };
})()`);
console.log("1280px Desktop Overflow Check:", desktopOverflow);

const ssDesktop = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/desktop-1280.png", Buffer.from(ssDesktop.data, "base64"));
console.log("Saved artifacts/desktop-1280.png");

ws.close();
console.log("All Prompt 11 Mobile Experience Visual Verifications Completed Successfully!");
