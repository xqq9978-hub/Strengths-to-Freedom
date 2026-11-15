(()=>{
'use strict';
const $=id=>document.getElementById(id),R=JSON.parse($('reportData').textContent);
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names={weekly_minutes:'每周可用分钟',budget:'预算',risk:'风险边界',cross_dimension_observations:'跨维度观察',priority_issue:'优先问题',continue:'继续',adjust:'调整',pause:'暂停',proposed:'待验证',unknown:'未知',planning_assumption:'规划估时',pending:'等待反馈',tentative:'暂定观察'};
function text(v){if(v==null)return '尚未了解';if(Array.isArray(v))return v.length?v.map(text).join('；'):'暂无';if(typeof v==='object'){if('value'in v)return text(v.value);return Object.entries(v).map(([k,x])=>(names[k]?names[k]+'：':'')+text(x)).join('；')}return names[v]||String(v)}
const fields=pairs=>'<dl>'+pairs.filter(([,v])=>v!==undefined).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(text(v))}</dd>`).join('')+'</dl>';
const details=(title,body)=>`<details><summary>${esc(title)}</summary>${body}</details>`;
const refLinks=refs=>(refs||[]).filter(id=>R.evidence_index.some(e=>e.id===id)).map((id,i)=>`<a class="evidence-link" href="#ev-${esc(encodeURIComponent(id))}">经历依据${i+1}</a>`).join(' · ');
const unknown=refs=>(refs||[]).map(id=>R.unknowns.find(u=>u.id===id)).filter(Boolean).map(u=>u.topic+'：'+u.reason).join('；');
const dims={mind:['心智','理解与判断','#ff9f92'],body:['身体与精力','持续发挥','#79aaf8'],spirit:['关系与价值','在意与连接','#56dfcf'],work:['事业与创造','价值与回报','#c1ec87']};
const phases={dissonance:'失调',uncertainty:'探索',discovery:'发现'};
const synthetic=R.evidence_index.some(e=>e.source_type?.startsWith('synthetic'));
$('reportNotice').textContent=synthetic?'合成演示：经历、金额与建议仅用于检查报告，不是你的个人结论。':'本报告依据本次访谈；收入为条件情景，关键假设和资料缺口随结论标注。';
$('reportStatus').textContent=synthetic?'模拟访谈 · 非本人报告':'个人访谈报告';
$('profileSummary').textContent=`${text(R.user_profile.stage)}。希望：${text(R.user_profile.goal)}。`;
function dimension(key){const [short,label,color]=dims[key],q=R.quadrants[key==='work'?'vocation':key],dev=q.development||{};
 document.querySelectorAll('[data-dim]').forEach(el=>{const on=el.dataset.dim===key;el.classList.toggle('active',on);el.setAttribute('aria-pressed',String(on))});
 document.querySelectorAll('[data-select]').forEach(el=>{el.setAttribute('aria-pressed',String(el.dataset.select===key));el.style.setProperty('--active',color)});
 $('dimensionPanel').style.setProperty('--dim-color',color);$('centerLabel').textContent=short;$('dimTitle').textContent=short+' · '+label;$('dimStatus').textContent='从你讲的经历来看';
 const coaching=q.coaching||{};
 $('dimDescription').textContent=text(coaching.judgment||q.reader_summary||q.observation);
 $('phaseTrack').innerHTML=Object.entries(phases).map(([p,n])=>`<span class="phase-step ${dev.phase===p?'current':''}"><b>${n}</b></span>`).join('');
 const stageMeaning={dissonance:'原来的做法最近不太管用了，先找出最具体的卡点。',uncertainty:'你已经在试新做法，接下来要看它在什么情况下有效。',discovery:'新做法已经几次起作用，接下来先把它保留下来。'};
 $('phaseMeaning').textContent=dev.phase?(coaching.stage_reading||stageMeaning[dev.phase]):'这次还看不出你处在哪个阶段，先从一件实际经历了解。';
 $('phaseLevel').textContent=dev.level?`暂定 ${dev.level}.0 · ${phases[dev.phase]||'阶段待了解'}，只表示本次访谈中的观察`:'层级还不能判断，外圈留空；内侧细弧显示当前阶段' ;
 $('dimensionAdvice').innerHTML=coaching.action?`<h4>接下来，先做这一件事</h4><p>${esc(text(coaching.action))}</p><p><small>留意什么变化</small><br>${esc(text(coaching.signal))}</p>`+details('为什么先做这件事',fields([['从经历看',coaching.bottleneck],['Human 3.0参考',coaching.framework_reason],['什么情况要调整',coaching.reconsider_if]])):`<h4>下一步</h4><p>${esc(dev.next_transition||'先找一件最近发生的事，说说你做了什么、后来怎样。')}</p><p class="reader-note">这版旧数据还没有完整的个人建议，需要结合经历补充，不能用阶段标签代替。</p>`;
 $('dimEvidence').innerHTML=refLinks(dev.evidence_refs?.length?dev.evidence_refs:q.evidence_refs)||'本次尚无足够经历依据';
 $('dimNext').innerHTML=details('展开适用边界与定位依据',fields([['适用边界',q.limitation],['层级依据',dev.level_basis],['阶段依据',dev.phase_basis],['生活场景',q.life_context],['仍需了解',unknown(q.unknown_refs)]]));
}
document.querySelectorAll('[data-dim]').forEach(el=>{el.addEventListener('click',()=>dimension(el.dataset.dim));el.addEventListener('keydown',e=>{const keys=Object.keys(dims);if(['Enter',' '].includes(e.key)){e.preventDefault();dimension(el.dataset.dim)}else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();const delta=['ArrowLeft','ArrowUp'].includes(e.key)?-1:1,key=keys[(keys.indexOf(el.dataset.dim)+delta+4)%4];dimension(key);document.querySelector('[data-dim="'+key+'"]').focus()}})});
document.querySelectorAll('[data-select]').forEach(el=>el.addEventListener('click',()=>dimension(el.dataset.select)));
Object.keys(dims).forEach(key=>{const dev=R.quadrants[key==='work'?'vocation':key].development||{};if($('wheel-phase-'+key))$('wheel-phase-'+key).textContent=phases[dev.phase]||'未定位'});dimension('mind');
const grade={A:'证据较充分',B:'初步支持',C:'待验证线索'};
$('strengthDetails').innerHTML=R.strengths.length?R.strengths.map(s=>`<article class="reader-strength"><small>${grade[s.grade]||'待验证'}</small><h3>${esc(s.name)}</h3><p>${esc(text(s.reader_summary||s.explanation))}</p><p>适用：${esc(text(s.application_contexts))}</p><p>边界：${esc(text(s.boundaries))}</p>${refLinks(s.evidence_refs)}</article>`).join(''):'<p class="reader-note">目前还不能确定可重复的优势，本轮先验证已有线索。</p>';
$('strengthDetails').innerHTML+=details('生活约束与跨维度观察',fields([['生活约束',R.constraints],['跨维度观察',R.analysis?.cross_dimension_observations],['优先问题',R.analysis?.priority_issue]]));
let selected=R.selected_path_id||R.recommended_path_id||'A',stage=0,playing=false,progress=0,last=null;
const frame=$('incomeFrame'),paths=[0,1,2].map(i=>$('segment'+i)),reduced=matchMedia('(prefers-reduced-motion: reduce)'),colors=['#65ded0','#b8a6fa','#c1ec87'];
function brief(){const b=R.decision_brief||{},rec=R.reader_quality?.passed===false?undefined:R.income_scenarios.find(s=>s.id===R.recommended_path_id),p=R.action_plans.find(p=>p.path_id===rec?.id);
 $('decisionBrief').innerHTML=`<small>${rec?'优先验证建议 · '+esc(rec.id+' '+rec.name):(R.reader_quality?.passed===false?'内容初稿：路径与行动建议仍需复核':'当前不急于选定唯一路径')}</small><h3>${esc(b.headline||(rec?'先验证这条路是否符合你的实际条件':'先核实关键缺口，再比较三条选择'))}</h3>`+refLinks(b.evidence_refs)+details('何时调整这项建议',esc(text(b.change_trigger||'新证据或本人约束改变时重新评估')));
}
brief();
function valueMap(){const s=R.income_scenarios.find(s=>s.id===selected),p=R.action_plans.find(p=>p.path_id===selected),st=s.strength_ids.map(id=>R.strengths.find(x=>x.id===id)).filter(Boolean),m=s.value_map||{};
 $('valueMapChain').innerHTML=[['优势',st.map(x=>x.name).join('、')||'先验证已有线索'],['服务谁/适用谁',m.audience||s.name],['交付什么',m.deliverable||p.tasks[0].deliverable],['收入怎样形成',m.income_mechanism||s.mechanism],['先检验什么',m.first_test||p.hypotheses[0]]].map(([a,b])=>`<article><small>${esc(a)}</small><h3>${esc(text(b))}</h3></article>`).join('');
}
function pathDetails(){const s=R.income_scenarios.find(s=>s.id===selected),b=s.life_blueprint||{},g=s.growth_checkpoint||{};
 const life=b.daily_life||'访谈未覆盖这条路的日常生活，先核实时间、地点与关系安排。';
 $('pathDetails').innerHTML=`<p class="life-route-summary">${esc(s.id+' · '+s.name)}：${esc(text(life))}</p>`+
 '<div class="reader-path">'+[['为什么适合你',s.fit_reason],['收入靠什么变化',s.mechanism],['你要付出的代价',b.tradeoff||s.reader_cost||s.risk]].map(([a,b])=>`<article><small>${esc(a)}</small><p>${esc(text(b))}</p></article>`).join('')+'</div>'+
 `<div class="path-checkpoint"><small>这条路先过哪一关</small><p>${esc(text(g.obstacle||s.new_capabilities))}</p><p>过关证据：${esc(text(g.pass_signal||'尚未定义；需要真实对象、产物和反馈标准，不能仅凭自我感觉判定'))}</p><p>回退信号：${esc(text(g.pause_signal||s.stop_condition))}</p></div>`+refLinks(s.evidence_refs)+
 details('展开五年生活蓝图与待解问题',fields([['未来工作方式',b.work_style||'待补访谈'],['时间与关系安排',b.time_and_relationships||'待补访谈'],['这条路想验证的问题',b.curiosity||'待补访谈'],['第1 / 3 / 5年',b.milestones||'尚未形成生活里程碑'],['定位与边界',b.status_note||'当前为职业走法候选，尚不足以称完整奥德赛人生蓝图'],['生活信息缺口',unknown(b.unknown_refs)]]))+
 details('查看年度金额与本路测算前提',fields([['各年收入',s.annual.map(a=>(a.year?'第'+a.year+'年':'现在')+'：'+(a.value===null?'金额待定':Number(a.value).toFixed(2)+' '+R.income_basis.unit)).join('\n')],['转折条件',s.growth_conditions],['本路假设',R.assumptions.filter(h=>(s.assumption_refs||[]).includes(h.id)||s.annual.some(a=>(a.assumption_refs||[]).includes(h.id))).map(h=>h.description)],['本路缺口',unknown(s.unknown_refs)]]));
}

function task(){const plan=R.action_plans.find(p=>p.path_id===selected),t=plan.tasks[stage];
 document.querySelectorAll('[data-stage]').forEach(el=>el.setAttribute('aria-pressed',String(Number(el.dataset.stage)===stage)));
 $('stageDetail').style.setProperty('--stage-color',colors[stage]);$('stageTime').textContent=t.day+' 天';$('stageTitle').textContent=t.name;
 const time=t.estimated_minutes===null?'待确认':`${t.estimated_minutes}分钟 · ${t.time_scope||'本阶段累计规划估时'}`;
 $('stageText').innerHTML='<div class="reader-task">'+fields([['做什么',t.steps],['交付什么',t.deliverable],['看什么反馈',t.feedback_target?`${t.feedback_target}；${t.metric}`:t.metric],['投入多少',time],['怎样复盘',t.review_condition||t.completion_rule]])+'</div>'+details('资源、风险与未完成时的调整',fields([['资源',t.resources],['风险',t.risk],['调整',t.fallback],['待确认',unknown(t.unknown_refs)]]));
 $('planDecision').innerHTML=details('本轮实验：继续、调整或暂停',fields([['要验证的判断',plan.hypotheses],['决策标准',plan.decision_rules],['真实结果',plan.decision_status==='pending'?'等待实际执行与反馈':plan.final_decision]]));
}
function sync(){$('toggleMotion').textContent=playing?'暂停动画':'播放动画';$('toggleMotion').setAttribute('aria-pressed',String(!playing));last=null}
function place(){const p=paths[stage],point=p.getPointAtLength(p.getTotalLength()*Math.max(0,Math.min(1,progress)));$('traveler').setAttribute('transform',`translate(${point.x} ${point.y})`);paths.forEach((x,i)=>x.classList.toggle('active',i===stage))}
function selectPath(id,notify=true){if(!R.income_scenarios.some(s=>s.id===id))return;selected=id;stage=0;progress=0;playing=false;sync();
 $('planPathControls').innerHTML=R.income_scenarios.map(s=>`<button data-plan-path="${s.id}" aria-pressed="${s.id===id}">${esc(s.id+' '+s.name)}</button>`).join('');
 document.querySelectorAll('[data-plan-path]').forEach(b=>b.addEventListener('click',()=>selectPath(b.dataset.planPath)));
 $('planSelection').textContent=`当前查看 ${id}；`+(R.selected_path_id?'本人选择 '+R.selected_path_id:'本人尚未选择')+(R.reader_quality?.passed===false?'，建议仍待复核':R.recommended_path_id?'，优先验证建议 '+R.recommended_path_id:'，暂不推荐唯一路径')+'。';
 $('mapPathControls').innerHTML=R.income_scenarios.map(s=>`<button data-map-path="${s.id}" aria-pressed="${s.id===id}">${esc(s.id+' '+s.name)}</button>`).join('');document.querySelectorAll('[data-map-path]').forEach(b=>b.addEventListener('click',()=>selectPath(b.dataset.mapPath)));
 const p=R.action_plans.find(p=>p.path_id===id);$('stageButtons').innerHTML=p.tasks.map((t,i)=>`<button class="stage" data-stage="${i}" aria-pressed="${i===stage}" style="--stage-color:${colors[i]}"><span class="day">DAY ${t.day}</span><strong>${esc(t.name)}</strong></button>`).join('');
 document.querySelectorAll('[data-stage]').forEach(b=>b.addEventListener('click',()=>{stage=Number(b.dataset.stage);progress=0;playing=false;sync();task();place()}));pathDetails();valueMap();task();place();if(notify)frame.contentWindow?.postMessage({type:'value-map-select',path:id},'*');
}
window.addEventListener('message',e=>{if(e.source!==frame.contentWindow)return;if(e.data?.type==='value-map-path'&&['A','B','C'].includes(e.data.path))selectPath(e.data.path,false);if(e.data?.type==='value-map-size'&&Number.isFinite(e.data.height))frame.style.height=Math.max(500,Math.min(8000,e.data.height))+'px'});
$('toggleMotion').addEventListener('click',()=>{if(!playing&&stage===2&&progress>=1){stage=0;progress=0;task()}playing=!playing;sync()});
$('restartMotion').addEventListener('click',()=>{stage=0;progress=0;playing=!reduced.matches;sync();task();place()});
function animate(now){if(playing){if(last!==null){progress+=(now-last)/6000;if(progress>=1){if(stage===2){progress=1;playing=false;sync()}else{stage++;progress=0;task()}}place()}last=now}else last=null;requestAnimationFrame(animate)}
reduced.addEventListener?.('change',()=>{if(reduced.matches){playing=false;sync()}});selectPath(selected,false);document.querySelectorAll('[data-boundary-plan]').forEach(a=>a.addEventListener('click',()=>selectPath(a.dataset.boundaryPlan)));requestAnimationFrame(animate);
document.addEventListener?.('click',event=>{const a=event.target.closest?.('a.evidence-link');if(!a)return;const target=document.getElementById(a.getAttribute('href').slice(1));if(!target)return;for(let node=target.parentElement;node;node=node.parentElement){if(node.tagName==='DETAILS')node.open=true}});
const allEvidence=R.evidence_index.map(e=>{const url=e.url&&/^https?:\/\//i.test(e.url)?`<a class="reader-source" href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">打开原始来源</a>`:'';return `<article class="evidence-entry" id="ev-${esc(encodeURIComponent(e.id))}"><small>${e.verified?'外部资料已核查':'本人陈述或未独立核查'} · ${esc(e.id)}</small><p>${esc(e.quote)}</p>${url}${e.publisher||e.region?'<p class="reader-note">'+esc([e.publisher,e.access_date,e.region,e.role,e.basis].filter(Boolean).join(' · '))+'</p>':''}</article>`}).join('');
$('evidenceDetails').innerHTML=details('查看经历与来源',allEvidence)+details('仍需了解的信息',R.unknowns.map(u=>fields([['缺口',u.topic],['原因',u.reason],['下一步核实',u.next_check]])).join(''))+details('方法参考', '<p class="reader-note">以下只解释分析口径，不作为本人的工资样本。</p><p><a class="reader-source" href="https://www.stats.gov.cn/zs/tjws/tjzb/202301/t20230101_1903795.html" target="_blank" rel="noopener noreferrer">国家统计局：平均工资口径</a></p><p><a class="reader-source" href="https://handbook.gitlab.com/handbook/total-rewards/compensation/" target="_blank" rel="noopener noreferrer">GitLab：岗位、级别与地区薪酬匹配方法</a></p><p><a class="reader-source" href="https://thedankoe.com/letters/a-complete-knowledge-base-of-human-3-0/" target="_blank" rel="noopener noreferrer">Dan Koe：Human 3.0公开框架</a><br>四维与阶段仅作访谈参考，具体建议是结合本次经历的应用，不是官方测评或收入依据。</p>');
})();
