/* ---------- Crédits des logos ---------- */
{ const L=Object.entries(LOGOS); if(L.length) $('#logoCredits').innerHTML = 'Logos des groupes : Wikimedia Commons, '+L.map(([k,[,page,lic,aut]])=>`<a href="${esc(page)}" target="_blank" rel="noopener">${esc(k)}</a> (${esc(aut||'auteur non indiqué')}, ${esc(lic)})`).join(', ')+'. Les autres groupes sont représentés par leur sigle.'; }

/* ---------- Démarrage ---------- */
$('#homeFresh').innerHTML = `Données du <b>${fdate(D.generated.slice(0,10))}</b> · dernier scrutin : <b>${fdate(D.lastScrutin)}</b>`;
{
  const OLD={'#votes':'/votes','#jeu':'/jouer/devine','#questionnaire':'/jouer/groupe'};
  if(location.hash && normPath(location.pathname)==='/'){ history.replaceState({inApp:false},'',OLD[location.hash]||'/'); render(location.pathname,{initial:true}); }
  else { const p=normPath(location.pathname); history.replaceState({inApp:false},'',p+location.hash); render(p,{initial:true}); }
}
