(() => {
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE = matchMedia('(pointer: fine)').matches;
const $ = (s, r=document) => r.querySelector(s), $$ = (s, r=document) => [...r.querySelectorAll(s)];

/* ---------- language ---------- */
const T={
  en:{work:'Work',contact:'Contact',back:'All work',next:'Next project',year:'Year',no:'No.',images:'Images',close:'Close',prev:'Prev',nxt:'Next'},
  sl:{work:'Dela',contact:'Kontakt',back:'Vsa dela',next:'Naslednji projekt',year:'Leto',no:'Št.',images:'Slike',close:'Zapri',prev:'Nazaj',nxt:'Naprej'}
};
let LANG=(()=>{ try{ const s=localStorage.getItem('df-lang'); if(s==='sl'||s==='en') return s; }catch(e){}
  return (navigator.language||'').toLowerCase().startsWith('sl')?'sl':'en'; })();
function applyLang(){ document.documentElement.lang=LANG; $$('[data-t]').forEach(e=>{ e.textContent=T[LANG][e.dataset.t]; }); $$('.lang b').forEach(b=>b.classList.toggle('on',b.dataset.l===LANG)); }
applyLang();
$('#lang').addEventListener('click',()=>{ LANG=LANG==='en'?'sl':'en'; try{ localStorage.setItem('df-lang',LANG); }catch(e){} document.body.classList.add('swap'); setTimeout(()=>{ applyLang(); document.body.classList.remove('swap'); },350); });

/* ---------- theme ---------- */
$('#theme').addEventListener('click',()=>{ const t=document.documentElement.dataset.theme==='light'?'dark':'light';
  document.documentElement.dataset.theme=t; try{ localStorage.setItem('df-theme',t); }catch(e){} });

/* ---------- grain ---------- */
(() => { const c=document.createElement('canvas'); c.width=c.height=160; const x=c.getContext('2d'), d=x.createImageData(160,160);
  for(let i=0;i<d.data.length;i+=4){ const v=Math.random()*255; d.data[i]=d.data[i+1]=d.data[i+2]=v; d.data[i+3]=255; }
  x.putImageData(d,0,0); $('#grain').style.backgroundImage=`url(${c.toDataURL()})`; })();

/* ---------- page transitions ---------- */
const curtain=$('#curtain');
try{ if(sessionStorage.getItem('df-zoom')===location.pathname.replace(/\//g,'')){ sessionStorage.removeItem('df-zoom');
  const c=document.body.dataset.cover; if(c){ curtain.style.background=`var(--ink2) center/cover no-repeat url("${c}")`; } } }catch(e){}
function enter(){ requestAnimationFrame(()=>requestAnimationFrame(()=>curtain.classList.add('up'))); }
addEventListener('pageshow',e=>{ if(e.persisted){ curtain.className='curtain up'; } });
document.addEventListener('click',e=>{
  const a=e.target.closest('a[href]'); if(!a||e.metaKey||e.ctrlKey||e.shiftKey||a.target==='_blank') return;
  const u=new URL(a.href,location.href); if(u.origin!==location.origin || (u.pathname===location.pathname && u.hash)) return;
  e.preventDefault(); if(RM){ location.href=u.href; return; }
  curtain.className='curtain cover'; void curtain.offsetWidth; curtain.classList.add('go');
  setTimeout(()=>location.href=u.href,700);
});

/* ---------- cursor ---------- */
if(FINE){
  const cur=$('#cur'), rg=$('#ring'); let cx=innerWidth/2, cy=innerHeight/2, rx=cx, ry=cy;
  addEventListener('pointermove',e=>{ cx=e.clientX; cy=e.clientY; cur.style.transform=`translate(${cx}px,${cy}px)`; });
  (function f(){ rx+=(cx-rx)*.16; ry+=(cy-ry)*.16; rg.style.transform=`translate(${rx}px,${ry}px)`; requestAnimationFrame(f); })();
  document.addEventListener('pointerover',e=>{ const fig=e.target.closest('.p-fig'), lk=e.target.closest('a,button');
    rg.classList.toggle('big',!!fig); rg.classList.toggle('link',!fig&&!!lk); });
}

/* ---------- title split ---------- */
const title=$('.p-title'); const txt=title.textContent; title.innerHTML='';
[...txt].forEach(c=>{ const s=document.createElement('span'); s.className='char'; s.textContent=c===' '?' ':c; title.appendChild(s); });
const chars=$$('.p-title .char');
if(!RM){ chars.forEach(c=>{ c.style.transform='translateY(110%)'; }); }
function intro(){
  chars.forEach((c,i)=>{ c.style.transition=`transform 1.3s cubic-bezier(.16,1,.3,1) ${.25+i*.04}s`; c.style.transform='translateY(0)'; });
  setTimeout(()=>$('.p-cover')&&$('.p-cover').classList.add('in'),550);
}

/* ---------- images: load + reveal ---------- */
const figs=$$('.p-fig');
figs.forEach(f=>{ const im=f.querySelector('img'); const done=()=>f.classList.add('loaded'); if(im.complete&&im.naturalWidth) done(); else { im.addEventListener('load',done); im.addEventListener('error',()=>f.remove()); } });
const io=new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } }),{rootMargin:'0px 0px -8% 0px'});
figs.forEach(f=>io.observe(f));
const cv=$('.p-cover img'); if(cv) cv.addEventListener('error',()=>$('.p-cover').remove());

/* ---------- lightbox ---------- */
const lb=$('#lb'), lbImg=$('#lb img'), lbN=$('#lbN'); let cur=0;
const srcs=figs.map(f=>f.querySelector('img').src);
function show(i){ cur=(i+srcs.length)%srcs.length; lbImg.style.opacity=0; const s=srcs[cur]; const im=new Image(); im.onload=()=>{ lbImg.src=s; lbImg.style.opacity=1; }; im.src=s; lbN.textContent=String(cur+1).padStart(2,'0')+' / '+String(srcs.length).padStart(2,'0'); }
function open(i){ show(i); lb.classList.add('on'); lenis&&lenis.stop(); }
function close(){ lb.classList.remove('on'); lenis&&lenis.start(); }
figs.forEach((f,i)=>f.addEventListener('click',()=>open(srcs.indexOf(f.querySelector('img').src))));
$('#lbX').addEventListener('click',close); $('#lbP').addEventListener('click',()=>show(cur-1)); $('#lbF').addEventListener('click',()=>show(cur+1));
lb.addEventListener('click',e=>{ if(e.target===lb) close(); });
addEventListener('keydown',e=>{ if(!lb.classList.contains('on')) return; if(e.key==='Escape') close(); if(e.key==='ArrowRight') show(cur+1); if(e.key==='ArrowLeft') show(cur-1); });
let tx=null; lb.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});
lb.addEventListener('touchend',e=>{ if(tx===null) return; const d=e.changedTouches[0].clientX-tx; if(Math.abs(d)>50) show(cur+(d<0?1:-1)); tx=null; });

/* ---------- smooth scroll + cover parallax ---------- */
let lenis=null;
if(!RM && typeof Lenis!=='undefined'){ lenis=new Lenis({lerp:.085}); (function raf(t){ lenis.raf(t); requestAnimationFrame(raf); })(performance.now()); }
const cover=$('.p-cover');
if(cover && !RM){ (function par(){ const r=cover.getBoundingClientRect(); const p=Math.max(-1,Math.min(1,(r.top+r.height/2-innerHeight/2)/innerHeight)); cv.style.translate=`0 ${p*-6}%`; requestAnimationFrame(par); })(); }
$$('[data-top]').forEach(a=>a.addEventListener('click',e=>{ e.preventDefault(); lenis?lenis.scrollTo(0,{duration:1.4}):scrollTo({top:0,behavior:'smooth'}); }));

/* preload next project's cover */
const nx=$('.p-next .bg img'); if(nx) nx.loading='eager';

/* ---------- go ---------- */
if(RM){ curtain.className='curtain up'; intro(); }
else { enter(); setTimeout(intro,250); }
})();
