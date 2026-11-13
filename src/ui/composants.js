/* ---------- Composants partagés ---------- */
const slugG = s => norm(s).replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const groupPath = g => '/groupes/'+slugG(g.short);
function searchDeps(q){
  q=norm(q.trim()); if(q.length<2) return null;
  const terms=q.split(/\s+/);
  return deps.filter(d=> /^\d+[ab]?$/.test(q)? d.nd.toLowerCase()===q.padStart(2,'0') : terms.every(t=>d.key.includes(t)));
}
function depLink(d){ return `<a href="/depute/${esc(d.sl)}">${avatar(d)}<span><b>${esc(d.p+' '+d.n)}</b><br><small>${esc(G[d.g]?.short||'')} · ${esc(circo(d))}</small></span></a>`; }
function bindSearch(id){
  const inp=document.getElementById(id), res=document.getElementById(id+'-results');
  if(!inp) return;
  inp.addEventListener('input',()=>{
    const hits=searchDeps(inp.value);
    if(!hits){ res.hidden=true; return; }
    res.innerHTML = hits.length? hits.slice(0,40).map(depLink).join('') : '<div class="note" style="padding:12px">Aucun député ne correspond.</div>';
    res.hidden=false;
  });
  res.addEventListener('click',e=>{ if(e.target.closest('a')){ res.hidden=true; inp.value=''; } });
}
['qHome','qDep','qNf'].forEach(bindSearch);
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
