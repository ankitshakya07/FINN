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

await send("Emulation.setDeviceMetricsOverride", {
  width: 390,
  height: 844,
  deviceScaleFactor: 1,
  mobile: true,
});

const culprits = await send("Runtime.evaluate", {
  expression: `(() => {
    const cw = document.documentElement.clientWidth;
    const overflowing = [];
    for (const el of document.querySelectorAll('*')) {
      const rect = el.getBoundingClientRect();
      if (rect.right > cw + 1) {
        overflowing.push({
          tag: el.tagName,
          id: el.id,
          class: String(el.className),
          right: Math.round(rect.right),
          width: Math.round(rect.width)
        });
      }
    }
    return overflowing;
  })()`,
  returnByValue: true,
});

console.log("Overflowing elements count:", culprits.result.value.length);
console.log("Top culprits:", JSON.stringify(culprits.result.value.slice(0, 10), null, 2));

ws.close();
