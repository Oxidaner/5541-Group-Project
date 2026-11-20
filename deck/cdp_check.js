// CDP geometry check for all slides via headless shell + Node WebSocket
const { spawn } = require('child_process');

const HS = "/Users/oxidaner/Library/Caches/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const PORT = 9333;
const browser = spawn(HS, ["--no-sandbox","--disable-gpu","--headless","--remote-debugging-port="+PORT,"--user-data-dir=/Users/oxidaner/polyu/project/5541/tmp/hs-cdp","--window-size=1920,1080","about:blank"], {stdio:"ignore"});

function sleep(ms){return new Promise(r=>setTimeout(r,ms));}

async function waitForDebugger(){
  for(let i=0;i<40;i++){
    try{ const r = await fetch("http://127.0.0.1:"+PORT+"/json/version"); if(r.ok) return; }catch(e){}
    await sleep(250);
  }
  throw new Error("debugger not ready");
}

async function newPage(url){
  const r = await fetch("http://127.0.0.1:"+PORT+"/json/new?"+encodeURIComponent(url), {method:"PUT"});
  return await r.json();
}

function evaluate(wsUrl, expression){
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 1;
    ws.onopen = () => ws.send(JSON.stringify({id, method:"Runtime.evaluate", params:{expression, returnByValue:true}}));
    ws.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if(m.id === id){ ws.close(); resolve(m.result?.result?.value); }
    };
    ws.onerror = reject;
  });
}

const EXPR = `(() => {
  const out = { scrollW: document.documentElement.scrollWidth, scrollH: document.documentElement.scrollHeight,
                innerW: innerWidth, innerH: innerHeight, overflow: [], textOverflow: [] };
  const allowOffscreen = new Set(['glowc','glowm','bg','glyph','ghost']);
  document.querySelectorAll('*').forEach(el => {
    const r = el.getBoundingClientRect();
    if (allowOffscreen.has(el.className && el.className.baseVal !== undefined ? el.className.baseVal : (typeof el.className === 'string' ? el.className : ''))) return;
    if (r.right > 1921 || r.bottom > 1081 || r.left < -1 || r.top < -1) {
      out.overflow.push({ tag: el.tagName, cls: (typeof el.className === 'string' ? el.className : '').slice(0,40), rect: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] });
    }
    // text overflow: element with text whose scrollWidth > clientWidth
    if (el.children.length === 0 && el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0) {
      out.textOverflow.push({ tag: el.tagName, cls: (typeof el.className === 'string' ? el.className : '').slice(0,40), sw: el.scrollWidth, cw: el.clientWidth, text: (el.textContent||'').slice(0,40) });
    }
  });
  return out;
})()`;

(async () => {
  await waitForDebugger();
  for (let i=1;i<=13;i++){
    const url = "file:///Users/oxidaner/polyu/project/5541/deck/slide-" + String(i).padStart(2,'0') + ".html";
    let page;
    try { page = await newPage(url); } catch(e){ console.log("slide", i, "NEWPAGE_ERR", e.message); continue; }
    await sleep(900); // let fonts/layout settle
    let res;
    try { res = await evaluate(page.webSocketDebuggerUrl, EXPR); } catch(e){ console.log("slide", i, "EVAL_ERR", e.message); continue; }
    const problems = (res.overflow || []).length + (res.textOverflow || []).length;
    console.log("slide", i, "scroll=" + res.scrollW + "x" + res.scrollH, "problems=" + problems);
    for (const o of (res.overflow||[]).slice(0,6)) console.log("   OUT", JSON.stringify(o));
    for (const t of (res.textOverflow||[]).slice(0,8)) console.log("   TXT", JSON.stringify(t));
    try { await fetch("http://127.0.0.1:"+PORT+"/json/close/"+page.id); } catch(e){}
  }
  browser.kill();
})();
