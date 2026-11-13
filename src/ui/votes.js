/* ---------- Votes ---------- */
let fCat='all', fRes='adopté', fKind='', fQ='', limit=20;
function filtered(){
  const q=norm(fQ);
  return votes.filter(v=> (fCat==='all'||v.cat===fCat) && (fRes==='all'||v.so===fRes) && (!fKind||v.k===fKind) && (!q || norm(v.t+' '+(v.dos||'')).includes(q)));
}
function renderCats(){
  const base=votes.filter(v=>(fRes==='all'||v.so===fRes)&&(!fKind||v.k===fKind));
  const cnt={}; base.forEach(v=>cnt[v.cat]=(cnt[v.cat]||0)+1);
  const list=[['all','Tout',base.length]].concat(D.cats.filter(([k])=>cnt[k]).map(([k,l])=>[k,l,cnt[k]]));
  $('#cats').innerHTML=list.map(([k,l,n])=>`<button class="cat" data-c="${k}" aria-pressed="${fCat===k}">${esc(l)}<span class="n">${n}</span></button>`).join('');
}
function barHTML(p,c,a){ const t=Math.max(1,p+c+a); return `<div class="bar" aria-hidden="true"><i class="bp" style="width:${100*p/t}%"></i><i class="ba" style="width:${100*a/t}%"></i><i class="bc" style="width:${100*c/t}%"></i></div>`; }
const posColor = {pour:'var(--pour)',contre:'var(--contre)',abstention:'var(--abst)'};
function renderVotes(){
  renderCats();
  const L=filtered();
  $('#vcount').textContent = `${L.length} vote${L.length>1?'s':''} · ${fCat==='all'?'tous sujets':CAT[fCat]}`;
  if(!L.length){ $('#vlist').innerHTML='<div class="empty">Aucun vote ne correspond à ces filtres.</div>'; $('#more').hidden=true; return; }
  $('#vlist').innerHTML = L.slice(0,limit).map(v=>{ const [p,c,a]=v.sy;
    const gs = groupsOrdered.map(g=>v.gv.find(x=>x[0]===g.id)).filter(Boolean);
    return `<a class="vcard vrow" href="/scrutin/${v.n}">
        <span class="vmeta"><span class="res ${v.so==='adopté'?'ok':'ko'}">${v.so==='adopté'?'Adopté':'Rejeté'}</span><span class="tag">${esc(CAT[v.cat])}</span><span>${esc(v.k)}${v.lec?' · '+esc(v.lec):''}</span><span class="num">${fdate(v.dt)}</span></span>
        <span class="vtitle" data-officiel>${esc(vTitle(v))}${v.dos && v.k==='Motion de rejet'?`<span class="vsub">Motion de rejet préalable</span>`:''}</span>
        ${barHTML(p,c,a)}
        <span class="vres">${esc(resultSentence(v))}</span>
        <span class="gdots" aria-hidden="true">${gs.map(x=>`<span class="gdot"><i style="background:${posColor[x[1]]||'var(--absent)'}"></i>${esc(G[x[0]].short)}</span>`).join('')}</span>
    </a>`; }).join('');
  $('#more').hidden = L.length<=limit;
}
$('#cats').addEventListener('click',e=>{ const b=e.target.closest('[data-c]'); if(!b) return; navigate(b.dataset.c==='all'?'/votes':'/votes/'+b.dataset.c,{keepScroll:true}); });
$('#resSeg').addEventListener('click',e=>{ const b=e.target.closest('[data-r]'); if(!b) return; fRes=b.dataset.r; document.querySelectorAll('#resSeg button').forEach(x=>x.setAttribute('aria-pressed',x===b)); limit=20; renderVotes(); });
$('#kindSel').addEventListener('change',e=>{ fKind=e.target.value; limit=20; renderVotes(); });
$('#vq').addEventListener('input',e=>{ fQ=e.target.value; limit=20; renderVotes(); });
$('#more').addEventListener('click',()=>{ limit+=20; renderVotes(); });
function resultSentence(v){ const [p,c,a]=v.sy; return `${v.so==='adopté'?'Adopté':'Rejeté'} : ${p} pour, ${c} contre, ${a} abstention${a>1?'s':''}.`; }

