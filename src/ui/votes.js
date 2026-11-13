/* ---------- Votes ---------- */
let fCat='all', fRes='adopté', fKind='', fQ='', limit=20, openVote=null;
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
  $('#vlist').innerHTML = L.slice(0,limit).map(v=>{ const idx=votes.indexOf(v); const [p,c,a]=v.sy; const open=openVote===idx;
    const gs = groupsOrdered.map(g=>v.gv.find(x=>x[0]===g.id)).filter(Boolean);
    return `<article class="vcard" id="v${idx}">
      <div class="vsum" role="button" tabindex="0" data-v="${idx}" aria-expanded="${open}">
        <div class="vmeta"><span class="res ${v.so==='adopté'?'ok':'ko'}">${v.so==='adopté'?'Adopté':'Rejeté'}</span><span class="tag">${esc(CAT[v.cat])}</span><span>${esc(v.k)}${v.lec?' · '+esc(v.lec):''}</span><span class="num">${fdate(v.dt)}</span></div>
        <div><div class="vtitle">${esc(vTitle(v))}${ib(idx)}</div>${v.dos && v.k==='Motion de rejet'?`<div class="vsub">Motion de rejet préalable</div>`:''}</div>
        ${barHTML(p,c,a)}
        <div class="bnums"><span><b>${p}</b> pour</span><span><b>${c}</b> contre</span><span><b>${a}</b> abstentions</span></div>
        <div class="gdots">${gs.map(x=>`<span class="gdot" title="${esc(G[x[0]].l)} : ${esc(x[1])}"><i style="background:${posColor[x[1]]||'var(--absent)'}"></i>${esc(G[x[0]].short)}</span>`).join('')}</div>
      </div>
      ${open?voteDetail(v,idx):''}
    </article>`; }).join('');
  $('#more').hidden = L.length<=limit;
  if(openVote!=null){ const svg=document.getElementById('vh'+openVote); if(svg){ drawHemi(svg, d=>{ const c=votes[openVote].v[d.i]; return c==='p'?'var(--pour)':c==='c'?'var(--contre)':c==='a'?'var(--abst)':'var(--absent)'; }); svg.dataset.vote=openVote; bindSeats(svg); } }
}
function voteDetail(v,idx){
  const rows = groupsOrdered.map(g=>{ const x=v.gv.find(y=>y[0]===g.id); if(!x) return ''; const [,pm,p,c,a]=x; const t=Math.max(1,p+c+a);
    return `<tr><td><span class="sw" style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${g.col};margin-right:6px"></span>${esc(g.short)}</td><td><div class="minibar"><i style="width:${100*p/t}%;background:var(--pour)"></i><i style="width:${100*a/t}%;background:var(--abst)"></i><i style="width:${100*c/t}%;background:var(--contre)"></i></div></td><td class="r">${p}</td><td class="r">${c}</td><td class="r">${a}</td></tr>`; }).join('');
  const S=summaryOf(v);
  return `<div class="vdetail">
    <div>${S.txt?`<p class="vresume"><b>En bref.</b> ${esc(S.txt)}${S.aut?` <span class="note">Déposé par ${esc(S.aut)}.</span>`:''}</p>`:''}
      <div style="overflow-x:auto"><table class="gtable"><thead><tr><td class="note">Groupe</td><td></td><td class="r note">Pour</td><td class="r note">Contre</td><td class="r note">Abst.</td></tr></thead><tbody>${rows}</tbody></table></div>
      <p class="note" style="margin-top:8px">${esc(v.t.charAt(0).toUpperCase()+v.t.slice(1))}</p>
      <div class="links">
        <a class="lnk" href="${AN}/dyn/17/scrutins/${v.n}" target="_blank" rel="noopener">Scrutin n° ${v.n} ${EXT}</a>
        ${v.dr?`<a class="lnk" href="${AN}/dyn/17/dossiers/${v.dr}" target="_blank" rel="noopener">Dossier législatif ${EXT}</a>`:''}
      </div>
    </div>
    <div><svg class="hemi" id="vh${idx}" viewBox="0 0 1000 520" role="img" aria-label="Vote de chaque député dans l'hémicycle"></svg>
      <div class="bnums" style="justify-content:center"><span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--pour)"></i> pour</span><span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--contre)"></i> contre</span><span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--abst)"></i> abstention</span><span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--absent)"></i> absent</span></div>
    </div>
  </div>`;
}
$('#cats').addEventListener('click',e=>{ const b=e.target.closest('[data-c]'); if(!b) return; navigate(b.dataset.c==='all'?'/votes':'/votes/'+b.dataset.c,{keepScroll:true}); });
$('#resSeg').addEventListener('click',e=>{ const b=e.target.closest('[data-r]'); if(!b) return; fRes=b.dataset.r; document.querySelectorAll('#resSeg button').forEach(x=>x.setAttribute('aria-pressed',x===b)); limit=20; renderVotes(); });
$('#kindSel').addEventListener('change',e=>{ fKind=e.target.value; limit=20; renderVotes(); });
$('#vq').addEventListener('input',e=>{ fQ=e.target.value; limit=20; renderVotes(); });
$('#vlist').addEventListener('keydown',e=>{ const b=e.target.closest('.vsum'); if(b && e.target===b && (e.key==='Enter'||e.key===' ')){ e.preventDefault(); b.click(); } });
$('#more').addEventListener('click',()=>{ limit+=20; renderVotes(); });
$('#vlist').addEventListener('click',e=>{ if(e.target.closest('a')||e.target.closest('.ib')||e.target.closest('svg.hemi')) return; const b=e.target.closest('.vsum'); if(!b) return; const i=+b.dataset.v; openVote = openVote===i?null:i; renderVotes(); });
function gotoVote(idx){ navigate('/scrutin/'+votes[idx].n); }
function showVoteInList(idx){
  const v=votes[idx]; fCat='all'; fRes='all'; fKind=''; fQ=''; $('#vq').value=''; $('#kindSel').value='';
  document.querySelectorAll('#resSeg button').forEach(x=>x.setAttribute('aria-pressed',x.dataset.r==='all'));
  const L=filtered(); limit=Math.max(20, L.indexOf(v)+5); openVote=idx; renderVotes();
  const el=document.getElementById('v'+idx); if(el) requestAnimationFrame(()=>el.scrollIntoView({block:'start'}));
}
function resultSentence(v){ const [p,c,a]=v.sy; return `${v.so==='adopté'?'Adopté':'Rejeté'} : ${p} pour, ${c} contre, ${a} abstention${a>1?'s':''}.`; }

