import fs from "node:fs";

const pages = await fetch("http://127.0.0.1:9222/json/list").then((r) => r.json());
let target = pages.find((x) => x.type === "page" && x.url.includes("localhost:3000"));

if (!target) {
  // If not open, open a new tab
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

console.log("Navigating/reloading page...");
await send("Page.reload", { ignoreCache: true });
await sleep(2500);

// --- 1. Mobile 390px Viewport Check ---
await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await sleep(800);

await evalCode("document.getElementById('promised-delivered')?.scrollIntoView({ block: 'start' })");
await sleep(800);

const overflowCheck = await evalCode(`(() => {
  const root = document.documentElement;
  const section = document.getElementById('promised-delivered');
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth,
    sectionScrollWidth: section?.scrollWidth,
    sectionClientWidth: section?.clientWidth
  };
})()`);

console.log("390px Mobile Overflow Check:", overflowCheck);

// Verify score and cards for INFY
const infyScore = await evalCode("document.querySelector('.score-number')?.textContent");
const infyCards = await evalCode("document.querySelectorAll('.commitment-card')?.length");
console.log(`INFY delivery score: ${infyScore}, commitment cards: ${infyCards}`);

// --- 2. Switch to TCS ---
console.log("Switching to TCS...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.ticker-selector-scroll button'));
  const tcsBtn = btns.find(b => b.textContent.includes('TCS'));
  if (tcsBtn) tcsBtn.click();
})()`);
await sleep(1000);

const tcsScore = await evalCode("document.querySelector('.score-number')?.textContent");
const tcsCompany = await evalCode("document.querySelector('.scorecard-co')?.textContent");
const tcsCards = await evalCode("document.querySelectorAll('.commitment-card')?.length");
console.log(`TCS loaded: ${tcsCompany}, score: ${tcsScore}, cards: ${tcsCards}`);

// --- 3. Switch to RELIANCE ---
console.log("Switching to RELIANCE...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.ticker-selector-scroll button'));
  const relBtn = btns.find(b => b.textContent.includes('RELIANCE'));
  if (relBtn) relBtn.click();
})()`);
await sleep(1000);

const relScore = await evalCode("document.querySelector('.score-number')?.textContent");
const relCompany = await evalCode("document.querySelector('.scorecard-co')?.textContent");
console.log(`RELIANCE loaded: ${relCompany}, score: ${relScore}`);

// --- 4. Switch back to INFY and test filtering ---
console.log("Switching back to INFY...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.ticker-selector-scroll button'));
  const infyBtn = btns.find(b => b.textContent.includes('INFY'));
  if (infyBtn) infyBtn.click();
})()`);
await sleep(800);

console.log("Testing Domain filter (operational)...");
await evalCode(`(() => {
  const sel = document.getElementById('commit-category-select');
  if (sel) {
    sel.value = 'operational';
    sel.dispatchEvent(new Event('change', { bubbles: true }));
  }
})()`);
await sleep(800);
const filteredCards = await evalCode("document.querySelectorAll('.commitment-card')?.length");
console.log(`Filtered operational cards: ${filteredCards}`);

// Reset filter
await evalCode(`(() => {
  const sel = document.getElementById('commit-category-select');
  if (sel) {
    sel.value = 'all';
    sel.dispatchEvent(new Event('change', { bubbles: true }));
  }
})()`);
await sleep(600);

// --- 5. Capture Mobile Screenshots ---
await evalCode("document.getElementById('promised-delivered')?.scrollIntoView({ block: 'start' })");
await sleep(500);

const mobileScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/promised-delivered-mobile-390.png", Buffer.from(mobileScreenshot.data, "base64"));
console.log("Saved artifacts/promised-delivered-mobile-390.png");

// Scroll slightly to capture comparative cards in view
await evalCode("window.scrollBy({ top: 350, behavior: 'instant' })");
await sleep(400);
const cardsScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/promised-delivered-card-mobile-390.png", Buffer.from(cardsScreenshot.data, "base64"));
console.log("Saved artifacts/promised-delivered-card-mobile-390.png");

// --- 6. Tablet 768px Viewport ---
await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 1024, deviceScaleFactor: 1, mobile: false });
await evalCode("document.getElementById('promised-delivered')?.scrollIntoView({ block: 'start' })");
await sleep(600);

const tabletScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/promised-delivered-tablet-768.png", Buffer.from(tabletScreenshot.data, "base64"));
console.log("Saved artifacts/promised-delivered-tablet-768.png");

// --- 7. Desktop 1440px Viewport ---
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await evalCode("document.getElementById('promised-delivered')?.scrollIntoView({ block: 'start' })");
await sleep(600);

const desktopScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/promised-delivered-desktop.png", Buffer.from(desktopScreenshot.data, "base64"));
console.log("Saved artifacts/promised-delivered-desktop.png");

ws.close();
console.log("CDP verification completed successfully!");
