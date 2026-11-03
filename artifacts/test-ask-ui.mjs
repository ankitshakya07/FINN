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

await evalCode("document.getElementById('ask')?.scrollIntoView({ block: 'start' })");
await sleep(1000);

const overflowCheck = await evalCode(`(() => {
  const root = document.documentElement;
  const section = document.getElementById('ask');
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth,
    sectionScrollWidth: section?.scrollWidth,
    sectionClientWidth: section?.clientWidth
  };
})()`);

console.log("390px Mobile Overflow Check:", overflowCheck);

const initialSuggestions = await evalCode("document.querySelectorAll('.suggestion-chip')?.length");
console.log(`Suggested Prompts count: ${initialSuggestions}`);

// Capture empty state at 390px
const ssEmpty = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/ask-mobile-390.png", Buffer.from(ssEmpty.data, "base64"));
console.log("Saved artifacts/ask-mobile-390.png");

// --- 2. Click on a suggested inquiry ---
console.log("Clicking first suggestion chip...");
await evalCode(`(() => {
  const chip = document.querySelector('.suggestion-chip');
  if (chip) chip.click();
})()`);

// Wait for response to arrive
await sleep(2000);

const messagesCount = await evalCode("document.querySelectorAll('.chat-message-row')?.length");
const firstAnswer = await evalCode("document.querySelector('.asst-bubble .bubble-content')?.textContent?.slice(0, 100)");
const citationsCount = await evalCode("document.querySelectorAll('.citation-pill')?.length");
const followupsCount = await evalCode("document.querySelectorAll('.followup-btn')?.length");

console.log(`Messages count: ${messagesCount}`);
console.log(`Assistant answer excerpt: ${firstAnswer}`);
console.log(`Citations count: ${citationsCount}, Follow-ups count: ${followupsCount}`);

// --- 3. Click citation pill to inspect verbatim primary source ---
console.log("Clicking primary source citation pill...");
await evalCode(`(() => {
  const cit = document.querySelector('.citation-pill');
  if (cit) cit.click();
})()`);
await sleep(600);

const inspectorDoc = await evalCode("document.querySelector('.inspector-doc')?.textContent");
const inspectorQuote = await evalCode("document.querySelector('.inspector-quote')?.textContent?.slice(0, 80)");
console.log(`Citation Inspector: doc="${inspectorDoc}", quote="${inspectorQuote}"`);

// --- 4. Click follow-up question ---
console.log("Clicking follow-up question...");
await evalCode(`(() => {
  const fBtn = document.querySelector('.followup-btn');
  if (fBtn) fBtn.click();
})()`);
await sleep(2000);

const updatedMessagesCount = await evalCode("document.querySelectorAll('.chat-message-row')?.length");
console.log(`Multi-turn Messages count: ${updatedMessagesCount}`);

// Check overflow again after conversation is rendered
const postChatOverflow = await evalCode(`(() => {
  const root = document.documentElement;
  return {
    clientWidth: root.clientWidth,
    scrollWidth: root.scrollWidth,
    hasOverflow: root.scrollWidth > root.clientWidth
  };
})()`);
console.log("Post-chat 390px Overflow Check:", postChatOverflow);

// Capture conversation at 390px
const ssConvo = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/ask-conversation-mobile-390.png", Buffer.from(ssConvo.data, "base64"));
console.log("Saved artifacts/ask-conversation-mobile-390.png");

// --- 5. Tablet 768px Viewport Check ---
await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 1024, deviceScaleFactor: 1, mobile: false });
await sleep(800);
await evalCode("document.getElementById('ask')?.scrollIntoView({ block: 'start' })");
await sleep(500);
const ssTablet = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/ask-tablet-768.png", Buffer.from(ssTablet.data, "base64"));
console.log("Saved artifacts/ask-tablet-768.png");

// --- 6. Desktop 1280px Viewport Check ---
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
await sleep(800);
await evalCode("document.getElementById('ask')?.scrollIntoView({ block: 'start' })");
await sleep(500);
const ssDesktop = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync("artifacts/ask-desktop.png", Buffer.from(ssDesktop.data, "base64"));
console.log("Saved artifacts/ask-desktop.png");

ws.close();
console.log("Ask AI UI Visual Verification Complete!");
