// Simulated DOM only: checks dimension-specific binding and escaping, not visuals.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'examples/projector-report.json'),'utf8'));
const els={};function el(id){return els[id]||(els[id]={textContent:'',innerHTML:'',style:{setProperty(){}},classList:{toggle(){}},setAttribute(){},addEventListener(k,f){this[k]=f},getTotalLength(){return 100},getPointAtLength(x){return {x,y:x}},contentWindow:{postMessage(){}}})}
el('reportData').textContent=JSON.stringify(data);
const keys=['mind','body','spirit','work'];const buttons=keys.map(key=>Object.assign(el('choose-'+key),{dataset:{select:key}}));
const document={getElementById:el,querySelectorAll:selector=>selector==='[data-select]'?buttons:[]};
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/report-runtime.js'),'utf8'),{document,window:{addEventListener(){}},matchMedia:()=>({matches:true,addEventListener(){}}),requestAnimationFrame(){}});
assert(els.dimensionAdvice.innerHTML.includes('最在意的两个条件'));
buttons[1].click();assert(els.dimensionAdvice.innerHTML.includes('沿用这六周有效的安排'));
assert(els.dimDescription.textContent.includes('精神更好'));
buttons[2].click();assert(els.dimensionAdvice.innerHTML.includes('今天已经有安排'));
assert(els.dimDescription.textContent.includes('不好意思拒绝'));
buttons[3].click();assert(els.dimensionAdvice.innerHTML.includes('客户是否确认下一步'));
data.quadrants.spirit.coaching.action.value='<img src=x onerror=alert(1)>';
const altered=JSON.stringify(data);el('reportData').textContent=altered;
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/report-runtime.js'),'utf8'),{document,window:{addEventListener(){}},matchMedia:()=>({matches:true,addEventListener(){}}),requestAnimationFrame(){}});
buttons[2].click();assert(els.dimensionAdvice.innerHTML.includes('&lt;img'));
assert(!els.dimensionAdvice.innerHTML.includes('<img'));
console.log('PASS four different actions and feedback, dimension switching and advice escaping');
