/* ---------- Adresses (History API) ---------- */
const SITE='Hémicycle ouvert';
const DESC_DEF=document.querySelector('meta[name="description"]')?.content||'';
const VIEWS={};
const NF={view:'introuvable',params:{}};
const NAV={'depute-liste':'depute',depute:'depute',votes:'votes',scrutin:'votes',comprendre:'comprendre',groupes:'comprendre',groupe:'comprendre',lexique:'comprendre',jouer:'jouer',devine:'jouer',quiz:'jouer'};
function registerView(name, el, render){ VIEWS[name]={el:typeof el==='string'?$(el):el, render}; }
function normPath(p){
  p=String(p).split(/[?#]/)[0];
  try{ p=decodeURIComponent(p); }catch(e){}
  p=p.toLowerCase().replace(/\/+$/,'');
  return p||'/';
}
function route(path){
  const s=normPath(path).split('/').filter(Boolean);
  if(!s.length) return {view:'home',params:{}};
  if(s.length>2) return NF;
  const [a,b]=s;
  switch(a){
    case 'depute': return b? {view:'depute',params:{slug:b}} : {view:'depute-liste',params:{}};
    case 'votes': return {view:'votes',params:{cat:b||null}};
    case 'scrutin': return b && /^\d+$/.test(b)? {view:'scrutin',params:{n:+b}} : NF;
    case 'comprendre': return b? NF : {view:'comprendre',params:{}};
    case 'groupes': return b? {view:'groupe',params:{sigle:b}} : {view:'groupes',params:{}};
    case 'lexique': return b? NF : {view:'lexique',params:{}};
    case 'jouer': return !b? {view:'jouer',params:{}} : b==='devine'? {view:'devine',params:{}} : b==='groupe'? {view:'quiz',params:{}} : NF;
  }
  return NF;
}
function metaTag(attr,key){
  let m=document.head.querySelector(`meta[${attr}="${key}"]`);
  if(!m){ m=document.createElement('meta'); m.setAttribute(attr,key); document.head.appendChild(m); }
  return m;
}
function setMeta(meta, path){
  const desc=meta.description||DESC_DEF, url=location.origin+path;
  document.title = meta.title+' · '+SITE;
  metaTag('name','description').content=desc;
  metaTag('property','og:title').content=meta.title;
  metaTag('property','og:description').content=desc;
  metaTag('property','og:url').content=url;
  let c=document.head.querySelector('link[rel="canonical"]');
  if(!c){ c=document.createElement('link'); c.rel='canonical'; document.head.appendChild(c); }
  c.href=url;
}
let curView=null;
function render(path, opts){
  opts=opts||{};
  const p=normPath(path);
  let r=route(p);
  // fiche député ouverte depuis le site : la vue en cours reste en fond
  if(r.view==='depute' && curView && curView!=='introuvable' && !opts.initial){
    const d=deps.find(x=>x.sl===r.params.slug);
    if(d){ openDep(d.i,{fromRoute:true}); setMeta(depMeta(d), p); return; }
  }
  let v=VIEWS[r.view], meta=v.render(r.params);
  if(!meta){ r=NF; v=VIEWS.introuvable; meta=v.render({}); }
  if(r.view!=='depute' && typeof closeDep==='function' && !overlay.hidden) closeDep({silent:true});
  Object.values(VIEWS).forEach(x=>{ if(x.el && x.el!==v.el) x.el.hidden=true; });
  v.el.hidden=false;
  setMeta(meta, p);
  document.querySelectorAll('.mainnav a').forEach(a=>{ if(a.dataset.nav===NAV[r.view]) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); });
  if(!opts.pop && !opts.initial && !opts.keepScroll && r.view!=='depute'){ scrollTo(0,0); const h=v.el.querySelector('h1'); if(h) h.focus({preventScroll:true}); }
  curView=r.view;
}
function navigate(path, opts){
  opts=opts||{};
  const p=normPath(path), hash=String(path).includes('#')? '#'+String(path).split('#')[1] : '';
  if(opts.replace) history.replaceState({inApp:!!(history.state&&history.state.inApp)},'',p+hash);
  else history.pushState({inApp:true},'',p+hash);
  render(p, opts);
}
document.addEventListener('click',e=>{
  if(e.defaultPrevented || e.button!==0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const a=e.target.closest('a[href^="/"]');
  if(!a || a.target || a.hasAttribute('download')) return;
  e.preventDefault(); navigate(a.getAttribute('href'));
});
addEventListener('popstate',()=>render(location.pathname,{pop:true}));

/* ---------- Vues ---------- */
registerView('home','#view-home',()=>({title:'Ce que fait votre Assemblée, en clair', description:"Trouver son député, comprendre ce que l'Assemblée nationale a décidé, et comment chaque groupe a voté."}));
registerView('depute-liste','#view-depute',()=>{ renderDepList(); return {title:'Trouver son député', description:"Les "+deps.length+" députés en exercice, par nom, département ou ville."}; });
registerView('comprendre','#view-hemi',()=>({title:"Comprendre l'Assemblée", description:"L'hémicycle interactif : les 577 sièges et les groupes politiques de l'Assemblée nationale."}));
registerView('groupes','#view-groupes',()=>{ selectGroup(null); return {title:'Les groupes politiques', description:"Les groupes politiques de l'Assemblée nationale : sièges, vote avec son groupe, participation."}; });
registerView('groupe','#view-groupes',({sigle})=>{ const g=groupsOrdered.find(x=>slugG(x.short)===sigle); if(!g) return null; selectGroup(g.id); return {title:`${g.l} (${g.short})`, description:`Le groupe ${g.l} à l'Assemblée nationale : ${g.n} sièges, ses membres et ses derniers votes.`}; });
registerView('lexique','#view-lexique',()=>({title:'Lexique', description:"Les mots de la procédure parlementaire, définis simplement."}));
registerView('jouer','#view-jouer',()=>({title:'Jouer', description:"Deux jeux construits à partir des vrais votes de l'Assemblée nationale."}));
registerView('devine','#view-game',()=>{ if(!gameState) newRound(); return {title:'Devine le vote', description:"Un vrai scrutin, un vrai groupe : comment la majorité du groupe a-t-elle voté ?"}; });
registerView('quiz','#view-quiz',()=>{ renderQuiz(); return {title:'Trouve ton groupe', description:"20 vrais votes de l'Assemblée : découvrez quel groupe a voté comme vous."}; });
registerView('introuvable','#view-introuvable',()=>({title:'Page introuvable', description:DESC_DEF}));
registerView('votes','#view-votes',({cat})=>{
  if(cat && !CAT[cat]) return null;
  const c=cat||'all';
  if(fCat!==c || openVote!=null){ fCat=c; limit=20; openVote=null; }
  renderVotes();
  return cat? {title:'Les décisions : '+CAT[cat], description:`Les votes clés de l'Assemblée nationale sur le thème « ${CAT[cat]} ».`}
            : {title:'Les décisions', description:"Les votes clés de l'Assemblée nationale, classés par thème, avec le vote de chaque groupe."};
});
registerView('scrutin','#view-votes',({n})=>{
  const idx=votes.findIndex(v=>v.n===n); if(idx<0) return null;
  showVoteInList(idx);
  return {title:`Scrutin n° ${n} : ${vTitle(votes[idx])}`, description:resultSentence(votes[idx])};
});
registerView('depute','#view-depute',({slug})=>{
  const d=deps.find(x=>x.sl===slug); if(!d) return null;
  renderDepList(); openDep(d.i,{fromRoute:true});
  return depMeta(d);
});
