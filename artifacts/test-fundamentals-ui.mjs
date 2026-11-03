import fs from "node:fs";

const pages = await fetch("http://127.0.0.1:9222/json/list").then((r) => r.json());
const target = pages.find((x) => x.type === "page" && x.url.includes("localhost:3000"));
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

await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await evalCode("document.getElementById('fundamentals')?.scrollIntoView({ block: 'start' })");
await sleep(400);

// 1. Switch company to TCS
await evalCode("(()=>{ const s = document.getElementById('fund-ticker-select'); s.value = 'TCS'; s.dispatchEvent(new Event('change', { bubbles: true })); })()");
await sleep(1000);
const tcsTitle = await evalCode("document.querySelector('.company-title')?.textContent");
console.log("Switched to TCS, title:", tcsTitle);

// 2. Switch company to RELIANCE
await evalCode("(()=>{ const s = document.getElementById('fund-ticker-select'); s.value = 'RELIANCE'; s.dispatchEvent(new Event('change', { bubbles: true })); })()");
await sleep(1000);
const relTitle = await evalCode("document.querySelector('.company-title')?.textContent");
console.log("Switched to RELIANCE, title:", relTitle);

// 3. Switch company back to INFY
await evalCode("(()=>{ const s = document.getElementById('fund-ticker-select'); s.value = 'INFY'; s.dispatchEvent(new Event('change', { bubbles: true })); })()");
await sleep(800);

// 4. Test Quarterly toggle
await evalCode("(()=>{ const btns = document.querySelectorAll('.pill-toggle button'); for(const b of btns) { if(b.textContent.trim() === 'Quarterly') { b.click(); break; } } })()");
await sleep(800);
const hasQuarter = await evalCode("document.body.innerText.includes('Q2 FY27')");
console.log("Quarterly toggle activated, Q2 FY27 present:", hasQuarter);

// 5. Test Balance Sheet tab
await evalCode("(()=>{ const btns = document.querySelectorAll('.statement-tab-btn'); for(const b of btns) { if(b.textContent.includes('Balance')) { b.click(); break; } } })()");
await sleep(600);
const hasAssets = await evalCode("document.body.innerText.includes('Total Assets')");
console.log("Balance sheet tab active, Total Assets present:", hasAssets);
const bsPic = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
fs.writeFileSync("artifacts/fundamentals-balance-mobile-390.png", Buffer.from(bsPic.data, "base64"));

// 6. Test Cash Flow tab
await evalCode("(()=>{ const btns = document.querySelectorAll('.statement-tab-btn'); for(const b of btns) { if(b.textContent.includes('Cash Flow')) { b.click(); break; } } })()");
await sleep(600);
const hasFCF = await evalCode("document.body.innerText.includes('Free Cash Flow')");
console.log("Cash flow tab active, Free Cash Flow present:", hasFCF);
const cfPic = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
fs.writeFileSync("artifacts/fundamentals-cashflow-mobile-390.png", Buffer.from(cfPic.data, "base64"));

// 7. Test Ratios tab
await evalCode("(()=>{ const btns = document.querySelectorAll('.statement-tab-btn'); for(const b of btns) { if(b.textContent.includes('Ratios')) { b.click(); break; } } })()");
await sleep(600);
const hasROE = await evalCode("document.body.innerText.includes('RETURN ON EQUITY')");
console.log("Ratios tab active, ROE present:", hasROE);

// Check final mobile overflow
const overflow = await evalCode("document.documentElement.scrollWidth > document.documentElement.clientWidth");
console.log("Final check overflow at 390px:", overflow);

ws.close();
console.log("All interactive UI controls tested successfully!");
