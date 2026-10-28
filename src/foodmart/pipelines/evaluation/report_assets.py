"""Estilos y JavaScript del reporte HTML (tema de supermercado, sin dependencias externas)."""

CSS = """
:root{--bg:#fff8ec;--card:#fffdf8;--ink:#233028;--muted:#66736a;--line:#eadcc2;--green:#1f9d55;
--green2:#14653a;--orange:#ef8a1f;--red:#d6403a;--tag:#ffd23f;--tagink:#3b2a00;--shadow:0 6px 18px rgba(80,60,20,.10);
--soft:color-mix(in srgb,var(--green) 12%,var(--card))}
:root[data-theme=dark]{--bg:#0f1a14;--card:#16231c;--ink:#eaf3ec;--muted:#9db0a3;--line:#27382d;--green:#3ddc84;
--green2:#2ab86a;--orange:#ffa94d;--red:#ff6b63;--tag:#ffd23f;--tagink:#3b2a00;--shadow:0 6px 18px rgba(0,0,0,.35)}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 "Avenir Next","Nunito","Segoe UI",system-ui,sans-serif;
background-image:radial-gradient(color-mix(in srgb,var(--line) 70%,transparent) 1px,transparent 1.5px);background-size:22px 22px}
.ic{flex:none;vertical-align:-4px}
a{color:var(--green2)}code{background:var(--soft);padding:1px 6px;border-radius:6px;font-size:.9em}
#prog{position:fixed;top:0;left:0;right:0;height:5px;z-index:60;background:color-mix(in srgb,var(--line) 60%,transparent)}
#prog i{display:block;height:100%;width:0;background:var(--green)}
#cart{position:fixed;top:-2px;left:0;z-index:61;color:var(--orange);transform:translateX(-50%);transition:left .1s}
nav{position:sticky;top:5px;z-index:50;display:flex;gap:3px;align-items:center;flex-wrap:wrap;padding:8px 10px;margin:0 auto;
max-width:1080px;background:color-mix(in srgb,var(--card) 92%,transparent);backdrop-filter:blur(8px);border:1px solid var(--line);
border-radius:14px;box-shadow:var(--shadow);font-size:14px}
nav a{display:inline-flex;gap:4px;align-items:center;text-decoration:none;color:var(--muted);padding:4px 8px;border-radius:999px;font-size:13px;
transition:.2s}nav a:hover{color:var(--ink);background:var(--soft)}nav a.on{background:var(--green);color:#fff}
nav .sp{flex:1}nav button{cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;
padding:5px 10px;display:inline-flex;gap:6px;align-items:center;font:inherit}
.hero{position:relative;padding:0 16px 8px;text-align:center}
.awning{height:46px;margin:0 -16px;background:repeating-linear-gradient(90deg,var(--green) 0 40px,#fff 40px 80px);position:relative;
box-shadow:0 2px 0 rgba(0,0,0,.06)}
.awning:after{content:"";position:absolute;left:0;right:0;bottom:-14px;height:14px;
background:radial-gradient(circle at 20px 0,var(--green) 20px,transparent 21px) 0 0/80px 14px repeat-x,
radial-gradient(circle at 60px 0,#fff 20px,transparent 21px) 0 0/80px 14px repeat-x}
.hero-in{max-width:1080px;margin:34px auto 0}
.brand{display:inline-flex;gap:10px;align-items:center;font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:14px;
color:#fff;background:var(--green2);padding:7px 16px;border-radius:999px;animation:drop .7s cubic-bezier(.2,1.4,.4,1) both}
h1{font-size:clamp(28px,5vw,46px);line-height:1.1;margin:16px auto 8px;max-width:820px;letter-spacing:-.02em}
h1 em{font-style:normal;color:var(--green)}
.sub{color:var(--muted);margin:0 0 22px}
.tags{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));margin:8px 0 24px}
.ptag{position:relative;background:var(--tag);color:var(--tagink);border-radius:12px 12px 12px 12px;padding:16px 16px 14px 46px;text-align:left;
clip-path:polygon(0 0,calc(100% - 18px) 0,100% 50%,calc(100% - 18px) 100%,0 100%);box-shadow:var(--shadow);transition:transform .25s}
.ptag:hover{transform:rotate(-1.5deg) translateY(-3px)}
.ptag:before{content:"";position:absolute;left:14px;top:50%;width:14px;height:14px;margin-top:-7px;border-radius:50%;background:var(--bg);
box-shadow:inset 0 1px 2px rgba(0,0,0,.35)}
.ptag b{display:block;font-size:36px;line-height:1.05;color:var(--red);font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.ptag span{font-size:13px;line-height:1.3;display:block;font-weight:600}
main{max-width:1080px;margin:0 auto;padding:12px 16px 40px}
.aisle{margin:34px 0;scroll-margin-top:72px}
.sign{display:flex;align-items:center;gap:12px;margin:0 0 14px;flex-wrap:wrap}
.sign .n{background:var(--green2);color:#fff;border-radius:10px;padding:4px 12px;font-weight:800;font-size:13px;letter-spacing:.08em;
text-transform:uppercase;position:relative}
.sign .n:before,.sign .n:after{content:"";position:absolute;top:-10px;width:2px;height:10px;background:var(--muted)}
.sign .n:before{left:16px}.sign .n:after{right:16px}
.sign h2{margin:0;font-size:clamp(22px,3.4vw,30px);display:flex;gap:10px;align-items:center;letter-spacing:-.01em}
.sign h2 .ic{color:var(--green)}
.shelf{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:var(--shadow);position:relative}
.shelf:after{content:"";position:absolute;left:12px;right:12px;bottom:-9px;height:8px;border-radius:0 0 8px 8px;
background:linear-gradient(var(--line),color-mix(in srgb,var(--line) 40%,transparent))}
h3{font-size:17px;margin:20px 0 8px;display:flex;gap:8px;align-items:center}h3 .ic{color:var(--orange)}
.note{color:var(--muted);font-size:14px}ol,ul{padding-left:20px;margin:0}li{margin:7px 0}
.chapin{position:relative;display:flex;gap:12px;align-items:flex-start;margin:16px 0 4px;padding:14px 16px;border-radius:14px;
background:color-mix(in srgb,var(--orange) 14%,var(--card));border:1px dashed var(--orange)}
.chapin .ic{color:var(--orange);margin-top:3px}.chapin b.l{display:block;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--orange)}
.reveal{transition:opacity .7s ease,transform .7s ease}.js .reveal{opacity:0;transform:translateY(22px)}
.js .reveal.in{opacity:1;transform:none}
.grid2{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.cards4{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.mini{border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--card);transition:.25s}
.mini:hover{transform:translateY(-4px);box-shadow:var(--shadow);border-color:var(--green)}
.mini .ic{color:var(--green);margin-bottom:4px}.mini b{display:block}.mini span{color:var(--muted);font-size:14px}
.flow{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
.step{position:relative;border:1px solid var(--line);border-radius:14px;padding:14px 12px;background:var(--card);font-size:14px;transition:.25s}
.step:hover{border-color:var(--green);transform:translateY(-3px)}
.step b{display:flex;gap:6px;align-items:center;margin-bottom:4px;font-size:15px}.step b .ic{color:var(--green)}
.step i{position:absolute;top:-9px;right:10px;background:var(--orange);color:#fff;font-style:normal;font-size:12px;font-weight:800;
width:22px;height:22px;border-radius:50%;display:grid;place-items:center}
details.acc{border:1px solid var(--line);border-radius:14px;margin:12px 0;background:var(--card);overflow:hidden}
details.acc summary{cursor:pointer;list-style:none;padding:13px 16px;font-weight:700;display:flex;gap:10px;align-items:center}
details.acc summary::-webkit-details-marker{display:none}details.acc summary .ic{color:var(--green)}
details.acc summary:after{content:"+";margin-left:auto;font-size:22px;color:var(--muted);transition:.2s}
details.acc[open] summary:after{transform:rotate(45deg)}details.acc[open] summary{background:var(--soft)}
details.acc .bd{padding:6px 18px 16px;animation:rise .4s both}
.find{border-left:4px solid var(--green);padding:3px 0 3px 14px;margin:12px 0}.find.warn{border-color:var(--orange)}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child,.l{text-align:left}th{color:var(--muted);font-weight:600}
tr.final td{font-weight:700;background:var(--soft)}
.tag{display:inline-block;font-size:12px;border-radius:999px;padding:1px 9px;border:1px solid var(--line);color:var(--muted)}
.tag.yes{color:var(--green);border-color:var(--green)}
.bar{display:grid;grid-template-columns:150px 1fr 60px;gap:8px;align-items:center;margin:6px 0;font-size:14px}
.bar .tr{height:11px;border-radius:6px;background:var(--soft);overflow:hidden}
.bar i{display:block;height:100%;width:0;border-radius:6px;background:var(--green);transition:width 1.1s cubic-bezier(.2,.8,.2,1)}
.in .bar i,.bar.in i{width:var(--w)}.bar.neg i{background:var(--red)}.bar.ns i{background:#b9c0b6}
.bar span:last-child{text-align:right;font-variant-numeric:tabular-nums}
.sim{display:grid;gap:22px;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);align-items:center}
@media(max-width:760px){.sim{grid-template-columns:1fr}}
.sim input[type=range]{width:100%;accent-color:var(--green);height:34px}
.rack{display:flex;flex-wrap:wrap;gap:8px;min-height:48px;margin:6px 0 12px}
.rack .ic{color:var(--red);animation:pop .45s cubic-bezier(.2,1.6,.4,1) both}
.rack .me{color:var(--green)}
.big{font-size:clamp(34px,6vw,54px);font-weight:800;letter-spacing:-.02em;line-height:1}
.meter{height:16px;border-radius:9px;background:var(--soft);overflow:hidden;margin:10px 0;position:relative}
.meter i{display:block;height:100%;width:0;border-radius:9px;background:var(--green);transition:width .5s,background .5s}
.meter u{position:absolute;top:-3px;bottom:-3px;width:2px;background:var(--ink);opacity:.55}
.verdict{display:inline-flex;gap:8px;align-items:center;font-weight:800;padding:6px 14px;border-radius:999px;color:#fff;background:var(--green);transition:.4s}
.verdict.low{background:var(--red)}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:3px;background:var(--card);gap:2px;margin:4px 0 10px}
.seg button{cursor:pointer;border:0;background:none;color:var(--muted);padding:6px 16px;border-radius:999px;font:inherit;font-weight:700}
.seg button.on{background:var(--green);color:#fff}
.chk{display:inline-flex;gap:6px;align-items:center;margin-right:14px;font-size:14px;cursor:pointer}.chk input{accent-color:var(--green)}
.mrow{display:grid;grid-template-columns:140px 1fr 70px;gap:10px;align-items:center;margin:9px 0}
.mrow .tr{height:20px;border-radius:10px;background:var(--soft);overflow:hidden}
.mrow i{display:block;height:100%;border-radius:10px;background:#9db7a6;width:0;transition:width .7s cubic-bezier(.2,.8,.2,1)}
.mrow.fin i{background:var(--green)}.mrow.fin{font-weight:800}.mrow span:last-child{text-align:right;font-variant-numeric:tabular-nums}
.cm{display:grid;grid-template-columns:auto 1fr 1fr;gap:8px;max-width:460px}
.cm div{padding:16px 8px;text-align:center;border-radius:12px}
.cm .h{color:var(--muted);font-size:13px;padding:6px;display:flex;align-items:center;justify-content:center}
.cm .c{cursor:pointer;transition:.25s;border:2px solid transparent}.cm .c:hover,.cm .c.on{transform:scale(1.04);border-color:var(--ink)}
.cm .ok{background:color-mix(in srgb,var(--green) 24%,var(--card))}.cm .bad{background:color-mix(in srgb,var(--red) 22%,var(--card))}
.cm .n{display:block;font-size:34px;font-weight:800;line-height:1.1}
#cm-info{margin-top:12px;min-height:3.2em;padding:10px 14px;border-radius:12px;background:var(--soft);font-size:15px}
.ticket{max-width:620px;margin:0 auto;background:#fffef9;color:#2b2b2b;padding:22px 24px 28px;font-family:ui-monospace,"SF Mono",Menlo,monospace;
font-size:14px;box-shadow:var(--shadow);position:relative;border-radius:4px;transform:rotate(-.4deg)}
:root[data-theme=dark] .ticket{background:#f4efe2}
.ticket:before,.ticket:after{content:"";position:absolute;left:0;right:0;height:10px;
background:linear-gradient(-45deg,transparent 7px,#fffef9 0) 0 0/14px 10px,linear-gradient(45deg,transparent 7px,#fffef9 0) 0 0/14px 10px}
:root[data-theme=dark] .ticket:before,:root[data-theme=dark] .ticket:after{filter:brightness(.95)}
.ticket:before{top:-9px;transform:scaleY(-1)}.ticket:after{bottom:-9px}
.t-h{text-align:center;font-weight:800;letter-spacing:.12em;margin-bottom:6px}.t-sep{border-top:2px dashed #aaa;margin:12px 0}
.t-l{display:flex;gap:8px;align-items:baseline;margin:8px 0}.t-l b{flex:1}.t-l .dots{flex:1;border-bottom:2px dotted #bbb;transform:translateY(-4px);min-width:20px}
.t-tot{display:flex;justify-content:space-between;font-size:17px;font-weight:800}
.barcode{height:44px;margin-top:16px;background:repeating-linear-gradient(90deg,#222 0 2px,transparent 2px 4px,#222 4px 5px,transparent 5px 9px,#222 9px 12px,transparent 12px 14px)}
.no li{list-style:none;display:flex;gap:8px;align-items:flex-start}.no .ic{color:var(--red);margin-top:3px}
.stats3{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:10px 0}.stats3 .s{flex:1;min-width:120px;text-align:center;padding:12px;
border-radius:14px;background:var(--soft)}.stats3 .s b{display:block;font-size:28px;line-height:1.1}.stats3 .arrow{color:var(--muted)}
#sc{position:relative}svg text{fill:var(--muted);font-size:11px}svg .ax{stroke:var(--line)}
svg .pt{fill:var(--green);fill-opacity:.45;cursor:pointer;transform-box:fill-box;transform-origin:center;animation:pop .5s both;transition:r .15s}
svg .pt:hover{fill-opacity:1;r:6}svg .mp{fill:var(--orange);stroke:var(--card);stroke-width:2;cursor:pointer}
svg .ln{stroke:var(--ink);stroke-width:2;fill:none;stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:draw 1.6s .5s forwards}
svg .md{stroke:var(--red);stroke-width:2;stroke-dasharray:6 5;fill:none;opacity:.9}
.tip{position:fixed;z-index:80;pointer-events:none;background:var(--ink);color:var(--bg);padding:6px 10px;border-radius:8px;font-size:13px;
opacity:0;transition:opacity .12s;max-width:240px}
footer{text-align:center;color:var(--muted);padding:10px 16px 50px;font-size:14px}
footer .pill{display:inline-flex;gap:8px;align-items:center;margin-top:8px;background:var(--card);border:1px solid var(--line);
padding:6px 14px;border-radius:999px}
@media(max-width:600px){th,td{padding:7px 5px;font-size:13px}.shelf{padding:16px 14px}.bar{grid-template-columns:104px 1fr 48px}
.mrow{grid-template-columns:104px 1fr 58px}.ptag b{font-size:30px}
nav{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}nav a{white-space:nowrap}nav .sp{display:none}
.t-l .dots{display:none}.t-l{justify-content:space-between}.ticket{padding:20px 16px 26px}}
#fs .ic:last-child,html.fs #fs .ic:first-child{display:none}html.fs #fs .ic:last-child{display:inline}
html:fullscreen{background:var(--bg);overflow:auto}html.fs body{font-size:18px}html.fs .shelf{padding:28px}
@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes drop{from{opacity:0;transform:translateY(-30px)}to{opacity:1;transform:none}}
@keyframes draw{to{stroke-dashoffset:0}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}
.js .reveal{opacity:1;transform:none}svg .ln{stroke-dashoffset:0}.bar i{width:var(--w)}}
@media print{nav,#prog,#cart{display:none}.js .reveal{opacity:1;transform:none}.bar i{width:var(--w)}details.acc{break-inside:avoid}}
"""

JS = """
const D = JSON.parse(document.getElementById('data').textContent);
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fmt = (v, d = 2) => v.toLocaleString('es-GT', {minimumFractionDigits: d, maximumFractionDigits: d});

/* Tema claro/oscuro */
const theme = t => { document.documentElement.dataset.theme = t; try { localStorage.setItem('fm-theme', t); } catch (e) {} };
$('#theme').onclick = () => theme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');

/* Carrito de progreso */
const prog = () => {
  const h = document.documentElement, p = Math.min(1, h.scrollTop / Math.max(1, h.scrollHeight - innerHeight));
  $('#prog i').style.width = p * 100 + '%'; $('#cart').style.left = p * 100 + '%';
};
addEventListener('scroll', prog, {passive: true}); prog();

/* Aparición al hacer scroll, contadores y barras */
const count = el => {
  const to = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0), pre = el.dataset.pre || '', suf = el.dataset.suf || '';
  if (calm) { el.textContent = pre + fmt(to, dec) + suf; return; }
  const t0 = performance.now();
  const step = t => { const k = Math.min(1, (t - t0) / 1300), e = 1 - Math.pow(1 - k, 3);
    el.textContent = pre + fmt(to * e, dec) + suf; if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
};
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) {
  e.target.classList.add('in'); $$('[data-count]', e.target).forEach(count);
  if (e.target.dataset.count) count(e.target); io.unobserve(e.target); } }), {threshold: 0, rootMargin: '0px 0px -8% 0px'});
$$('.reveal, .bar, .ptag').forEach(el => io.observe(el));

/* Pasillo activo en el menú */
const spy = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting)
  $$('nav a').forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id)); }),
  {rootMargin: '-45% 0px -50% 0px'});
$$('.aisle').forEach(s => spy.observe(s));

/* Tooltip genérico */
const tip = $('#tip');
const showTip = (html, x, y) => { tip.innerHTML = html; tip.style.opacity = 1;
  tip.style.left = Math.min(innerWidth - 250, x + 14) + 'px'; tip.style.top = y + 14 + 'px'; };
const hideTip = () => tip.style.opacity = 0;
document.addEventListener('mousemove', e => { const t = e.target.closest('[data-tip]');
  t ? showTip(t.dataset.tip, e.clientX, e.clientY) : hideTip(); });

/* Calculadora de ubicación */
(() => {
  const s = $('#sim'), c = D.comp, store = $('#tpl-store').innerHTML, thr = D.thr;
  const ymax = Math.max(...c.groups.map(g => g.mean)) * 1.05;
  const run = () => {
    const n = +s.value, u = Math.max(0, c.intercept + c.slope * n);
    $('#sim-n').textContent = n;
    $('#sim-u').textContent = '$' + fmt(u * 1000, 0) + ' mil';
    $('#sim-rack').innerHTML = '<span class="me" data-tip="Tu tienda">' + store.replace('class="ic', 'class="ic me') + '</span>' +
      Array.from({length: n}, (_, i) => '<span style="animation-delay:' + i * 60 + 'ms" data-tip="Competidor ' + (i + 1) + '">' + store + '</span>').join('');
    const m = $('#sim-m'); m.style.width = Math.min(100, u / ymax * 100) + '%';
    const v = $('#sim-v'), good = u >= thr; v.classList.toggle('low', !good);
    v.querySelector('span').textContent = good ? 'Pinta chilero: utilidad alta' : 'Se ve difícil: utilidad baja';
    m.style.background = good ? 'var(--green)' : 'var(--red)';
    const g = c.groups.find(x => x.n_comp === n);
    $('#sim-real').textContent = g ? 'En los datos hubo ' + g.stores + ' tiendas con ' + n + ' competidor' + (n === 1 ? '' : 'es') +
      ' y ganaron en promedio $' + fmt(g.mean * 1000, 0) + ' mil.' : 'No hay tiendas con ese número de competidores en los datos.';
  };
  s.max = Math.max(...c.groups.map(g => g.n_comp)); s.addEventListener('input', run); run();
  $('#sim-thr').style.left = Math.min(100, thr / ymax * 100) + '%';
})();

/* Dispersión interactiva */
(() => {
  const c = D.comp, W = 640, H = 340, ml = 48, mb = 38, mt = 12, mr = 14, host = $('#sc');
  const xmax = Math.max(...c.groups.map(g => g.n_comp)) + .6, ymax = Math.ceil(Math.max(...c.points.map(p => p[1])) * 2) / 2;
  const sx = v => ml + v / xmax * (W - ml - mr), sy = v => H - mb - v / ymax * (H - mb - mt);
  let s = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Utilidad por número de competidores">';
  for (let i = 0; i <= ymax * 2; i++) s += '<line class="ax" x1="' + ml + '" x2="' + (W - mr) + '" y1="' + sy(i / 2) + '" y2="' + sy(i / 2) +
    '"/><text x="' + (ml - 7) + '" y="' + (sy(i / 2) + 4) + '" text-anchor="end">' + (i / 2).toFixed(1) + '</text>';
  for (let i = 0; i < xmax; i++) s += '<text x="' + sx(i) + '" y="' + (H - mb + 17) + '" text-anchor="middle">' + i + '</text>';
  s += '<g id="g-pts">' + c.points.map((p, i) => { const j = (((i * 37) % 100) / 100 - .5) * .3;
    return '<circle class="pt" r="4" cx="' + sx(p[0] + j).toFixed(1) + '" cy="' + sy(p[1]).toFixed(1) + '" style="animation-delay:' + (i * 8) +
      'ms" data-tip="Tienda con <b>' + p[0] + '</b> competidor' + (p[0] === 1 ? '' : 'es') + '<br>Utilidad: <b>$' + fmt(p[1], 2) + 'M</b>"/>'; }).join('') + '</g>';
  const pts = c.groups.map(g => sx(g.n_comp).toFixed(1) + ',' + sy(g.mean).toFixed(1)).join(' ');
  s += '<g id="g-avg"><polyline class="ln" style="--len:900" points="' + pts + '"/>' + c.groups.map(g => '<circle class="mp" r="6" cx="' + sx(g.n_comp).toFixed(1) +
    '" cy="' + sy(g.mean).toFixed(1) + '" data-tip="<b>' + g.n_comp + '</b> competidores · ' + g.stores + ' tiendas<br>Promedio: <b>$' + fmt(g.mean, 2) + 'M</b>"/>').join('') + '</g>';
  s += '<g id="g-mod"><line class="md" x1="' + sx(0) + '" y1="' + sy(c.intercept) + '" x2="' + sx(xmax - .6) + '" y2="' + sy(c.intercept + c.slope * (xmax - .6)) + '"/></g>';
  s += '<text x="' + (W / 2) + '" y="' + (H - 3) + '" text-anchor="middle">Número de competidores</text><text transform="rotate(-90)" x="' + (-H / 2) +
    '" y="13" text-anchor="middle">Utilidad bruta ($ millones)</text></svg>';
  host.innerHTML = s;
  [['#c-pts', '#g-pts'], ['#c-avg', '#g-avg'], ['#c-mod', '#g-mod']].forEach(([i, g]) =>
    $(i).addEventListener('change', e => $(g).style.display = e.target.checked ? '' : 'none'));
})();

/* Métricas de los modelos (validación cruzada o prueba) */
(() => {
  const host = $('#mbars'), note = $('#mnote'), info = {
    MAE: ['Error absoluto promedio en $ millones: <b>menor es mejor</b>.', false],
    RMSE: ['Raíz del error cuadrático medio ($ millones): castiga más los errores grandes. <b>Menor es mejor</b>.', false],
    R2: ['Qué parte de la variación explica el modelo: <b>mayor es mejor</b>; 0 equivale a predecir la media.', true]};
  let src = 'cv', met = 'MAE';
  const draw = () => {
    const data = D[src === 'cv' ? 'cv' : 'metrics'], [txt, up] = info[met], vals = data.map(m => m[met]);
    const top = Math.max(...vals.map(v => Math.max(v, 0)), 1e-9), best = up ? Math.max(...vals) : Math.min(...vals);
    note.innerHTML = txt;
    host.innerHTML = data.map(m => '<div class="mrow' + (m.modelo === D.final ? ' fin' : '') + '"><span>' + m.modelo + (m[met] === best ? ' ★' : '') +
      '</span><div class="tr"><i data-w="' + Math.max(m[met], 0) / top * 100 + '"></i></div><span>' + fmt(m[met], 3) + '</span></div>').join('');
    requestAnimationFrame(() => requestAnimationFrame(() => $$('#mbars i').forEach(i => i.style.width = i.dataset.w + '%')));
  };
  const wire = (id, set) => $$(id + ' button').forEach(b => b.onclick = () => { $$(id + ' button').forEach(x => x.classList.toggle('on', x === b)); set(b); draw(); });
  wire('#mseg', b => met = b.dataset.m); wire('#msrc', b => src = b.dataset.s); draw();
})();

/* Pantalla completa y modo presentación */
(() => {
  const b = $('#fs'), root = document.documentElement;
  if (!root.requestFullscreen) { b.style.display = 'none'; return; }
  const toggle = () => document.fullscreenElement ? document.exitFullscreen() : root.requestFullscreen().catch(() => {});
  b.onclick = toggle;
  document.addEventListener('fullscreenchange', () => root.classList.toggle('fs', !!document.fullscreenElement));
  document.addEventListener('keydown', e => {
    if (e.target.matches('input, textarea') || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === 'f' || e.key === 'F') { toggle(); return; }
    if (document.fullscreenElement && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
      const as = $$('.aisle'); let cur = -1;
      as.forEach((a, i) => { if (a.getBoundingClientRect().top <= 120) cur = i; });
      const next = cur + (e.key === 'ArrowRight' ? 1 : -1);
      next < 0 ? scrollTo({top: 0}) : as[Math.min(as.length - 1, next)].scrollIntoView({block: 'start'});
      e.preventDefault();
    }
  });
})();

/* Matriz de confusión */
$$('.cm .c').forEach(c => { const go = () => { $$('.cm .c').forEach(x => x.classList.toggle('on', x === c)); $('#cm-info').innerHTML = c.dataset.info; };
  c.addEventListener('click', go); c.addEventListener('mouseenter', go); c.addEventListener('keydown', e => e.key === 'Enter' && go()); });
"""
