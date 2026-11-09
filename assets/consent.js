/* Google Analytics (GA4) — loaded only after the visitor accepts cookies.
   The choice is remembered; "Cookies" in the footer lets visitors change it. */
(function () {
  var ID = 'G-0F2QH31JZW', KEY = 'df-consent';
  var T = {
    en: { t: 'This site uses cookies for anonymous visit statistics.', a: 'Accept', d: 'Decline' },
    sl: { t: 'Stran uporablja piškotke za anonimno statistiko obiskov.', a: 'Sprejmi', d: 'Zavrni' }
  };
  var get = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  var set = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };

  function load() {
    if (window.__dfGA) return; window.__dfGA = 1;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', ID, { anonymize_ip: true });
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
    document.head.appendChild(s);
  }

  var css = '.cc{position:fixed;left:var(--pad,24px);bottom:var(--pad,24px);z-index:94;max-width:340px;background:var(--ink);color:var(--bone);' +
    'border:1px solid var(--line);padding:16px 18px;font-family:var(--mono,monospace);font-size:11px;letter-spacing:.06em;line-height:1.6;' +
    'opacity:0;transform:translateY(12px);transition:opacity .6s,transform .8s cubic-bezier(.16,1,.3,1)}' +
    '.cc.in{opacity:1;transform:none}.cc p{margin:0 0 12px;text-transform:none}' +
    '.cc .b{display:flex;gap:8px}.cc button{font:inherit;text-transform:uppercase;letter-spacing:.08em;border:1px solid var(--bone);border-radius:99px;padding:8px 14px;cursor:pointer;background:none;color:var(--bone);transition:background .3s,color .3s}' +
    '.cc button.y{background:var(--bone);color:var(--ink)}.cc button:hover{background:var(--bone);color:var(--ink)}' +
    '@media(max-width:720px){.cc{left:12px;right:12px;bottom:12px;max-width:none}}';

  var box = null;
  function text() {
    if (!box) return;
    var L = T[document.documentElement.lang === 'sl' ? 'sl' : 'en'];
    box.querySelector('p').textContent = L.t;
    box.querySelector('.y').textContent = L.a;
    box.querySelector('.n').textContent = L.d;
  }
  function close(v) {
    set(v); if (v === 'yes') load();
    if (box) { box.classList.remove('in'); var b = box; box = null; setTimeout(function () { b.remove(); }, 700); }
  }
  function show(delay) {
    if (box) return;
    if (!document.getElementById('cc-css')) { var st = document.createElement('style'); st.id = 'cc-css'; st.textContent = css; document.head.appendChild(st); }
    box = document.createElement('div'); box.className = 'cc'; box.setAttribute('role', 'dialog');
    box.innerHTML = '<p></p><div class="b"><button class="y" type="button"></button><button class="n" type="button"></button></div>';
    box.querySelector('.y').onclick = function () { close('yes'); };
    box.querySelector('.n').onclick = function () { close('no'); };
    document.body.appendChild(box); text();
    setTimeout(function () { box && box.classList.add('in'); }, delay || 50);
  }
  new MutationObserver(text).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });

  window.dfCookies = function () { show(50); };
  var c = get();
  if (c === 'yes') load();
  if (!c) {
    var go = function () { show(document.getElementById('loader') ? 2600 : 900); };
    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', go) : go();
  }
})();
