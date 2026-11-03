import fs from "node:fs";

console.log("=== FINN FINAL END-TO-END QA AUDIT ===");

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

const results = {
  healthcheck: null,
  mobile390Overflow: null,
  briefFeedItems: null,
  askAssistant: null,
  watchAnomalies: null,
  researchModules: null,
  tablet768Overflow: null,
  desktop1280Overflow: null,
  allPassed: false
};

// 1. Healthcheck check
console.log("\n[Audit 1/6] Verifying Backend Health & Database Connectivity...");
const health = await fetch("http://127.0.0.1:8000/health").then((r) => r.json());
console.log("Healthcheck:", health);
results.healthcheck = health.status === "ok" && health.database_connected === true;

// 2. Mobile 390px Zero Overflow Audit
console.log("\n[Audit 2/6] Verifying 390px Mobile Viewport Overflow...");
await send("Page.reload", { ignoreCache: true });
await sleep(2500);

await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await sleep(1000);

const mobileOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    zeroOverflow: root.scrollWidth === root.clientWidth
  };
})()`);
console.log("390px Mobile Overflow:", mobileOverflow);
results.mobile390Overflow = mobileOverflow.zeroOverflow;

// 3. Brief Feed & Digest Audit
console.log("\n[Audit 3/6] Verifying Brief Feed Intelligence...");
const briefItemsCount = await evalCode("document.querySelectorAll('.brief-card')?.length");
console.log(`Brief feed items count: ${briefItemsCount}`);
results.briefFeedItems = briefItemsCount > 0;

// 4. Ask AI Query Audit
console.log("\n[Audit 4/6] Verifying Ask AI Grounded Assistant...");
await evalCode("document.getElementById('ask')?.scrollIntoView({ block: 'start' })");
await sleep(800);
await evalCode(`(() => {
  const chip = document.querySelector('.suggestion-chip');
  if (chip) chip.click();
})()`);
await sleep(2000);
const askAnswersCount = await evalCode("document.querySelectorAll('.asst-bubble')?.length");
const citationPillsCount = await evalCode("document.querySelectorAll('.citation-pill')?.length");
console.log(`Assistant answers: ${askAnswersCount}, Primary citations: ${citationPillsCount}`);
results.askAssistant = askAnswersCount > 0 && citationPillsCount > 0;

// 5. Watch & Anomaly Scanner Audit
console.log("\n[Audit 5/6] Verifying Watch Surveillance & Anomaly Scanner...");
await evalCode("document.getElementById('watch')?.scrollIntoView({ block: 'start' })");
await sleep(800);
const watchCards = await evalCode("document.querySelectorAll('.watchlist-item-card')?.length");
const anomaliesList = await evalCode("document.querySelectorAll('.anomaly-card')?.length");
console.log(`Watchlist companies: ${watchCards}, Detected anomalies: ${anomaliesList}`);
results.watchAnomalies = watchCards === 4 && anomaliesList > 0;

// 6. Research Hub Sub-Modules Audit
console.log("\n[Audit 6/6] Verifying Research Hub Sub-Modules...");
await evalCode("document.getElementById('research-hub')?.scrollIntoView({ block: 'start' })");
await sleep(800);
const subtabs = await evalCode("document.querySelectorAll('.research-subtab-btn')?.length");
console.log(`Research subtabs count: ${subtabs}`);
results.researchModules = subtabs >= 6;

// Final Responsiveness checks
await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 1024, deviceScaleFactor: 1, mobile: false });
await sleep(500);
const tabletCheck = await evalCode("document.documentElement.scrollWidth <= document.documentElement.clientWidth");
results.tablet768Overflow = tabletCheck;

await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
await sleep(500);
const desktopCheck = await evalCode("document.documentElement.scrollWidth <= document.documentElement.clientWidth");
results.desktop1280Overflow = desktopCheck;

results.allPassed = Object.entries(results).every(([k, v]) => k === "allPassed" || v === true);

console.log("\n==========================================");
console.log("FINAL END-TO-END QA AUDIT RESULTS:");
console.log(JSON.stringify(results, null, 2));
console.log("==========================================");

fs.writeFileSync("artifacts/final-qa-results.json", JSON.stringify(results, null, 2));
ws.close();
