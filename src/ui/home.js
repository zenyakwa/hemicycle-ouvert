/* ---------- Accueil ---------- */
function voteCard(v){
  const s=summaryOf(v), [p,c,a]=v.sy;
  return `<a class="vcard vlink" href="/scrutin/${v.n}">
    <span class="vmeta"><span class="res ${v.so==='adopté'?'ok':'ko'}">${v.so==='adopté'?'Adopté':'Rejeté'}</span><span class="num">${fdate(v.dt)}</span><span class="tag">${esc(CAT[v.cat])}</span><span>${esc(v.k)}</span></span>
    <span class="vtitle" data-officiel>${esc(vTitle(v))}</span>
    <span class="vbref" data-officiel><b>En bref.</b> ${s.txt?esc(s.txt):'Résumé à venir.'}</span>
    ${barHTML(p,c,a)}
    <span class="vres">${esc(resultSentence(v))}</span>
  </a>`;
}
function groupsBar(withLinks){
  const tot=groupsOrdered.reduce((x,g)=>x+g.n,0), M=Math.floor(577/2)+1, max=Math.max(...groupsOrdered.map(g=>g.n));
  return `<div class="gbar" role="img" aria-label="Répartition des ${tot} députés en exercice par groupe, de gauche à droite de l'hémicycle">${groupsOrdered.map(g=>`<a class="seg" href="${groupPath(g)}" style="flex:${g.n};background:${g.col}" title="${esc(g.short)} : ${g.n} sièges" tabindex="-1" aria-hidden="true"></a>`).join('')}</div>
  <ul class="gbar-legend">${groupsOrdered.map(g=>`<li><a href="${groupPath(g)}"><span class="sw" style="background:${g.col}"></span>${esc(g.short)} <span class="n num">${g.n}</span><span class="sr-only"> sièges, ${esc(g.l)}</span></a></li>`).join('')}</ul>
  <p class="gbar-maj">${termLink('Majorité absolue','majorite-absolue')} : <b class="num">${M}</b> sièges.${max<M?" Aucun groupe ne l'atteint seul.":''}</p>
  ${withLinks?`<p class="gbar-links"><a href="/comprendre">Explorer l'hémicycle interactif</a><a href="/groupes">Les ${groupsOrdered.length} groupes</a><a href="/lexique">Lexique</a></p>`:''}`;
}
function renderHome(){
  $('#homeVotes').innerHTML = votes.slice(0,3).map(voteCard).join('');
  const cnt={}; votes.forEach(v=>cnt[v.cat]=(cnt[v.cat]||0)+1);
  $('#homeThemes').innerHTML = '<span class="lbl">Par thème :</span>'+D.cats.filter(([k])=>cnt[k]).map(([k,l])=>`<a href="/votes/${k}">${esc(l)}</a>`).join('');
  $('#homeGroups').innerHTML = groupsBar(true);
  $('#hemiGroups').innerHTML = groupsBar(false);
}
renderHome();
