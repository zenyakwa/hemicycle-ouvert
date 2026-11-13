/* ---------- Legend & groups ---------- */
let selGroup=null;
function renderLegend(){
  $('#legend').innerHTML = groupsOrdered.map(g=>`<button class="chip" aria-pressed="${selGroup===g.id}" data-g="${g.id}" title="${esc(g.l)}"><span class="sw" style="background:${g.col}"></span>${esc(g.short)}<span class="n">${g.n}</span></button>`).join('');
}
$('#legend').addEventListener('click',e=>{ const b=e.target.closest('[data-g]'); if(!b) return; selectGroup(selGroup===b.dataset.g?null:b.dataset.g, true); });
function highlight(){
  hemi.querySelectorAll('circle').forEach(c=>{ const d=deps[+c.dataset.i]; c.classList.toggle('dim', !!selGroup && d.g!==selGroup); c.classList.remove('hit'); });
  const g=G[selGroup];
  $('#hc-big').textContent = g? g.n : 577;
  $('#hc-lbl').textContent = g? `sièges · ${(100*g.n/577).toFixed(1).replace('.',',')} %` : 'députés';
}
function selectGroup(id, legendOnly){
  selGroup=id; renderLegend(); highlight();
  if(legendOnly) return;
  id? renderGroup(G[id]) : renderOverview();
}
function renderOverview(){
  const maj=289;
  $('#groupsArea').innerHTML = `
  <div class="block-h"><h1 tabindex="-1">Les groupes politiques</h1><p>Majorité absolue : <b class="num">${maj}</b> sièges. Aucun groupe ne l'atteint seul.</p></div>
  <div class="gcards">${groupsOrdered.map(g=>`
    <button class="gcard" data-g="${g.id}">
      <span class="band" style="background:${g.col}"></span>
      ${groupBadge(g,48)}
      <span class="ab">${esc(g.short)}</span>
      <span class="ln">${esc(g.l)}</span>
      <span class="meter" title="${g.n} sièges"><i style="width:${(100*g.n/122).toFixed(1)}%;background:${g.col}"></i></span>
      <span class="row"><span><b>${g.n}</b> sièges</span><span>vote avec son groupe <b>${g.loy} %</b></span></span>
      <span class="row"><span>femmes <b>${g.fem} %</b></span><span>âge moyen <b>${g.age}</b></span></span>
    </button>`).join('')}
  </div>
  <p class="hint" style="margin-top:10px">${termLink('Vote avec son groupe','vote-avec-son-groupe')} : ${esc(lexDef('vote-avec-son-groupe'))}</p>`;
}
$('#groupsArea').addEventListener('click',e=>{
  const g=e.target.closest('.gcard'); if(g){ navigate(groupPath(G[g.dataset.g])); return; }
  const m=e.target.closest('[data-dep]'); if(m){ e.preventDefault(); openDep(+m.dataset.dep); return; }
  if(e.target.closest('.back')){ navigate('/groupes'); return; }
  const sb=e.target.closest('[data-sort]'); if(sb){ memberSort=sb.dataset.sort; renderGroup(G[selGroup]); }
});
let memberSort='nom';
function renderGroup(g){
  const m=g.members.slice();
  const sorters={nom:(a,b)=>a.n.localeCompare(b.n,'fr'), part:(a,b)=>b.part/b.elig-a.part/a.elig, loy:(a,b)=>(b.loy??-1)-(a.loy??-1), dep:(a,b)=>a.nd.localeCompare(b.nd)||(+a.ci-+b.ci)};
  m.sort(sorters[memberSort]);
  const recent = votes.filter(v=>v.k!=='Motion de rejet').slice(0,8);
  const fg=textColorOn(g.col);
  $('#groupsArea').innerHTML = `
  <div class="gpanel">
    <div class="gp-top"><span class="band" style="background:${g.col}"></span>
      <div style="padding-left:6px;display:flex;gap:14px;align-items:center">${groupBadge(g,56)}<div><h1 tabindex="-1">${esc(g.short)}</h1><div class="full">${esc(g.l)}${g.pres?` · présidé par <a href="#" data-dep="${g.pres.i}" style="font-weight:600">${esc(g.pres.p+' '+g.pres.n)}</a>`:''}</div></div></div>
      <button class="back">← Tous les groupes</button>
    </div>
    <div class="stats">
      <div class="stat"><div class="v num">${g.n}</div><div class="k">sièges sur 577</div></div>
      <div class="stat"><div class="v">${g.loy} %</div><div class="k">vote avec son groupe</div></div>
      <div class="stat"><div class="v">${g.part} %</div><div class="k">participation moy. <span style="text-transform:none">(AN : ${avgPart} %)</span></div></div>
      <div class="stat"><div class="v">${g.fem} %</div><div class="k">de femmes</div></div>
      <div class="stat"><div class="v">${g.age} ans</div><div class="k">âge moyen</div></div>
    </div>
    <div class="gp-body">
      <div>
        <div class="block-h" style="margin-bottom:6px"><h2 style="font-size:20px">Ses derniers votes</h2></div>
        <div class="gvotes">${recent.map(v=>{ const gv=v.gv.find(x=>x[0]===g.id); const pc=gv?posCls[gv[1]]:'x'; return `
          <div class="gv"><span class="d">${fdate(v.dt)}</span><span class="t" style="display:flex;align-items:center;min-width:0"><a href="/scrutin/${v.n}" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(vTitle(v))}</a>${ib(votes.indexOf(v))}</span><span class="pos ${pc}">${gv?esc(gv[1]):'—'}</span></div>`; }).join('')}</div>
      </div>
      <div>
        <div class="toolbar" style="justify-content:space-between;margin-bottom:10px">
          <h2 style="font-family:var(--display);font-weight:800;font-size:20px;margin:0;text-transform:uppercase">Les ${g.n} membres</h2>
          <div class="seg" role="group" aria-label="Trier">
            ${[['nom','Nom'],['dep','Département'],['part','Participation'],['loy','Vote avec son groupe']].map(([k,l])=>`<button data-sort="${k}" aria-pressed="${memberSort===k}">${l}</button>`).join('')}
          </div>
        </div>
        <div class="members">${m.map(d=>`
          <button class="mcard" data-dep="${d.i}">${avatar(d)}
            <span class="who"><span class="nm" style="display:block">${esc(d.p+' '+d.n)}</span><span class="pl" style="display:block">${esc(d.dep)} (${esc(d.nd)})</span></span>
            <span class="sc">${memberSort==='loy'?(d.loy??'–')+' %':Math.round(100*d.part/Math.max(1,d.elig))+' %'}</span>
          </button>`).join('')}</div>
        <p class="hint">Chiffre à droite : ${memberSort==='loy'?'vote avec son groupe sur les votes clés':'participation aux scrutins publics'}.</p>
      </div>
    </div>
  </div>`;
}
renderLegend(); renderOverview();

