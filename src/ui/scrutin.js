/* ---------- Page d'un vote : /scrutin/<n> ---------- */
const POSN = {pour:'Pour',contre:'Contre',abstention:'Abstention'};
function depVoteText(v,d){
  if(v.dt<d.d) return d.c==='Mme'? "Pas encore députée à cette date" : "Pas encore député à cette date";
  return {p:'Pour',c:'Contre',a:'Abstention'}[v.v[d.i]] || "N'a pas pris part au vote";
}
function keyDef(v){
  const id = (v.lec && lecLexId(v.lec)!=='lecture')? lecLexId(v.lec) : KIND_LEX[v.k];
  return id && LEX[id]? LEX[id] : null;
}
function voteListHTML(v){
  const cat={p:[],c:[],a:[],x:[],y:[]};
  deps.forEach(d=>{ const k = v.dt<d.d? 'y' : ({p:'p',c:'c',a:'a'})[v.v[d.i]]||'x'; cat[k].push(d); });
  const T={p:'Pour',c:'Contre',a:'Abstention',x:"N'a pas pris part au vote",y:'Pas encore député à cette date'};
  const diff = cat.p.length!==v.sy[0] || cat.c.length!==v.sy[1] || cat.a.length!==v.sy[2];
  return (diff?'<p class="note">Liste des députés actuellement en exercice : les totaux peuvent différer du résultat officiel, qui compte aussi les députés ayant quitté l\'Assemblée depuis ce vote.</p>':'')+Object.keys(T).filter(k=>cat[k].length).map(k=>`<section><h3>${T[k]} (${cat[k].length})</h3><ul>${cat[k].sort((a,b)=>a.n.localeCompare(b.n,'fr')).map(d=>`<li><a href="/depute/${esc(d.sl)}">${esc(d.p+' '+d.n)}</a> <small>${esc(G[d.g]?.short||'')}</small></li>`).join('')}</ul></section>`).join('');
}
let curScrutin=null;
function renderScrutin(v){
  curScrutin=v;
  const [p,c,a]=v.sy, S=summaryOf(v), def=keyDef(v), ok=v.so==='adopté';
  const rows=groupsOrdered.map(g=>{ const x=v.gv.find(y=>y[0]===g.id); if(!x) return ''; const [,pm,gp,gc,ga]=x; const t=Math.max(1,gp+gc+ga);
    return `<li class="grow"><span class="sw" style="background:${g.col}"></span><span class="gsig">${esc(g.short)}</span><span class="gname">${esc(g.l)}</span>
      <span class="gpos ${posCls[pm]||'x'}">${esc(POSN[pm]||pm)}</span>
      <span class="minibar" aria-hidden="true"><i style="width:${100*gp/t}%;background:var(--pour)"></i><i style="width:${100*ga/t}%;background:var(--abst)"></i><i style="width:${100*gc/t}%;background:var(--contre)"></i></span>
      <span class="gnums num"><span title="pour">${gp}</span><span title="contre">${gc}</span><span title="abstention">${ga}</span><span class="sr-only"> : ${gp} pour, ${gc} contre, ${ga} abstentions</span></span></li>`; }).join('');
  $('#view-scrutin').innerHTML = `
  <nav class="crumb" aria-label="Fil d'Ariane"><a href="/votes">Les décisions</a> <span aria-hidden="true">›</span> <a href="/votes/${v.cat}">${esc(CAT[v.cat])}</a></nav>
  <p class="smeta"><span class="num">${fdate(v.dt)}</span> · ${termLink(v.k,KIND_LEX[v.k])}${v.lec?' · '+termLink(v.lec,lecLexId(v.lec)):''}</p>
  <h1 tabindex="-1" class="stitle" data-officiel>${esc(vTitle(v))}</h1>
  <div class="sgrid">
    <div class="smain">
      <section class="resbox ${ok?'ok':'ko'}" aria-label="Résultat du vote">
        <div class="big">${ok?'ADOPTÉ':'REJETÉ'}</div>
        <div class="bnums"><span><b class="num">${p}</b> pour</span><span><b class="num">${c}</b> contre</span><span><b class="num">${a}</b> ${termLink('abstention'+(a>1?'s':''),'abstention')}</span></div>
        ${barHTML(p,c,a)}
        <p>${p+c+a} députés ont pris part à ce vote (pour, contre ou abstention).</p>
        ${v.k==='Motion de censure'?`<p class="note">Une ${termLink('motion de censure','motion-de-censure')} n'est adoptée que si elle recueille la ${termLink('majorité absolue','majorite-absolue')} des membres composant l'Assemblée${v.rq?` (${v.rq} voix pour ce vote)`:''}. Seules les voix « pour » sont comptées.</p>`:''}
      </section>
      <section class="ssec">
        <h2>De quoi s'agit-il ?</h2>
        <p data-officiel>${S.txt?`<b>En bref.</b> ${esc(S.txt)}`:`<b>Résumé à venir.</b>${v.dr?` <a href="${AN}/dyn/17/dossiers/${v.dr}" target="_blank" rel="noopener">Lire le texte officiel</a>`:''}`}</p>
        ${S.aut||S.promu?`<p class="note">${S.aut?`Déposé par ${esc(S.aut)}.`:''}${S.promu?` Loi promulguée le ${esc(S.promu.replace(/^\w+ /,''))}.`:''}</p>`:''}
        <p class="note" data-officiel>Intitulé du scrutin : ${esc(v.t.charAt(0).toUpperCase()+v.t.slice(1))}</p>
        ${def?`<div class="defbox"><b>${esc(def.terme)}</b> : ${esc(def.def)} <a href="/lexique#${def.id}">Voir le lexique</a></div>`:''}
      </section>
      <section class="ssec">
        <h2>Comment chaque groupe a voté</h2>
        <p class="note">Position de la majorité de chaque groupe, puis le détail : pour, contre, abstentions.</p>
        <div class="ghead" aria-hidden="true"><span class="gnums"><span>Pour</span><span>Contre</span><span>Abst.</span></span></div>
        <ul class="glist">${rows}</ul>
        <svg class="hemi" id="vhemi" viewBox="0 0 1000 520" role="img" aria-label="Vote de chaque député dans l'hémicycle : ${p} pour, ${c} contre, ${a} abstentions, les autres n'ont pas pris part au vote"></svg>
        <details id="voteList" class="votelist"><summary>Voir le vote de chaque député en liste</summary>${voteListHTML(v)}</details>
        <div class="bnums hlegend"><span><i style="background:var(--pour)"></i> pour</span><span><i style="background:var(--contre)"></i> contre</span><span><i style="background:var(--abst)"></i> abstention</span><span><i style="background:var(--absent)"></i> n'a pas pris part au vote</span></div>
      </section>
    </div>
    <aside class="sside">
      <section class="sidecard">
        <h2><label for="qVote">Et mon député, qu'a-t-il voté ?</label></h2>
        <div class="search">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          <input id="qVote" type="search" placeholder="Nom ou n° de département" autocomplete="off" aria-label="Et mon député, qu'a-t-il voté ?">
          <div class="results" id="qVote-results" hidden></div>
        </div>
        <div id="myVote" aria-live="polite"></div>
      </section>
      <section class="sidecard links">
        ${v.dr?`<a class="lnk" href="${AN}/dyn/17/dossiers/${v.dr}" target="_blank" rel="noopener">Texte officiel (dossier législatif) ${EXT}</a>`:''}
        <a class="lnk" href="${AN}/dyn/17/scrutins/${v.n}" target="_blank" rel="noopener">Scrutin n° ${v.n} sur assemblee-nationale.fr ${EXT}</a>
        <button type="button" class="lnk" id="copyLink">Copier le lien de ce vote</button>
        <span id="copyMsg" class="note" aria-live="polite"></span>
      </section>
    </aside>
  </div>`;
  const svg=$('#vhemi'), idx=votes.indexOf(v);
  drawHemi(svg, d=>{ const x=v.v[d.i]; return x==='p'?'var(--pour)':x==='c'?'var(--contre)':x==='a'?'var(--abst)':'var(--absent)'; });
  svg.dataset.vote=idx; bindSeats(svg);
  bindSearch('qVote',{asButton:true, onPick:d=>{
    $('#myVote').innerHTML=`<p class="myvote"><a href="/depute/${esc(d.sl)}">${esc(d.p+' '+d.n)}</a> <small>(${esc(G[d.g]?.short||'')} · ${esc(circo(d))})</small><br><span class="pos ${({p:'p',c:'c',a:'a'})[v.dt<d.d?'':v.v[d.i]]||'x'}">${esc(depVoteText(v,d))}</span></p>`; }});
  $('#qVote').placeholder='Nom, ville ou code postal';
  $('#copyLink').addEventListener('click',async()=>{
    const url=location.origin+'/scrutin/'+v.n, m=$('#copyMsg');
    let ok=false;
    try{ await navigator.clipboard.writeText(url); ok=true; }
    catch(e){ const t=document.createElement('textarea'); t.value=url; t.setAttribute('readonly',''); t.style.position='fixed'; t.style.opacity='0'; document.body.appendChild(t); t.select(); try{ ok=document.execCommand('copy'); }catch(_){} t.remove(); }
    m.textContent = ok? 'Lien copié' : 'Copiez ce lien : '+url;
  });
}
