/* ---------- Hemicycle geometry ---------- */
const W=1000, H=520, CX=500, CY=505, R0=170, R1=480;
function seatPositions(n){
  const rows=13; const radii=[]; for(let r=0;r<rows;r++) radii.push(R0+(R1-R0)*r/(rows-1));
  const tot=radii.reduce((a,b)=>a+b,0);
  let counts=radii.map(r=>Math.round(n*r/tot));
  let diff=n-counts.reduce((a,b)=>a+b,0); let k=rows-1; while(diff!==0){ counts[k]+=Math.sign(diff); diff-=Math.sign(diff); k=(k-1+rows)%rows; }
  const pts=[];
  radii.forEach((r,ri)=>{ const c=counts[ri]; for(let j=0;j<c;j++){ const a=Math.PI - (c===1?Math.PI/2:Math.PI*j/(c-1)); pts.push({x:CX+r*Math.cos(a), y:CY-r*Math.sin(a), a, r:ri}); } });
  pts.sort((p,q)=> (q.a-p.a) || (p.r-q.r));
  return {pts, rad: Math.min(13, (R1-R0)/(rows-1)*0.42)};
}
const seatOrder = [];
groupsOrdered.forEach(g=>{ g.members.slice().sort((a,b)=>(+a.s||999)-(+b.s||999)).forEach(d=>seatOrder.push(d)); });
deps.filter(d=>!G[d.g]).forEach(d=>seatOrder.push(d));
const GEO = seatPositions(seatOrder.length);

function drawHemi(svg, colorFn, opts){
  opts=opts||{};
  const rad = opts.rad || GEO.rad;
  let s='';
  GEO.pts.forEach((p,k)=>{ const d=seatOrder[k]; s+=`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${rad.toFixed(1)}" fill="${colorFn(d)}" data-i="${d.i}"></circle>`; });
  svg.innerHTML = s;
}
const hemi = $('#hemi');
drawHemi(hemi, d=>G[d.g]?G[d.g].col:'#999');

// tooltip + click
const tip=$('#tip');
function bindSeats(svg){
  svg.addEventListener('mousemove',e=>{
    const c=e.target.closest('circle'); if(!c){tip.hidden=true;return;}
    const d=deps[+c.dataset.i]; const g=G[d.g];
    let extra=''; if(svg.dataset.vote){ const v=votes[+svg.dataset.vote]; extra=' · '+posName[v.v[d.i]]; }
    tip.innerHTML=`<b>${esc(d.p+' '+d.n)}</b> <small>${esc(g?g.short:'')} · ${esc(d.dep)}${esc(extra)}</small>`;
    tip.hidden=false; tip.style.left=Math.min(e.clientX+12, innerWidth-tip.offsetWidth-8)+'px'; tip.style.top=(e.clientY+14)+'px';
  });
  svg.addEventListener('mouseleave',()=>tip.hidden=true);
  svg.addEventListener('click',e=>{ const c=e.target.closest('circle'); if(c){ tip.hidden=true; openDep(+c.dataset.i); } });
}
bindSeats(hemi);

