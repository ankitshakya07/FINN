const pages = await fetch("http://127.0.0.1:9222/json/list").then((r) => r.json());
let target = pages.find((x) => x.type === "page" && x.url.includes("localhost:3000"));

if (!target) {
  console.log("No tab found on port 9222");
  process.exit(0);
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

console.log("Reloading page in Chrome...");
await send("Page.reload", { ignoreCache: true });
await new Promise((r) => setTimeout(r, 3000));

const status = await evalCode(`(() => {
  const cards = document.querySelectorAll('.brief-card').length;
  const watchCards = document.querySelectorAll('.watchlist-item-card').length;
  const anomCards = document.querySelectorAll('.anomaly-card').length;
  const resBtns = document.querySelectorAll('.research-module-btn').length;
  const banner = document.querySelector('.module-banner-title')?.textContent;
  const modePill = document.querySelector('.mode-pill')?.textContent;
  const answerMarkdown = document.querySelector('.answer-markdown')?.textContent?.slice(0, 80);
  const briefHeadlines = Array.from(document.querySelectorAll('.brief-card h3')).map(h => h.textContent);
  return { cards, watchCards, anomCards, resBtns, banner, modePill, answerMarkdown, briefHeadlines };
})()`);

console.log("Live UI Status:", status);
ws.close();
