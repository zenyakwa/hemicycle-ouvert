/* ---------- Search ---------- */
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
deps.forEach(d=>d.key=norm(`${d.p} ${d.n} ${d.dep} ${d.nd} ${d.r}`));
const qEl=$('#q'), resEl=$('#results');
qEl.addEventListener('input',()=>{
  const q=norm(qEl.value.trim());
  hemi.querySelectorAll('circle').forEach(c=>c.classList.remove('hit'));
  if(q.length<2){ resEl.hidden=true; if(!selGroup) hemi.querySelectorAll('circle').forEach(c=>c.classList.remove('dim')); return; }
  const terms=q.split(/\s+/);
  const hits=deps.filter(d=> /^\d+[ab]?$/.test(q)? d.nd.toLowerCase()===q.padStart(2,'0') : terms.every(t=>d.key.includes(t)));
  const set=new Set(hits.map(d=>d.i));
  hemi.querySelectorAll('circle').forEach(c=>{ const on=set.has(+c.dataset.i); c.classList.toggle('dim',!on); c.classList.toggle('hit',on && hits.length<30); });
  resEl.innerHTML = hits.length? hits.slice(0,40).map(d=>`<button data-dep="${d.i}">${avatar(d)}<span><b>${esc(d.p+' '+d.n)}</b><br><small>${esc(G[d.g]?.short||'')} · ${esc(circo(d))}</small></span></button>`).join('') : `<div style="padding:12px" class="note">Aucun député ne correspond.</div>`;
  resEl.hidden=false;
});
resEl.addEventListener('click',e=>{ const b=e.target.closest('[data-dep]'); if(b){ resEl.hidden=true; openDep(+b.dataset.dep); } });
document.addEventListener('click',e=>{ if(!e.target.closest('.search')) resEl.hidden=true; });

