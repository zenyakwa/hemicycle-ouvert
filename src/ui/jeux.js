/* ---------- Game ---------- */
let gameState=null, score={ok:0,tot:0,streak:0,best:0};
try{ score.best=+(localStorage.getItem('ho-best')||0); }catch(e){}
const pool = votes.filter(v=>v.k==='Projet de loi'||v.k==='Proposition de loi'||v.k==='Motion de censure');
function newRound(){
  let v,gx,tries=0;
  do{ v=pool[Math.floor(Math.random()*pool.length)]; const cands=v.gv.filter(x=>G[x[0]] && G[x[0]].n>=15 && (x[2]+x[3]+x[4])>=5); gx=cands[Math.floor(Math.random()*cands.length)]; tries++; } while(!gx && tries<50);
  gameState={v,gx,answered:false};
  renderGame();
}
function renderGame(){
  const {v,gx,answered,choice}=gameState; const g=G[gx[0]];
  const [,pm,p,c,a]=gx;
  const btn=(val,lab)=>{ let cls=''; if(answered){ if(val===pm) cls='right'; else if(val===choice) cls='wrong'; } return `<button data-v="${val}" class="${cls}" ${answered?'disabled':''}>${lab}</button>`; };
  $('#game').innerHTML = `
    <div class="q">Le groupe</div>
    <div class="who"><span class="sw" style="background:${g.col}"></span>${esc(g.l)}</div>
    <div class="q" style="margin-top:14px">a voté, le ${fdate(v.dt)}, sur</div>
    <div class="txt" style="margin-top:6px">${esc(vTitle(v))}${ib(votes.indexOf(v), !answered)}</div>
    <div class="ctx">${esc(v.k)} · ${esc(CAT[v.cat])}${v.lec?' · '+esc(v.lec):''}</div>
    <div class="answers">${btn('pour','Pour')}${btn('contre','Contre')}${btn('abstention','Abstention')}</div>
    ${answered?`<div class="verdict"><b class="${choice===pm?'ok':'ko'}">${choice===pm?'Bien vu !':'Raté.'}</b> La majorité du groupe a voté <b>${esc(pm)}</b> : ${p} pour, ${c} contre, ${a} abstentions. Au final, le texte a été <b>${esc(v.so)}</b> par l'Assemblée (${v.sy[0]} pour, ${v.sy[1]} contre).
      <div class="links"><a class="lnk" href="${AN}/dyn/17/scrutins/${v.n}" target="_blank" rel="noopener">Voir le scrutin ${EXT}</a><a class="lnk" href="#" data-goto="${votes.indexOf(v)}">Détail par groupe</a></div></div>`:''}
    <div class="score"><span><b>${score.ok}</b>/ ${score.tot} bonnes réponses</span><span><b>${score.streak}</b>série</span><span><b>${score.best}</b>record</span>${answered?'<button class="next">Question suivante →</button>':''}</div>`;
}
$('#game').addEventListener('click',e=>{
  const n=e.target.closest('.next'); if(n){ newRound(); return; }
  const gt=e.target.closest('[data-goto]'); if(gt){ e.preventDefault(); gotoVote(+gt.dataset.goto); return; }
  const b=e.target.closest('.answers button'); if(!b||gameState.answered) return;
  gameState.answered=true; gameState.choice=b.dataset.v;
  score.tot++; if(b.dataset.v===gameState.gx[1]){ score.ok++; score.streak++; if(score.streak>score.best){ score.best=score.streak; try{localStorage.setItem('ho-best',score.best);}catch(e){} } } else score.streak=0;
  renderGame();
});
document.addEventListener('click',e=>{ const a=e.target.closest('a[href="#"]'); if(a) e.preventDefault(); });

/* ---------- Trouve ton groupe ---------- */
const QUIZ=(D.quiz||[]).map(q=>Object.assign({},q,{vi:votes.findIndex(v=>v.n===q.n)})).filter(q=>q.vi>=0);
const QG=groupsOrdered.filter(g=>g.a!=='NI');
let qzState={step:-1,ans:{}};
try{ const s=JSON.parse(localStorage.getItem('ho-quiz')||'null'); if(s&&s.ans) qzState=s; }catch(e){}
function qzSave(){ try{ localStorage.setItem('ho-quiz',JSON.stringify(qzState)); }catch(e){} }
const ANS={p:'Pour',c:'Contre',s:'Sans avis'};
function groupPos(v,gid){ const x=v.gv.find(y=>y[0]===gid); return x?x[1]:null; }
function qzScores(){
  return QG.map(g=>{ let s=0,n=0,same=0;
    QUIZ.forEach(q=>{ const a=qzState.ans[q.n]; if(a!=='p'&&a!=='c') return; const gp=groupPos(votes[q.vi],g.id); if(!gp) return;
      n++; const my=a==='p'?'pour':'contre'; if(gp===my){s+=1;same++;} else if(gp==='abstention') s+=.5; });
    return {g,pct:n?Math.round(100*s/n):0,n,same}; }).filter(r=>r.n>0).sort((a,b)=>b.pct-a.pct||b.same-a.same);
}
function renderQuiz(){
  const el=$('#quiz'); const st=qzState.step;
  if(st<0){
    el.innerHTML=`<div class="qz qz-intro">
      <p>Chaque question reprend un <b>vrai texte</b> voté par l'Assemblée entre 2024 et 2026. Vous votez « pour », « contre », ou vous passez. On compare ensuite vos réponses au vote de la majorité de chaque groupe.</p>
      <ul><li>20 questions, environ 3 minutes.</li><li>Sous chaque question : un extrait officiel du texte, et le bouton ⓘ pour en savoir plus.</li><li>C'est un jeu, pas une consigne de vote : 20 votes ne résument pas un programme politique.</li></ul>
      <button class="btn" data-qz="start">${Object.keys(qzState.ans).length?'Reprendre le questionnaire':'Commencer'}</button>
      ${Object.keys(qzState.ans).length?' <button class="btn ghost" data-qz="reset">Recommencer à zéro</button>':''}
    </div>`; return;
  }
  if(st>=QUIZ.length){ renderQuizResult(); return; }
  const q=QUIZ[st], v=votes[q.vi], a=qzState.ans[q.n];
  el.innerHTML=`<div class="qz">
    <div class="qz-top"><span>Question <b class="num">${st+1}</b> / ${QUIZ.length}</span><span class="tag">${esc(q.th)}</span></div>
    <div class="qz-prog"><i style="width:${100*st/QUIZ.length}%"></i></div>
    <div class="qz-q">${esc(q.q)}${ib(q.vi,true)}</div>
    ${q.qt?`<blockquote class="qz-quote">« ${esc(q.qt)} »<cite>L'argument des auteurs du texte · ${esc(q.qs)} · <a href="${AN}/dyn/17/scrutins/${v.n}" target="_blank" rel="noopener">scrutin n° ${v.n}</a></cite></blockquote>`:`<p class="note">Texte voté le ${fdate(v.dt)} · <a href="${AN}/dyn/17/scrutins/${v.n}" target="_blank" rel="noopener">scrutin n° ${v.n}</a></p>`}
    <div class="qz-ans">${['p','c','s'].map(k=>`<button data-a="${k}" aria-pressed="${a===k}">${ANS[k]}</button>`).join('')}</div>
    <div class="qz-nav"><button data-qz="prev" ${st===0?'hidden':''}>← Question précédente</button><button data-qz="skip">Passer →</button></div>
  </div>`;
}
function renderQuizResult(){
  const R=qzScores(); const el=$('#quiz');
  const answered=QUIZ.filter(q=>['p','c'].includes(qzState.ans[q.n])).length;
  if(answered<3){ el.innerHTML=`<div class="qz"><p>Vous avez répondu à ${answered} question${answered>1?'s':''} seulement : il en faut au moins 3 pour comparer.</p><button class="btn" data-qz="restart">Reprendre au début</button></div>`; return; }
  const top=R[0], g=top.g;
  el.innerHTML=`<div class="qz">
    <div class="qz-win" style="border-color:${g.col}">${groupBadge(g,64)}
      <div><div class="note">Le groupe qui a le plus voté comme vous</div><h3>${esc(g.l)}</h3><div class="note">Même vote sur ${top.same} question${top.same>1?'s':''} sur ${top.n}</div></div>
      <div class="pct">${top.pct} %</div></div>
    <div class="qz-actions">
      <button class="btn" data-qz="group" data-g="${g.id}">Voir ce groupe dans l'hémicycle</button>
      <button class="btn ghost" data-qz="restart">Refaire le questionnaire</button>
    </div>
    <h4 style="margin:18px 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)">Tous les groupes</h4>
    <div class="qz-rank">${R.map(r=>`<button class="r" data-qz="group" data-g="${r.g.id}" title="${esc(r.g.l)}"><b>${esc(r.g.short)}</b><span class="tr"><i style="width:${r.pct}%;background:${r.g.col}"></i></span><span class="v">${r.pct} %</span></button>`).join('')}</div>
    <p class="note">Score : 1 point quand le groupe a voté comme vous, ½ point quand il s'est abstenu, sur les questions où vous avez voté « pour » ou « contre ». Les non-inscrits ne forment pas un groupe et ne sont pas classés. Le groupe UDR n'existait pas encore lors de certains votes : il est comparé sur moins de questions.</p>
    <h4 style="margin:22px 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)">Vos réponses, question par question</h4>
    <div style="overflow-x:auto"><table class="qz-det"><thead><tr><th>Question</th><th>Vous</th><th>${esc(g.short)}</th><th>Tous les groupes (de gauche à droite)</th></tr></thead><tbody>
    ${QUIZ.map(q=>{ const v=votes[q.vi], a=qzState.ans[q.n]||'s', gp=groupPos(v,g.id);
      return `<tr><td><a href="#" data-openvote="${q.vi}">${esc(q.q)}</a>${ib(q.vi)}</td><td><span class="pos ${a==='p'?'p':a==='c'?'c':'x'}">${ANS[a]}</span></td><td>${gp?`<span class="pos ${posCls[gp]}">${esc(gp)}</span>`:'—'}</td><td><span class="gd">${QG.map(x=>{const p=groupPos(v,x.id); return `<i title="${esc(x.short)} : ${esc(p||'absent')}" style="background:${p?posColor[p]:'var(--absent)'}"></i>`;}).join('')}</span></td></tr>`; }).join('')}
    </tbody></table></div>
  </div>`;
}
$('#quiz').addEventListener('click',e=>{
  if(e.target.closest('.ib')) return;
  const ov=e.target.closest('[data-openvote]'); if(ov){ e.preventDefault(); gotoVote(+ov.dataset.openvote); return; }
  const b=e.target.closest('[data-a]');
  if(b){ const q=QUIZ[qzState.step]; qzState.ans[q.n]=b.dataset.a; qzState.step++; qzSave(); renderQuiz(); $('#view-quiz').scrollIntoView({block:'start'}); return; }
  const c=e.target.closest('[data-qz]'); if(!c) return; const k=c.dataset.qz;
  if(k==='start'){ const firstOpen=QUIZ.findIndex(q=>!(q.n in qzState.ans)); qzState.step=firstOpen<0?QUIZ.length:firstOpen; }
  if(k==='reset'||k==='restart'){ qzState={step:0,ans:{}}; }
  if(k==='prev') qzState.step=Math.max(0,qzState.step-1);
  if(k==='skip'){ qzState.ans[QUIZ[qzState.step].n]='s'; qzState.step++; }
  if(k==='group'){ showTab('hemi'); selectGroup(c.dataset.g); $('#view-hemi').scrollIntoView({block:'start'}); return; }
  qzSave(); renderQuiz();
});

let startTab='hemi'; try{ startTab=localStorage.getItem('ho-tab')||'hemi'; }catch(e){}
