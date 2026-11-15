// A simulated DOM and SVG path contract test, not a browser screenshot/animation test.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'assets/income-runtime.js'),'utf8');
const colors=['#79b5ff','#f3cd7c','#89d5b1'];
function scenario(reduced=false,equalEnds=false,unknown=false){
 const data=Object.fromEntries(['A','B','C'].map((k,i)=>[k,{name:'路径'+k,color:colors[i],values:unknown?[null,null,null,null,null,null]:[15,15+i,16+i,17+i,18+i,equalEnds?20:20+i],steps:['第一步','第二步','第三步']}]));
 const elements={},queue=new Map(),messages=[],listeners={};let next=0;
 class Element{
  constructor(id){this.id=id;this.attrs={};this.dataset={};this.style={setProperty(k,v){this[k]=v}};this.handlers={};this.classes=new Set();this.classList={toggle:(k,on)=>on?this.classes.add(k):this.classes.delete(k)};this.children=id.startsWith('tail-')?Array.from({length:9},()=>new Element('orb')):[];this.clientWidth=700;this._html='';}
  setAttribute(k,v){this.attrs[k]=String(v)}getAttribute(k){return this.attrs[k]||''}
  addEventListener(k,f){this.handlers[k]=f}querySelectorAll(){return []}
  set innerHTML(s){this._html=s;for(const m of s.matchAll(/<[^>]+id="([^"]+)"[^>]*>/g)){const el=get(m[1]);for(const a of m[0].matchAll(/([\w-]+)="([^"]*)"/g))el.attrs[a[1]]=a[2]}}
  get innerHTML(){return this._html}
  getTotalLength(){return 1000}
  getPointAtLength(d){const n=(this.attrs.d||'M0 0 C1 1 2 2 3 3').match(/-?\d+(?:\.\d+)?/g).map(Number),p=Math.max(0,Math.min(1,d/1000));return{x:n[0]+(n[n.length-2]-n[0])*p,y:n[1]+(n[n.length-1]-n[1])*p}}
 }
 const get=id=>elements[id]||(elements[id]=new Element(id));
 const paths=['A','B','C'].map(k=>{const b=new Element('choice'+k);b.dataset.path=k;return b});
 const views=['curve','branch'].map(k=>{const b=new Element(k);b.dataset.view=k;return b});
 const document={getElementById:get,documentElement:{style:{setProperty(){}},scrollHeight:1000},body:{},querySelectorAll(s){return s==='[data-path]'?paths:s==='.switch [data-view]'?views:[]}};
 const parent={postMessage:m=>messages.push(m)};
 const context={document,parent,window:{addEventListener(k,f){listeners[k]=f}},matchMedia:()=>({matches:reduced,addEventListener(){}}),requestAnimationFrame:f=>{const id=++next;queue.set(id,f);return id},cancelAnimationFrame:id=>queue.delete(id),setTimeout:f=>f(),clearTimeout(){}};
 let code=source.replace('__INCOME_DATA__',JSON.stringify(data)).replace('__INCOME_UNIT__',JSON.stringify('万元/年')).replace('__INCOME_BASIS__',JSON.stringify('模拟口径')).replace('__INITIAL_PATH__','"A"');
 vm.runInNewContext(code,context);
 function tick(time){const callbacks=[...queue.values()];queue.clear();callbacks.forEach(f=>f(time))}
 get('allPaths').handlers.click();assert.equal(get('allPaths').attrs['aria-pressed'],'true');assert.equal(messages.filter(m=>m.type==='value-map-path').length,0);
 if(!reduced){assert.equal(queue.size,1);tick(0);tick(1300);for(const k of ['A','B','C']){assert.equal(get('fx-'+k).style.opacity,'1');assert(get('node-'+k+'-2').classes.has('lit'));assert(!get('node-'+k+'-3').classes.has('lit'))}tick(2600);tick(3300)}
 else assert.equal(queue.size,0);
 for(const k of ['A','B','C']){assert.equal(get('trace-'+k).style.strokeDashoffset,0);assert(get('node-'+k+'-5').classes.has('lit'));assert(get('end-'+k).classes.has('lit'))}
 if(equalEnds&&!unknown){const ys=['A','B','C'].map(k=>Number(get('end-'+k).attrs.y)).sort((a,b)=>a-b);assert(ys[1]-ys[0]>=19&&ys[2]-ys[1]>=19)}
 if(unknown){assert.equal(get('app').dataset.view,'branch');assert(views[0].disabled)}
 paths[1].handlers.click();assert.equal(get('allPaths').attrs['aria-pressed'],'false');assert.equal(get('fx-A').style.opacity,'0');assert.equal(get('fx-B').style.opacity,'1');assert.equal(messages.filter(m=>m.type==='value-map-path').length,1);
 console.log('PASS synchronized all paths, single exit, no plan change:',{reduced,equalEnds,unknown});
}
scenario();scenario(true);scenario(false,true);scenario(true,false,true);
