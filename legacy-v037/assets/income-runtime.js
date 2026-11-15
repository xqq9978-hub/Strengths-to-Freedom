(()=>{
'use strict';
const DATA=__INCOME_DATA__,UNIT=__INCOME_UNIT__,BASIS=__INCOME_BASIS__,INITIAL=__INITIAL_PATH__;
const $=id=>document.getElementById(id),app=$('app'),svg=$('chart'),wrap=$('chart-wrap'),keys=Object.keys(DATA);
const complete=keys.every(k=>DATA[k].values.every(v=>typeof v==='number'&&Number.isFinite(v)));
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>v===null?'金额待定':Number.isInteger(v)?String(v):v.toFixed(2).replace(/0+$/,'').replace(/\.$/,'');
let selected=keys.includes(INITIAL)?INITIAL:'A',mode='single',view=complete?'curve':'branch',raf=0,token=0,tracks={},width=0,animating=false;
const active=()=>mode==='all'?keys:[selected];
function stop(){cancelAnimationFrame(raf);token++;animating=false}
function path(points){return points.map((p,i)=>{if(!i)return `M${p.x} ${p.y}`;const b=points[i-1];return view==='curve'?`C${(b.x+p.x)/2} ${b.y} ${(b.x+p.x)/2} ${p.y} ${p.x} ${p.y}`:`C${b.x} ${(b.y+p.y)/2} ${p.x} ${(b.y+p.y)/2} ${p.x} ${p.y}`}).join(' ')}
function stateUI(){
 app.classList.toggle('all-mode',mode==='all');app.dataset.view=view;
 $('allPaths').setAttribute('aria-pressed',String(mode==='all'));
 document.documentElement.style.setProperty('--active',mode==='all'?'#c4d7ef':DATA[selected].color);
 $('selection-name').textContent=mode==='all'?'三条路径同时比较':selected+' · '+DATA[selected].name;
 $('final-number').textContent=mode==='all'?'A / B / C':fmt(DATA[selected].values[5]);
 $('final-label').textContent=mode==='all'?'共同起点 · 同步点亮':'第5年 · 条件情景';
 document.querySelectorAll('[data-path]').forEach(b=>b.setAttribute('aria-pressed',String(mode==='all'||b.dataset.path===selected)));
 document.querySelectorAll('.switch [data-view]').forEach(b=>{b.disabled=!complete&&b.dataset.view==='curve';b.setAttribute('aria-pressed',String(b.dataset.view===view))});
 $('milestones').innerHTML=mode==='all'?keys.map(k=>`<div class="milestone" data-route="${k}" style="--active:${DATA[k].color}"><div class="milestone-head">路径 ${k}</div><strong>${esc(DATA[k].name)}</strong><p>第5年 ${fmt(DATA[k].values[5])} ${esc(UNIT)}</p></div>`).join(''):[1,3,5].map((year,i)=>`<div class="milestone" data-year="${year}"><div class="milestone-head">第 ${year} 年</div><strong>${esc(DATA[selected].steps[i])}</strong><p>${fmt(DATA[selected].values[year])} ${esc(UNIT)}</p></div>`).join('');
}
function render(){
 stop();width=Math.max(260,wrap.clientWidth);const mobile=width<540,height=view==='curve'?(mobile?326:410):(mobile?530:580),geometry={};
 svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.style.height=height+'px';
 let s='<title>五年收入路径</title><desc>支持单路径及三路径同时播放；金额来自本次报告，未知不插值；比较模式不更改行动计划选择。</desc><defs><filter id="line-glow"><feGaussianBlur stdDeviation="4"/></filter><filter id="orb-glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="5"/></filter></defs>';
 if(view==='curve'){
  const left=mobile?30:46,right=width-(mobile?69:83),top=43,bottom=height-43,vals=keys.flatMap(k=>DATA[k].values),lo=Math.min(...vals),hi=Math.max(...vals),padding=Math.max((hi-lo)*.12,Math.abs(hi)*.05,1),min=lo-padding,max=hi+padding;
  const x=i=>left+(right-left)*i/5,y=v=>bottom-(v-min)/(max-min)*(bottom-top);
  keys.forEach(k=>geometry[k]=DATA[k].values.map((v,i)=>({x:x(i),y:y(v)})));
  Array.from({length:6},(_,i)=>min+(max-min)*i/5).forEach(v=>s+=`<line class="grid" x1="${left}" x2="${right}" y1="${y(v)}" y2="${y(v)}"/><text class="tick" x="${left-8}" y="${y(v)+4}" text-anchor="end">${fmt(v)}</text>`);
  for(let i=0;i<6;i++)s+=`<text class="tick" x="${x(i)}" y="${height-13}" text-anchor="middle">${i===0?'现在':mobile?i+'年':'第'+i+'年'}</text>`;
  s+=`<text class="axis-note" x="${left}" y="16">${esc(UNIT)}</text>`;
 }else{
  keys.forEach((k,j)=>geometry[k]=Array.from({length:6},(_,i)=>({x:width/2+(j-1)*width*.33*(i?(.64+.36*i/5):0),y:42+i*(height-81)/5})));
  s+=`<text class="axis-note" x="${width/2}" y="15" text-anchor="middle">条件路径 · ${esc(UNIT)}</text>`;
 }
 const slots={};let previous=-Infinity;
 keys.slice().sort((a,b)=>geometry[a][5].y-geometry[b][5].y).forEach(k=>{slots[k]=Math.max(geometry[k][5].y,previous+19);previous=slots[k]});
 const overflow=Math.max(0,previous-(height-48));keys.forEach(k=>slots[k]-=overflow);
 keys.forEach(k=>s+=`<path id="base-${k}" class="base-path" d="${path(geometry[k])}"/>`);
 keys.forEach(k=>{
  const color=DATA[k].color,p=path(geometry[k]);
  s+=`<g id="fx-${k}" style="--active:${color};opacity:0" pointer-events="none"><path id="aura-${k}" class="aura" d="${p}"/><path id="trace-${k}" class="trace" d="${p}"/><g id="head-${k}"><circle r="12" fill="${color}" opacity=".45" filter="url(#orb-glow)"/><circle r="5.5" fill="${color}"/><circle r="2.8" fill="#fff8e8"/></g><g id="tail-${k}" fill="${color}">${Array.from({length:9},()=>'<circle r="2" opacity="0"/>').join('')}</g><circle id="end-ring-${k}" r="6" fill="none" stroke="${color}" opacity="0"/></g>`;
 });
 const nodeW=Math.min(118,width*.205);
 keys.forEach(k=>{
  const d=DATA[k],pts=geometry[k];
  for(let i=1;i<6;i++){
   const p=pts[i];
   s+=view==='curve'?`<g id="node-${k}-${i}" class="marker-group" style="--active:${d.color}"><circle class="marker" cx="${p.x}" cy="${p.y}" r="${mobile?3.7:4.6}"/>${!mobile&&i<5?`<text class="point-value" x="${p.x}" y="${p.y-14}" text-anchor="middle">${fmt(d.values[i])}</text>`:''}</g>`:`<g id="node-${k}-${i}" class="branch-node" style="--active:${d.color}"><rect x="${p.x-nodeW/2}" y="${p.y-21}" width="${nodeW}" height="42" rx="7"/><text class="node-year" x="${p.x-nodeW/2+7}" y="${p.y-5}">第${i}年</text><text class="node-value" x="${p.x+nodeW/2-7}" y="${p.y+12}" text-anchor="end">${d.values[i]===null?'待定':fmt(d.values[i])}</text></g>`;
  }
  const end=pts[5];
  if(view==='curve'){
   if(Math.abs(slots[k]-end.y)>2)s+=`<path fill="none" stroke="${d.color}" opacity=".5" stroke-width="1" d="M${end.x} ${end.y} L${end.x+8} ${slots[k]}"/>`;
   s+=`<text id="end-${k}" class="endpoint" style="--active:${d.color}" x="${end.x+12}" y="${slots[k]+5}">${fmt(d.values[5])} <tspan font-size="10" font-weight="400">${k}</tspan></text>`;
  }else s+=`<text id="end-${k}" class="endpoint" style="--active:${d.color};font-size:11px" x="${end.x}" y="${height-3}" text-anchor="middle">路径 ${k}</text>`;
 });
 keys.forEach(k=>s+=`<path class="hit" data-line="${k}" d="${path(geometry[k])}" aria-hidden="true"/>`);
 const start=geometry.A[0];s+=`<g pointer-events="none"><circle cx="${start.x}" cy="${start.y}" r="5" fill="#ffe8ad"/>${view==='curve'?`<text class="start-label" x="${start.x+8}" y="${start.y-15}">${fmt(DATA.A.values[0])}</text>`:''}</g>`;
 svg.innerHTML=s;tracks={};
 keys.forEach(k=>{
  const base=$('base-'+k),length=base.getTotalLength(),axis=view==='curve'?'x':'y';
  const thresholds=geometry[k].slice(1).map(point=>{let lo=0,hi=length;for(let i=0;i<24;i++){const m=(lo+hi)/2;if(base.getPointAtLength(m)[axis]<point[axis])lo=m;else hi=m}return (lo+hi)/2});
  const reveal=[$('aura-'+k),$('trace-'+k)];reveal.forEach(p=>{p.style.strokeDasharray=`${length} ${length}`;p.style.strokeDashoffset=length});
  tracks[k]={base,length,reveal,head:$('head-'+k),tail:[...$('tail-'+k).children],ring:$('end-ring-'+k),fx:$('fx-'+k),thresholds,end:geometry[k][5]};
 });
 svg.querySelectorAll('[data-line]').forEach(p=>p.addEventListener('click',()=>select(p.dataset.line)));
 stateUI();frame(1,true,1);
}
function frame(progress,finished=false,pulse=0){
 const shown=active();
 keys.forEach(k=>{
  const tr=tracks[k],on=shown.includes(k);tr.fx.style.opacity=on?'1':'0';
  const year=Math.min(5,Math.max(0,progress*5)),i=Math.min(4,Math.floor(year)),bounds=[0,...tr.thresholds],distance=progress>=1?tr.length:bounds[i]+(bounds[i+1]-bounds[i])*(year-i);
  tr.reveal.forEach(p=>p.style.strokeDashoffset=tr.length-distance);
  const point=tr.base.getPointAtLength(distance);tr.head.setAttribute('transform',`translate(${point.x} ${point.y})`);tr.head.setAttribute('opacity',on&&!finished?'1':'0');
  tr.tail.forEach((orb,j)=>{const back=(j+1)*3,p=tr.base.getPointAtLength(Math.max(0,distance-back));orb.setAttribute('cx',p.x);orb.setAttribute('cy',p.y);orb.setAttribute('opacity',on&&!finished&&distance>back?String(.4*(1-j/9)):'0')});
  for(let n=1;n<6;n++)$('node-'+k+'-'+n).classList.toggle('lit',on&&progress*5>=n-1e-6);
  $('end-'+k).classList.toggle('lit',on&&finished);
  tr.ring.setAttribute('cx',tr.end.x);tr.ring.setAttribute('cy',tr.end.y);tr.ring.setAttribute('r',6+20*pulse);tr.ring.setAttribute('opacity',on&&finished?String(.6*(1-pulse)):'0');
 });
 document.querySelectorAll('.milestone').forEach(n=>n.classList.toggle('reached',mode==='all'?finished:progress*5>=Number(n.dataset.year)));
 $('progress-text').textContent=mode==='all'?(finished?'三条路径已全部点亮 · 点击单路可查看对应计划':`三条路径同步出发 · 正在经过第${Math.min(5,Math.floor(progress*5))}年`):(finished?'当前路径已点亮':`路径${selected} · 正在经过第${Math.min(5,Math.floor(progress*5))}年`);
}
function play(){
 stop();stateUI();frame(0);const currentToken=token;
 if(reduce.matches){frame(1,true,1);announce();return}
 animating=true;let start=null;const duration=2600;
 function tick(now){if(currentToken!==token)return;if(start===null)start=now;const elapsed=now-start,raw=Math.min(1,elapsed/duration),p=raw<.5?2*raw*raw:1-Math.pow(-2*raw+2,2)/2;
  const pulse=raw===1?Math.min(1,(elapsed-duration)/650):0;frame(p,raw===1,pulse);
  if(raw===1&&pulse===1){animating=false;announce();return}raf=requestAnimationFrame(tick);
 }raf=requestAnimationFrame(tick);
}
function announce(){$('announcement').textContent=mode==='all'?'三条路径已全部点亮；比较模式不改变行动计划选择。':`路径${selected}已点亮，第5年${fmt(DATA[selected].values[5])} ${UNIT}`}
function select(key,notify=true){if(!DATA[key])return;mode='single';selected=key;play();if(notify)parent.postMessage({type:'value-map-path',path:key},'*')}
$('allPaths').addEventListener('click',()=>{mode='all';play()});$('replay').addEventListener('click',play);
document.querySelectorAll('[data-path]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.path)));
document.querySelectorAll('.switch [data-view]').forEach(b=>b.addEventListener('click',()=>{if(!complete&&b.dataset.view==='curve')return;view=b.dataset.view;render();play()}));
window.addEventListener('message',e=>{if(e.source===parent&&e.data?.type==='value-map-select'&&DATA[e.data.path])select(e.data.path,false)});
let resizeTimer;const resized=()=>{if(Math.abs(wrap.clientWidth-width)<2)return;clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>render(),90)};
if('ResizeObserver'in window)new ResizeObserver(resized).observe(wrap);else window.addEventListener('resize',resized);
reduce.addEventListener?.('change',()=>{if(reduce.matches&&animating){stop();frame(1,true,1);announce()}});
$('basisNote').textContent=BASIS;
const sendSize=()=>parent.postMessage({type:'value-map-size',height:document.documentElement.scrollHeight},'*');
if('ResizeObserver'in window)new ResizeObserver(sendSize).observe(document.body);window.addEventListener('load',sendSize);
render();play();sendSize();
})();
