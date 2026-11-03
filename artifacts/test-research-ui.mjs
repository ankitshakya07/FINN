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

console.log("Navigating/reloading page...");
await send("Page.reload", { ignoreCache: true });
await sleep(2500);

// --- 1. Mobile 390px Viewport Check ---
await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await sleep(800);

await evalCode("document.getElementById('research')?.scrollIntoView({ block: 'start' })");
await sleep(1000);

const overflowCheck = await evalCode(`(() => {
  const root = document.documentElement;
  const section = document.getElementById('research');
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth,
    sectionScrollWidth: section?.scrollWidth,
    sectionClientWidth: section?.clientWidth
  };
})()`);

console.log("390px Mobile Overflow Check:", overflowCheck);

// Verify module buttons count and initial load
const moduleBtns = await evalCode("document.querySelectorAll('.research-module-btn')?.length");
const activeModuleTitle = await evalCode("document.querySelector('.module-banner-title')?.textContent");
const answerText = await evalCode("document.querySelector('.answer-markdown')?.textContent?.slice(0, 80)");
const findingsCount = await evalCode("document.querySelectorAll('.finding-card')?.length");
const citationsCount = await evalCode("document.querySelectorAll('.citation-card')?.length");

console.log(`Research Modules count: ${moduleBtns}`);
console.log(`Active Module Title: ${activeModuleTitle}`);
console.log(`Answer snippet: ${answerText}`);
console.log(`Findings count: ${findingsCount}, Citations count: ${citationsCount}`);

// --- 2. Switch to Financial Snapshot module ---
console.log("Switching module to Financial Snapshot...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.research-module-btn'));
  const finBtn = btns.find(b => b.textContent.includes('Financial Snapshot'));
  if (finBtn) finBtn.click();
})()`);
await sleep(1200);

const finTitle = await evalCode("document.querySelector('.module-banner-title')?.textContent");
const finAnswer = await evalCode("document.querySelector('.answer-markdown')?.textContent?.slice(0, 80)");
console.log(`Switched module: ${finTitle}, answer: ${finAnswer}`);

// --- 3. Switch company to TCS ---
console.log("Switching company to TCS...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('#research .ticker-selector-scroll button'));
  const tcsBtn = btns.find(b => b.textContent.includes('TCS'));
  if (tcsBtn) tcsBtn.click();
})()`);
await sleep(1200);

const tcsAnswer = await evalCode("document.querySelector('.answer-markdown')?.textContent?.slice(0, 80)");
console.log(`TCS research answer: ${tcsAnswer}`);

// --- 4. Switch back to INFY and Bull vs Bear ---
console.log("Switching back to INFY and Bull vs Bear...");
await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('#research .ticker-selector-scroll button'));
  const infyBtn = btns.find(b => b.textContent.includes('INFY'));
  if (infyBtn) infyBtn.click();
})()`);
await sleep(800);

await evalCode(`(() => {
  const btns = Array.from(document.querySelectorAll('.research-module-btn'));
  const bvbBtn = btns.find(b => b.textContent.includes('Bull vs. Bear'));
  if (bvbBtn) bvbBtn.click();
})()`);
await sleep(1000);

// --- 5. Capture Mobile Screenshots ---
await evalCode("document.getElementById('research')?.scrollIntoView({ block: 'start' })");
await sleep(500);

const mobileScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/research-mobile-390.png", Buffer.from(mobileScreenshot.data, "base64"));
console.log("Saved artifacts/research-mobile-390.png");

// Scroll down to capture Findings and Citations
await evalCode("window.scrollBy({ top: 400, behavior: 'instant' })");
await sleep(400);

const findingsScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/research-findings-mobile-390.png", Buffer.from(findingsScreenshot.data, "base64"));
console.log("Saved artifacts/research-findings-mobile-390.png");

// --- 6. Tablet 768px Viewport ---
await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 1024, deviceScaleFactor: 1, mobile: false });
await evalCode("document.getElementById('research')?.scrollIntoView({ block: 'start' })");
await sleep(600);

const tabletScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/research-tablet-768.png", Buffer.from(tabletScreenshot.data, "base64"));
console.log("Saved artifacts/research-tablet-768.png");

// --- 7. Desktop 1440px Viewport ---
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await evalCode("document.getElementById('research')?.scrollIntoView({ block: 'start' })");
await sleep(600);

const desktopScreenshot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/research-desktop.png", Buffer.from(desktopScreenshot.data, "base64"));
console.log("Saved artifacts/research-desktop.png");

ws.close();
console.log("Research CDP verification completed successfully!");
