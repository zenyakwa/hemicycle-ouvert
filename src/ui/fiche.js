/* ---------- Deputy sheet ---------- */
function gauge(pct, color, label, cmp){
  const r=34, c=2*Math.PI*r, off=c*(1-pct/100);
  return `<div class="gauge"><svg viewBox="0 0 84 84"><circle cx="42" cy="42" r="${r}" fill="none" stroke="var(--surface-2)" stroke-width="9"/><circle cx="42" cy="42" r="${r}" fill="none" stroke="${color}" stroke-width="9" stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" transform="rotate(-90 42 42)"/><text x="42" y="48" text-anchor="middle" font-family="Big Shoulders Display, Arial Narrow, sans-serif" font-weight="800" font-size="22" fill="var(--ink)">${pct==null?'–':pct+'%'}</text></svg><div class="k">${label}</div><div class="cmp">${cmp}</div></div>`;
}
const overlay=$('#overlay'), sheet=$('#sheet'); let lastFocus=null;
function openDep(i, opts){
  const d=deps[i], g=G[d.g];
  opts=opts||{};
  if(overlay.hidden) lastFocus=document.activeElement;
  const mine = votes.filter(v=>v.dt>=d.d);
  const shown = mine.slice(0,14);
  const partPct=Math.round(100*d.part/Math.max(1,d.elig)), keyPct=Math.round(100*d.kp/Math.max(1,d.ke));
  const comm = d.com? `${esc(d.com)}${d.comq && !/^membre$/i.test(d.comq)?` (${esc(d.comq.toLowerCase())})`:''}`:'—';
  sheet.innerHTML = `
  <div class="sh-top"><span class="band" style="background:${g?g.col:'#888'}"></span>
    <button class="sh-close" aria-label="Fermer">×</button>
    <div class="sh-id">${avatar(d)}
      <div><h3>${esc(d.p)} ${esc(d.n)}</h3><div class="gname"><span class="sw" style="width:12px;height:12px;border-radius:50%;background:${g?g.col:'#888'};display:inline-block"></span>${esc(g?g.l:'')}${d.gq && !/^membre$/i.test(d.gq)?` · ${esc(d.gq)}`:''}</div></div>
    </div>
    <dl class="facts">
      <dt>Circonscription</dt><dd>${esc(circo(d))}</dd>
      <dt>Région</dt><dd>${esc(d.r)}</dd>
      <dt>Âge</dt><dd>${d.b?age(d.b)+' ans':'—'}</dd>
      <dt>Profession</dt><dd>${esc(d.pr||'—')}</dd>
      <dt>Commission</dt><dd>${comm}</dd>
      <dt>Parti</dt><dd>${esc(d.pp||'—')}</dd>
      <dt>Élu le</dt><dd>${fdate(d.d)}${d.pe==='1'?' · premier mandat':''}</dd>
    </dl>
  </div>
  <div class="sh-sec">
    <h4>En chiffres</h4>
    <div class="gauges">
      ${gauge(partPct,'var(--accent)','Participation aux scrutins',`moyenne AN ${avgPart} %`)}
      ${gauge(keyPct,'var(--ink)','Présence aux votes clés',`moyenne AN ${avgKey} %`)}
      ${gauge(d.loy,g?g.col:'#888','Vote avec son groupe',`moyenne AN ${avgLoy} %`)}
    </div>
    <p class="note" style="margin-top:10px">${d.part.toLocaleString('fr-FR')} votes exprimés sur ${d.elig.toLocaleString('fr-FR')} scrutins publics depuis le début du mandat.</p>
  </div>
  <div class="sh-sec">
    <h4>Transparence<button type="button" class="ib" data-ibt="1" aria-label="Que signifient ces informations ?" aria-expanded="false">i</button></h4>
    <div class="tlist">
      <div class="trow"><span class="ic">€</span><div>${d.hv?`<a href="https://www.hatvp.fr/pages_nominatives/${esc(d.hv)}" target="_blank" rel="noopener"><b>Déclarations d'intérêts et de patrimoine</b></a> <span class="note">sur le site de la HATVP</span>`:'<span class="note">Pas de page HATVP référencée.</span>'}</div></div>
      <div class="trow"><span class="ic">⇥</span><div>${d.dp&&d.dp.length?`<b>${d.dp.length} déport${d.dp.length>1?'s':''} déclaré${d.dp.length>1?'s':''}</b><div style="display:grid;gap:6px;margin-top:6px">${d.dp.map(x=>`<div class="dport"><span class="d">${esc(x[0])} · ${esc(x[2])}</span><span>${esc(x[1])}</span>${x[3]?`<span class="m">Motif : ${esc(x[3])}</span>`:''}</div>`).join('')}</div>`:'Aucun déport déclaré au registre de l\'Assemblée.'}</div></div>
      <div class="trow"><span class="ic">⌂</span><div>${d.cm?`<b>Arrivée en cours de législature</b> : ${esc(d.cm)}.${/office/.test(d.cm)?' <span class="note">Son prédécesseur a été déclaré démissionnaire d\'office par le Conseil constitutionnel.</span>':/annulation/.test(d.cm)?' <span class="note">L\'élection précédente avait été annulée par le Conseil constitutionnel.</span>':''}`:'Élu lors des élections générales de juillet 2024.'}</div></div>
    </div>
  </div>
  <div class="sh-sec">
    <h4>Ses derniers votes clés</h4>
    ${shown.length? shown.map(v=>{ const c=v.v[d.i]; const pc={p:'p',c:'c',a:'a'}[c]||'x'; return `<div class="dvote"><div><div class="d">${fdate(v.dt)} · ${esc(v.k)} · ${v.so==='adopté'?'adopté':'rejeté'}</div><a href="${AN}/dyn/17/scrutins/${v.n}" target="_blank" rel="noopener">${esc(vTitle(v))}</a>${ib(votes.indexOf(v))}</div><span class="pos ${pc}">${posName[c]}</span></div>`; }).join('') : '<p class="note">Aucun vote clé depuis son arrivée.</p>'}
  </div>
  <div class="sh-sec">
    <h4>Aller plus loin sur le site de l'Assemblée</h4>
    <div class="links" style="margin-top:0">
      <a class="lnk" href="${AN}/dyn/deputes/${d.id}" target="_blank" rel="noopener">Fiche officielle ${EXT}</a>
      <a class="lnk" href="${AN}/dyn/deputes/${d.id}/travaux-parlementaires" target="_blank" rel="noopener">Travaux parlementaires ${EXT}</a>
      <a class="lnk" href="${AN}/dyn/deputes/${d.id}/documents" target="_blank" rel="noopener">Textes déposés ${EXT}</a>
      <a class="lnk" href="${AN}/dyn/deputes/${d.id}/questions" target="_blank" rel="noopener">Questions au Gouvernement ${EXT}</a>
      <a class="lnk" href="${AN}/dyn/17/deports?depute=${d.id}" target="_blank" rel="noopener">Registre des déports ${EXT}</a>
    </div>
  </div>`;
  overlay.hidden=false; document.body.style.overflow='hidden';
  if(!opts.fromRoute){ const path='/depute/'+d.sl; if(normPath(location.pathname)!==path) history.pushState({inApp:true},'',path); setMeta(depMeta(d), path); }
  sheet.querySelector('.sh-close').focus();
}
function depMeta(d){ return {title:`${d.p} ${d.n}, ${d.c==='Mme'?'députée':'député'} ${deDep(d.dep)}`, description:`${d.p} ${d.n} (${G[d.g]?G[d.g].l:'non inscrit'}), ${circo(d)} : participation, votes clés, transparence.`}; }
function closeDep(opts){
  if(overlay.hidden) return;
  overlay.hidden=true; document.body.style.overflow='';
  const f=lastFocus; lastFocus=null;
  if(!(opts&&opts.silent) && normPath(location.pathname).startsWith('/depute/')){
    if(history.state && history.state.inApp) history.back();
    else navigate('/depute',{replace:true,keepScroll:true});
  }
  if(f && document.contains(f)) f.focus();
}
overlay.addEventListener('click',e=>{ if(e.target===overlay || e.target.closest('.sh-close')) closeDep(); });
document.addEventListener('keydown',e=>{ if(e.key==='Escape' && !overlay.hidden) closeDep(); });

