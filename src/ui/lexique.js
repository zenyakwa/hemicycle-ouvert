/* ---------- Lexique ---------- */
const LEX = {}; (D.lex||[]).forEach(([id,terme,def,formes])=>LEX[id]={id,terme,def,formes});
const lexDef = id => LEX[id] ? LEX[id].def : null;
const KIND_LEX = {'Motion de censure':'motion-de-censure','Motion de rejet':'motion-de-rejet','Résolution':'proposition-de-resolution','Déclaration du Gouvernement':'article-50-1','Projet de loi':'projet-de-loi','Proposition de loi':'proposition-de-loi'};
function lecLexId(l){ if(!l) return null; l=l.toLowerCase();
  if(l.includes('mixte paritaire')) return 'commission-mixte-paritaire';
  if(l.includes('définitive')) return 'lecture-definitive';
  if(l.includes('nouvelle lecture')) return 'nouvelle-lecture';
  return 'lecture'; }
function termLink(text, id){ return LEX[id]? `<a class="lex" href="/lexique#${id}">${esc(text)}</a>` : esc(text); }
let lexDone=false;
function renderLexique(){
  if(lexDone) return; lexDone=true;
  const L=Object.values(LEX).sort((a,b)=>a.terme.localeCompare(b.terme,'fr'));
  $('#lexique').innerHTML = `<dl class="lexlist">${L.map(t=>`<div class="lexitem"><dt id="${t.id}" tabindex="-1">${esc(t.terme)}</dt><dd>${esc(t.def)}</dd></div>`).join('')}</dl>`;
}
