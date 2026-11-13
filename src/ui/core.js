const D = JSON.parse(document.getElementById('data').textContent);
const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const AN = 'https://www.assemblee-nationale.fr';
const EXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>';
const MOIS = ['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
const fdate = s => { const [y,m,d]=s.split('-'); return (+d)+' '+MOIS[+m-1]+' '+y; };
const ABR = {UDDPLR:'UDR'};
const LOGOS = D.logos||{};
const ORDER = ['LFI-NFP','GDR','ECOS','SOC','LIOT','DEM','EPR','HOR','DR','UDR','UDDPLR','RN','NI'];
const G = {}; D.groups.forEach(g=>{ g.short = ABR[g.a]||g.a; G[g.id]=g; });
const groupsOrdered = ORDER.map(a=>D.groups.find(g=>g.a===a)).filter(Boolean);
D.groups.forEach(g=>{ if(!groupsOrdered.includes(g)) groupsOrdered.push(g); });
const deps = D.deputes; deps.forEach((d,i)=>{ d.i=i; });
const votes = D.votes; // newest first
const CAT = Object.fromEntries(D.cats);
const posName = {p:'Pour',c:'Contre',a:'Abstention',n:'Non-votant','-':'Absent'};
const posCls = {pour:'p',contre:'c',abstention:'a'};

// group stats
groupsOrdered.forEach(g=>{
  const m = deps.filter(d=>d.g===g.id);
  g.members = m;
  g.n = m.length;
  g.fem = m.length? Math.round(100*m.filter(d=>d.c==='Mme').length/m.length):0;
  const ages = m.filter(d=>d.b).map(d=>age(d.b));
  g.age = ages.length? Math.round(ages.reduce((a,b)=>a+b,0)/ages.length):0;
  const L = m.filter(d=>d.loy!=null);
  g.loy = L.length? Math.round(L.reduce((a,d)=>a+d.loy,0)/L.length):0;
  g.part = m.length? Math.round(100*m.reduce((a,d)=>a+d.part/Math.max(1,d.elig),0)/m.length):0;
  g.pres = m.find(d=>d.gq && /pr[ée]sident/i.test(d.gq));
});
const avgPart = Math.round(100*deps.reduce((a,d)=>a+d.part/Math.max(1,d.elig),0)/deps.length);
const avgKey = Math.round(100*deps.reduce((a,d)=>a+d.kp/Math.max(1,d.ke),0)/deps.length);
const avgLoy = Math.round(deps.filter(d=>d.loy!=null).reduce((a,d)=>a+d.loy,0)/deps.filter(d=>d.loy!=null).length);
function age(b){ const t=new Date('2026-09-28'), d=new Date(b); let a=t.getFullYear()-d.getFullYear(); if(t<new Date(t.getFullYear(),d.getMonth(),d.getDate())) a--; return a; }
function groupBadge(g,px){
  const fs=Math.round(px*(g.short.length>5?0.2:g.short.length>3?0.28:0.36));
  return `<span class="gbadge" style="width:${px}px;height:${px}px;font-size:${fs}px;background:${g.col};color:${textColorOn(g.col)}" aria-hidden="true">${esc(g.short)}${LOGOS[g.short]?`<img src="${esc(LOGOS[g.short][0])}" alt="" loading="lazy">`:''}</span>`;
}
function initials(d){ return (d.p[0]||'')+(d.n.replace(/^(de |d'|le |la |du )/i,'')[0]||''); }
function avatar(d,cls){ const g=G[d.g]; return `<span class="av ${cls||''}" style="background:${g?g.col:'#888'}">${esc(initials(d))}</span>`; }
function relLum(hex){ const h=hex.replace('#',''); return [0,2,4].map(i=>{ const x=parseInt(h.substr(i,2),16)/255; return x<=0.03928?x/12.92:Math.pow((x+0.055)/1.055,2.4); }).reduce((a,x,i)=>a+x*[0.2126,0.7152,0.0722][i],0); }
function textColorOn(hex){ const L=relLum(hex); return (1.05)/(L+0.05) >= (L+0.05)/(relLum('#111111')+0.05) ? '#fff' : '#111'; } // la couleur de texte la plus contrastée
function circo(d){ const n=+d.ci; return `${d.dep} (${d.nd}) · ${n}${n===1?'re':'e'} circ.`; }
const DEP_DU=['Bas-Rhin','Calvados','Cantal','Cher','Doubs','Finistère','Gard','Gers','Haut-Rhin','Jura','Loir-et-Cher','Loiret','Lot','Lot-et-Garonne','Morbihan','Nord','Pas-de-Calais','Puy-de-Dôme','Rhône','Tarn','Tarn-et-Garonne','Territoire de Belfort',"Val-d'Oise",'Val-de-Marne','Var','Vaucluse'];
const DEP_SANS=['Paris','Mayotte','Saint-Pierre-et-Miquelon','Wallis-et-Futuna','Saint-Barthélemy et Saint-Martin'];
function deDep(n){
  if(DEP_SANS.includes(n)) return 'de '+n;
  if(n==='Réunion') return 'de La Réunion';
  if(DEP_DU.includes(n)) return 'du '+n;
  if(/^(Hauts-|Hautes-|Alpes-|Bouches-|Côtes-|Deux-|Pyrénées-|Français |Ardennes|Landes|Vosges|Yvelines)/.test(n)) return 'des '+n;
  if(/^[AEÉIOUYH]/.test(n) && !/^Haute-/.test(n)) return "de l'"+n;
  return 'de la '+n;
}
function vTitle(v){ return v.dos || v.t.replace(/^l['’]ensemble (de la |du |des )?/i,'').replace(/\s*\([^)]*\)\.?$/,''); }


