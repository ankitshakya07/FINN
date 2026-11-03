const pages = await fetch('http://127.0.0.1:9222/json/list').then(r => r.json());
const target = pages.find(x => x.type === 'page' && x.url.includes('localhost:3000'));
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));
let id = 0;
const send = (method, params = {}) => new Promise(res => {
  const cId = ++id;
  const handler = (e) => {
    const m = JSON.parse(e.data);
    if (m.id === cId) { ws.removeEventListener('message', handler); res(m.result); }
  };
  ws.addEventListener('message', handler);
  ws.send(JSON.stringify({ id: cId, method, params }));
});
const evalCode = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  return r.result?.value;
};
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

await send('Page.reload', { ignoreCache: true });
await sleep(2500);

const ids = await evalCode('Array.from(document.querySelectorAll("[id]")).map(el => el.id)');
console.log('All IDs found after hard reload:', ids);
const hasSection = await evalCode('!!document.getElementById("promised-delivered")');
console.log('promised-delivered section present:', hasSection);
ws.close();
