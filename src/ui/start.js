/* ---------- Tabs ---------- */
function showTab(t){
  document.querySelectorAll('nav.tabs button').forEach(b=>b.setAttribute('aria-selected', b.dataset.tab===t));
  ['hemi','votes','game','quiz'].forEach(k=>$('#view-'+k).hidden = k!==t);
  if(t==='quiz') renderQuiz();
  if(t==='game' && !gameState) newRound();
  try{ localStorage.setItem('ho-tab',t); }catch(e){}
}
document.querySelector('nav.tabs').addEventListener('click',e=>{ const b=e.target.closest('[data-tab]'); if(b) showTab(b.dataset.tab); });


/* ---------- Démarrage ---------- */
if(location.hash==='#votes') startTab='votes'; if(location.hash==='#jeu') startTab='game'; if(location.hash==='#questionnaire') startTab='quiz';
showTab(['hemi','votes','game','quiz'].includes(startTab)?startTab:'hemi');
