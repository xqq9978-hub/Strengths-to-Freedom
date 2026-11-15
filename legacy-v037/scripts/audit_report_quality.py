"""Editorial heuristics. Distinct wording alone does not establish good advice."""
from pathlib import Path
import json,sys

def audit(d):
    issues=[]
    def flag(code,message):issues.append(dict(code=code,message=message))
    scenarios=d['income_scenarios'];plans=d['action_plans'];tasks=[t for p in plans for t in p['tasks']]
    def norm(x):return json.dumps(x,ensure_ascii=False,sort_keys=True)
    if len({norm(s['fit_reason']) for s in scenarios})==1:flag('identical_path_reason','三路匹配理由相同，需分别解释个人依据、门槛与代价。')
    for field in ('steps','metric','completion_rule','feedback_method','fallback'):
        if len({norm(t[field]) for t in tasks})==1:flag('all_tasks_share_'+field,'所有任务共用'+field+'，无法体现阶段或路径差异。')
    weekly=d.get('constraints',{}).get('weekly_minutes',{}).get('value')
    for p in plans:
        previous=0
        for t in p['tasks']:
            if isinstance(weekly,(int,float)) and not isinstance(weekly,bool):
                if '容量未知' in t.get('risk',''):flag('known_capacity_called_unknown',p['path_id']+'已有周时间，任务仍称容量未知。')
                estimated=t.get('estimated_minutes')
                if isinstance(estimated,(int,float)) and estimated>weekly*(t['day']-previous)/7:flag('plan_exceeds_time',p['path_id']+'阶段估时超过可用时间容量。')
            previous=t['day']
    brief=d.get('decision_brief')
    if d.get('recommended_path_id') and not brief:flag('missing_decision_brief','已推荐路径，但缺优先结论简报。')
    if brief:
        if not brief.get('key_condition') or not brief.get('first_action'):flag('incomplete_decision_brief','优先结论缺成立前提或第一步。')
        active={e['id'] for e in d['evidence_index'] if e.get('status')=='active'}
        if not brief.get('evidence_refs') or any(r not in active for r in brief.get('evidence_refs',[])):flag('untraceable_decision','结论简报缺有效证据。')
    coaches=[q.get('coaching') for q in d.get('quadrants',{}).values()]
    if all(coaches) and len({norm(c.get('action',{}).get('value')) for c in coaches})==1:
        flag('identical_quadrant_advice','四维使用完全相同的建议，未结合各维经历。')
    for key,q in d.get('quadrants',{}).items():
        c=q.get('coaching')
        if c:
            for field in ('action','signal'):
                v=c.get(field,{}).get('value')
                if isinstance(v,str) and v.strip('。 ！!') in ('提升能力','设立边界','建立边界','持续成长','继续努力','保持平衡'):
                    flag('generic_quadrant_advice',key+'建议只有抽象词，缺触发情境、动作或反馈。')
    life_status={}
    for scenario in scenarios:
        blueprint=scenario.get('life_blueprint',{})
        missing=[key for key in ('daily_life','work_style','time_and_relationships','tradeoff','curiosity','milestones') if not blueprint.get(key) or (isinstance(blueprint.get(key),dict) and blueprint[key].get('kind')=='unknown')]
        life_status[scenario['id']]={'status':'limited' if missing else 'provided_not_independently_verified','missing_fields':missing}
        gate=scenario.get('growth_checkpoint')
        if gate and any(not gate.get(key) for key in ('obstacle','pass_signal','pause_signal')):
            flag('incomplete_growth_checkpoint',scenario['id']+'增长门槛缺阻碍、过关证据或暂停条件。')
    blueprints=[s.get('life_blueprint') for s in scenarios]
    if all(blueprints) and len({norm(b.get('daily_life')) for b in blueprints})==1:
        flag('identical_life_blueprints','三路生活样貌相同，不能只改路线名称或金额。')
    return dict(passed=not issues,issues=issues,life_blueprints=life_status,note='这是重复与一致性启发式检查，不证明建议精准、证据真实或收入可兑现。')

if __name__=='__main__':
    result=audit(json.loads(Path(sys.argv[1]).read_text()));print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['passed'] else 1)
