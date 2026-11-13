/* ---------- Info-bulles « En bref » ---------- */
const DOS = D.dos||{};
const KIND_NOTE = Object.fromEntries(Object.entries(KIND_LEX).filter(([k])=>!/^Pro/.test(k)).map(([k,id])=>[k,lexDef(id)]));
function lecNote(l){ const id=lecLexId(l); return id && id!=='lecture'? lexDef(id) : (l && /deuxième|troisième/i.test(l)? lexDef('lecture') : null); }
function summaryOf(v){
  const d = v.dk ? DOS[v.dk] : null;
  let txt = d ? d[0] : null;
  if(!txt && v.k==='Motion de censure') txt = "Motion de censure contre le Gouvernement, déposée par une partie des députés d'opposition.";
  return {txt, aut:d?d[1]:null, promu:d?d[2]:null, expo:d?d[3]:0};
}
function ib(idx,nores){ return `<button type="button" class="ib" data-ib="${idx}"${nores?' data-nores="1"':''} aria-label="En bref : de quoi parle ce texte ?" aria-expanded="false">i</button>`; }
const pop = document.getElementById('pop'); let popFor=null, popTimer=null;
function popHTML(v,nores){
  const s=summaryOf(v); const notes=[KIND_NOTE[v.k], lecNote(v.lec)].filter(Boolean);
  let h = `<div class="k">En bref</div><p>${esc(s.txt || "Pas de résumé disponible pour ce vote. Ouvrez le scrutin pour lire le texte.")}</p>`;
  if(v.k==='Motion de rejet' && s.txt) h = `<div class="k">Le texte visé</div><p>${esc(s.txt)}</p>`;
  const meta=[];
  if(s.aut) meta.push(`Déposé par <b>${esc(s.aut)}</b>`);
  if(!nores) meta.push(`Résultat : <b>${v.so==='adopté'?'adopté':'rejeté'}</b> (${v.sy[0]} pour, ${v.sy[1]} contre, ${v.sy[2]} abst.)`);
  if(s.promu && !nores) meta.push(`Loi promulguée le <b>${esc(s.promu.replace(/^\w+ /,''))}</b>`);
  notes.forEach(n=>meta.push(esc(n)));
  h += `<div class="meta">${meta.map(m=>`<span>${m}</span>`).join('')}</div>`;
  if(s.txt && v.dk) h += `<div class="src">${s.expo===2?"Extrait de l'exposé des motifs (résumé automatique, en attente de relecture).":"Résumé rédigé d'après "+(s.expo?"l'exposé des motifs":"l'intitulé")+" du texte."}</div>`;
  return h;
}
const TRANSP_HELP = `<div class="k">Transparence</div>
  <p><b>HATVP</b> : ${esc(lexDef('hatvp'))}</p>
  <div class="meta">
    <span><b>Déport</b> : ${esc(lexDef('deport'))}</span>
    <span><b>Démission d'office</b> : le Conseil constitutionnel peut retirer son mandat à un député, par exemple après une peine d'inéligibilité ou des comptes de campagne irréguliers.</span>
    <span>Le casier judiciaire n'est pas public en France : il n'est pas affiché ici.</span>
  </div>
  <div class="src">Sources : hatvp.fr et assemblee-nationale.fr. <a href="/lexique">Lexique</a></div>`;
function showPop(btn){
  if(btn.dataset.ibt){ if(popFor && popFor!==btn) popFor.setAttribute('aria-expanded','false'); pop.innerHTML=TRANSP_HELP; pop.hidden=false; popFor=btn; btn.setAttribute('aria-expanded','true'); placePop(btn); return; }
  const v=votes[+btn.dataset.ib]; if(!v) return;
  if(popFor && popFor!==btn) popFor.setAttribute('aria-expanded','false');
  pop.innerHTML=popHTML(v, btn.dataset.nores==='1'); pop.hidden=false; popFor=btn; btn.setAttribute('aria-expanded','true');
  placePop(btn);
}
function placePop(btn){
  const r=btn.getBoundingClientRect(), pw=pop.offsetWidth, ph=pop.offsetHeight;
  let x=Math.min(Math.max(12, r.left+r.width/2-pw/2), innerWidth-pw-12);
  let y=r.bottom+8; if(y+ph>innerHeight-8) y=Math.max(8, r.top-ph-8);
  pop.style.left=x+'px'; pop.style.top=y+'px';
}
function hidePop(){ pop.hidden=true; if(popFor) popFor.setAttribute('aria-expanded','false'); popFor=null; }
document.addEventListener('mouseover',e=>{ const b=e.target.closest('.ib'); if(b && matchMedia('(hover:hover)').matches){ clearTimeout(popTimer); showPop(b); } });
document.addEventListener('mouseout',e=>{ const b=e.target.closest('.ib'); if(b && matchMedia('(hover:hover)').matches){ popTimer=setTimeout(()=>{ if(!pop.matches(':hover')) hidePop(); },180); } });
pop.addEventListener('mouseleave',()=>{ if(matchMedia('(hover:hover)').matches) hidePop(); });
document.addEventListener('click',e=>{ const b=e.target.closest('.ib'); if(b){ e.preventDefault(); e.stopPropagation(); (popFor===b && !pop.hidden && !matchMedia('(hover:hover)').matches)? hidePop() : showPop(b); return; } if(!e.target.closest('#pop')) hidePop(); }, true);
document.addEventListener('focusin',e=>{ const b=e.target.closest('.ib'); if(b) showPop(b); });
document.addEventListener('keydown',e=>{ if(e.key==='Escape') hidePop(); });
addEventListener('scroll',()=>{ if(!pop.hidden) hidePop(); }, {passive:true});
document.getElementById('sheet').addEventListener('scroll',()=>{ if(!pop.hidden) hidePop(); }, {passive:true});

$('#fresh').innerHTML = `<span>Données du <b>${fdate(D.generated.slice(0,10))}</b> · dernier scrutin : <b>${fdate(D.lastScrutin)}</b></span><span><b class="num">${D.nScrutins.toLocaleString('fr-FR')}</b> scrutins publics analysés</span><span>17<sup>e</sup> législature · open data AN</span>`;

