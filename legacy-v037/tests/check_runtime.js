// Minimal DOM simulation: verifies initialization, content binding and path synchronization.
// This is not browser rendering or visual QA.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..');
for(const name of ['sales','student','developer','freelancer','support','explicit-zero']){
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,name+'.json'),'utf8'));
 data.action_plans[1].tasks[0].name='路径B特定任务-'+name;
 const listeners={},els={};let mapButtons=[];const sent=[];
 function element(id){return els[id]||(els[id]={textContent:'',innerHTML:'',style:{setProperty(){}},classList:{toggle(){}},setAttribute(){},addEventListener(k,f){this[k]=f},getTotalLength(){return 100},getPointAtLength(x){return{x,y:x}},contentWindow:{postMessage(){}}})}
 element('reportData').textContent=JSON.stringify(data);
 element('incomeFrame').contentWindow.postMessage=m=>sent.push(m);
 mapButtons=['A','B','C'].map(id=>Object.assign(element('map-'+id),{dataset:{mapPath:id}}));
 const document={getElementById:element,querySelectorAll(selector){return selector==='[data-map-path]'?mapButtons:[]}};
 const window={addEventListener(k,f){listeners[k]=f}};
 const context={document,window,matchMedia:()=>({matches:true,addEventListener(){}}),requestAnimationFrame(){}};
 vm.runInNewContext(fs.readFileSync(path.join(root,'assets/report-runtime.js'),'utf8'),context);
 assert(els.profileSummary.textContent.includes(data.user_profile.stage.value));
 assert(els.reportNotice.textContent.includes('合成演示'));
 listeners.message({source:els.incomeFrame.contentWindow,data:{type:'value-map-path',path:'B'}});
 assert.equal(els.stageTitle.textContent,'路径B特定任务-'+name);
 assert(els.planSelection.textContent.includes('B'));
 const before=els.stageTitle.textContent;
 listeners.message({source:{},data:{type:'value-map-path',path:'A'}});
 assert.equal(els.stageTitle.textContent,before);
 assert(els.mapPathControls.innerHTML.includes('data-map-path="C"'));
 mapButtons[2].click();
 assert(els.planSelection.textContent.includes('当前查看 C'));
 assert(els.stageTitle.textContent===data.action_plans[2].tasks[0].name);
 assert(sent.at(-1).type==='value-map-select'&&sent.at(-1).path==='C');
 console.log('PASS content and B-plan sync: '+name);
}
