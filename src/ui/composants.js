/* ---------- Composants partagés ---------- */
const slugG = s => norm(String(s).replace(/œ/g,'oe').replace(/Œ/g,'Oe').replace(/æ/g,'ae')).replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const groupPath = g => '/groupes/'+slugG(g.short);
function searchDeps(q){
  q=norm(q.trim()); if(q.length<2) return null;
  const terms=q.split(/\s+/);
  return deps.filter(d=> /^\d+[ab]?$/.test(q)? d.nd.toLowerCase()===q.padStart(2,'0') : terms.every(t=>d.key.includes(t)));
}
/* Codes postaux et communes (/cp.json, chargé à la demande) */
let CPDATA=null, cpPromise=null, COMMUNES=null;
function loadCP(){
  if(!cpPromise) cpPromise=fetch('/cp.json').then(r=>{ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
    .then(j=>{ CPDATA=j; COMMUNES=[]; Object.entries(j).forEach(([cp,L])=>L.forEach(([nom,cs])=>COMMUNES.push({k:norm(nom), nom, cp, cs}))); return j; })
    .catch(e=>{ console.warn('Codes postaux indisponibles :', e.message); cpPromise=null; return null; });
  return cpPromise;
}
const OUTREMER={ZA:'971',ZB:'972',ZC:'973',ZD:'974',ZM:'976',ZN:'988',ZP:'987',ZS:'975',ZW:'986',ZX:'977',ZZ:'099'};
function circoKey(code){ const d=code.slice(0,2); return [OUTREMER[d]||d, +code.slice(2)]; }
const BY_CIRCO={}, DEP_NAME={}; deps.forEach(d=>{ BY_CIRCO[d.nd+'-'+(+d.ci)]=d; DEP_NAME[d.nd]=d.dep; });
function circoLabel(code){ const [nd,ci]=circoKey(code); const dn=DEP_NAME[nd]; return `${ci}${ci===1?'re':'e'} circonscription ${dn?deDep(dn):'('+nd+')'}`; }
function placeItems(list){ // [{nom, cs}] -> [{nom, code, d}]
  const out=[]; list.forEach(({nom,cs})=>cs.forEach(code=>{ const [nd,ci]=circoKey(code); out.push({nom, code, d:BY_CIRCO[nd+'-'+ci]||null}); }));
  return out;
}
/* Recherche « Trouver mon député » : nom, n° de département, code postal ou ville */
function searchAll(q, done){
  const t=q.trim();
  if(/^\d{5}$/.test(t)){
    if(!CPDATA){ done({msg:'Recherche…'}); loadCP().then(j=>j||loadCP()).then(j=>done(j? searchSync(t) : {msg:'Recherche par code postal momentanément indisponible. Essayez avec un nom ou un numéro de département.'})); return; }
    done(searchSync(t)); return;
  }
  done(searchSync(t));
  if(!CPDATA && norm(t).length>=3 && !/^\d/.test(t)) loadCP().then(j=>{ if(j) done(searchSync(t)); });
}
function searchSync(t){
  if(/^\d{5}$/.test(t)){
    const L=CPDATA && CPDATA[t];
    if(!L) return {msg:CPDATA?'Aucune commune pour ce code postal.':'Recherche par code postal momentanément indisponible. Essayez avec un nom ou un numéro de département.'};
    // une ligne par circonscription (les communes d'un même code postal sont regroupées)
    const byC={}; placeItems(L.map(([nom,cs])=>({nom,cs}))).forEach(x=>{ (byC[x.code]=byC[x.code]||{code:x.code,d:x.d,noms:[]}).noms.push(x.nom); });
    return {places:Object.values(byC).sort((a,b)=>a.code.localeCompare(b.code)).map(g=>({code:g.code, d:g.d, nom:g.noms.length>2? `Code postal ${t} (${g.noms.length} communes)` : g.noms.join(', ')}))};
  }
  const hits=searchDeps(t);
  if(!hits) return null;
  let places=[];
  const k=norm(t);
  if(COMMUNES && k.length>=3 && !/^\d/.test(k)){
    const seen=new Set();
    places=placeItems(COMMUNES.filter(c=>c.k.startsWith(k) || c.k.includes(' '+k) || c.k.includes('-'+k)).filter(c=>{ const key=c.nom+c.cs; if(seen.has(key)) return false; seen.add(key); return true; }).slice(0,8));
  }
  return {deps:hits.slice(0,40), places};
}
function depLink(d){ return `<a href="/depute/${esc(d.sl)}">${avatar(d)}<span><b>${esc(d.p+' '+d.n)}</b><br><small>${esc(G[d.g]?.short||'')} · ${esc(circo(d))}</small></span></a>`; }
function depButton(d, extra){ return `<button type="button" data-dep="${d.i}">${avatar(d)}<span><b>${esc(d.p+' '+d.n)}</b><br><small>${extra?esc(extra)+' · ':''}${esc(G[d.g]?.short||'')} · ${esc(circo(d))}</small></span></button>`; }
function placeHTML(x, asButton){
  const head=`${esc(x.nom)} · ${esc(circoLabel(x.code))}`;
  if(!x.d) return `<div class="res-vacant"><span><b>${head}</b><br><small>Siège vacant actuellement</small></span></div>`;
  const inner=`${avatar(x.d)}<span><b>${head}</b><br><small>${esc(x.d.p+' '+x.d.n)} (${esc(G[x.d.g]?.short||'non inscrit')})</small></span>`;
  return asButton? `<button type="button" data-dep="${x.d.i}">${inner}</button>` : `<a href="/depute/${esc(x.d.sl)}">${inner}</a>`;
}
function bindSearch(id, opts){
  opts=opts||{};
  const inp=document.getElementById(id), res=document.getElementById(id+'-results');
  if(!inp) return;
  let st=document.getElementById(id+'-status');
  if(!st){ st=document.createElement('p'); st.id=id+'-status'; st.className='sr-only'; st.setAttribute('aria-live','polite'); inp.parentNode.appendChild(st); }
  inp.addEventListener('focus',()=>loadCP(),{once:true});
  inp.addEventListener('input',()=>{
    const q=inp.value;
    searchAll(q, r=>{
      if(inp.value!==q) return;
      if(!r){ res.hidden=true; st.textContent=''; return; }
      if(r.msg){ res.innerHTML=`<div class="note" style="padding:12px">${esc(r.msg)}</div>`; res.hidden=false; st.textContent=r.msg; return; }
      const items=(r.places||[]).map(x=>placeHTML(x,opts.asButton)).concat((r.deps||[]).map(d=>opts.asButton?depButton(d):depLink(d)));
      res.innerHTML = items.length? items.join('') : '<div class="note" style="padding:12px">Aucun député ni aucune commune ne correspond.</div>';
      res.hidden=false;
      st.textContent = items.length? `${items.length} résultat${items.length>1?'s':''}` : 'Aucun résultat';
    });
  });
  inp.addEventListener('keydown',e=>{ if(e.key==='ArrowDown'){ const f=res.querySelector('a,button'); if(f && !res.hidden){ e.preventDefault(); f.focus(); } } });
  res.addEventListener('keydown',e=>{
    const L=[...res.querySelectorAll('a,button')], i=L.indexOf(document.activeElement);
    if(e.key==='ArrowDown' && i<L.length-1){ e.preventDefault(); L[i+1].focus(); }
    if(e.key==='ArrowUp'){ e.preventDefault(); (i>0? L[i-1] : inp).focus(); }
    if(e.key==='Escape'){ res.hidden=true; inp.focus(); }
  });
  res.addEventListener('click',e=>{
    const el=e.target.closest('a,button'); if(!el) return;
    res.hidden=true;
    if(opts.onPick && el.dataset.dep!=null){ inp.value=''; opts.onPick(deps[+el.dataset.dep]); }
    else inp.value='';
  });
}
['qHome','qDep','qNf'].forEach(id=>bindSearch(id));
document.addEventListener('click',e=>{ if(!e.target.closest('.search')) document.querySelectorAll('.results').forEach(r=>r.hidden=true); });
document.querySelectorAll('.ndeps').forEach(x=>x.textContent=deps.length);

let depListDone=false;
function renderDepList(){
  if(depListDone) return; depListDone=true;
  const by={}; deps.forEach(d=>(by[d.nd]=by[d.nd]||[]).push(d));
  const keys=Object.keys(by).sort((a,b)=>a.localeCompare(b,'fr',{numeric:true}));
  $('#deplist').innerHTML=keys.map(k=>{ const L=by[k].slice().sort((a,b)=>+a.ci-+b.ci);
    return `<section class="dgrp"><h3>${esc(L[0].dep)} <span class="num">(${esc(k)})</span></h3><ul>${L.map(d=>`<li><a href="/depute/${esc(d.sl)}">${esc(d.p+' '+d.n)}</a> <small>${+d.ci}${+d.ci===1?'re':'e'} circ. · ${esc(G[d.g]?.short||'NI')}</small></li>`).join('')}</ul></section>`; }).join('');
}
