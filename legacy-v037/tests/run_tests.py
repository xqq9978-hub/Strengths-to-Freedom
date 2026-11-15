"""Synthetic fixtures + negative mutations; not a Doubao or LLM execution test."""
import copy
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('validator',ROOT/'scripts/validate_report.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
validate=module.validate

def claim(kind,value):
    return dict(kind=kind,value=value,evidence_refs=['U1'] if kind in ('fact','inference') else [],assumption_refs=['H1'] if kind=='assumption' else [],unknown_refs=['N1'] if kind=='unknown' else [])

CASES=[
 dict(id='sales',role='海外销售',statement='我给客户方案和报价，并解释如何组合；未提供结果。',mechanisms=['本职方案交付深化','相邻售前岗位探索','本人愿意时的小型方案验证'],expected='动作可记经历，不能断言成交、定价谈判强或强制推荐陪跑'),
 dict(id='student',role='学生',statement='我在社团整理过报名表，暂时没有工资。',mechanisms=['在校项目实践','实习岗位探索','有意愿时的小型真实任务'],expected='用学习社团经历，不生成任职业绩，不将没工作理解为无优势'),
 dict(id='developer',role='技术岗位',statement='我用AI写过一次脚本，主要由AI生成，我调试了一处错误。',mechanisms=['本职调试能力验证','相邻工具支持角色','小型工具需求验证'],expected='区分AI贡献与本人调试，不写成已熟练掌握完整开发流程'),
 dict(id='freelancer',role='自由设计师',statement='我收到过一次设计费，但不愿说收入，每周时间也不确定。',mechanisms=['现有项目交付改进','相邻设计细分需求','稳定合同组合探索'],expected='不强套工资加副业，年金额未知，工时容量标待确认'),
 dict(id='support',role='行政支持',statement='我只想提高主业工资，不想做副业；曾整理过一次交接清单。',mechanisms=['原岗位责任升级','同类组织岗位迁移','内部轮岗及职责组合'],expected='组合路径可适配内部职责，不强迫副业；一次清单仅初步证据'),
]

def fixture(case):
    u=claim('unknown',None)
    d=dict(schema_version='0.3.7',report_id='SIM-'+case['id'],revision=1,state={'mode':'REPORT','answered_count':1,'question_budget':12,'pending_question':None,'selected_path_id':None,'user_confirmed':False},user_profile={'stage':claim('fact',case['role']),'goal':copy.deepcopy(u),'background':claim('fact',case['statement'])},constraints={'weekly_minutes':copy.deepcopy(u),'budget':copy.deepcopy(u),'risk':copy.deepcopy(u)},quadrants={},strengths=[],events=[],opportunities=[],evidence_index=[dict(id='U1',source_type='synthetic_user',turn=1,quote=case['statement'],status='active',verified=False,url=None,publisher=None,access_date=None,region=None,role=None,basis=None)],unknowns=[dict(id='N1',topic='收入、目标与容量待补',reason='测试输入没有提供',next_check='真实访谈中只补问一个高价值缺口')],assumptions=[dict(id='H1',description='最小实验规划估时，不代表用户空闲容量',accepted=False,reason='测试规划',failure_condition='用户没有时间则缩小或延期')],income_basis=dict(currency='CNY',unit='万元/年',tax_basis='税前工资+副业净贡献',period='annual',composition='口径候选，需用户确认'),income_baseline=copy.deepcopy(u),income_scenarios=[],action_plans=[],selected_path_id=None,recommended_path_id=None,reviews={},reports=[])
    for q in ['mind','body','spirit','vocation']:
        d['quadrants'][q]=dict(life_context=copy.deepcopy(u),development=dict(level=None,phase=None,level_basis='信息不足',phase_basis='信息不足',evidence_refs=[],counterevidence_refs=[],support='insufficient',next_transition='先了解一段真实生活经历',unknown_refs=['N1']),observation=copy.deepcopy(u),evidence_refs=[],potential_strength_ids=[],limitation=copy.deepcopy(u),unknown_refs=['N1'])
    for i,id in enumerate('ABC'):
        d['income_scenarios'].append(dict(id=id,name=case['mechanisms'][i],mechanism=case['mechanisms'][i],status='exploratory',annual=[dict(year=y,formula=None,**copy.deepcopy(u)) for y in range(6)],strength_ids=[],evidence_refs=['U1'],fit_reason=claim('inference','仅是待核实候选，不构成推荐'),capacity_status='unknown',new_capabilities=['待真实实践核实'],market_feedback_needed=['有实际职责方或需求方反馈后再判断'],growth_conditions=['用户认可方向并验证需求'],inflection_reason='取决于后续验证，未设置金额拐点',risk='需求与时间均未验证',continue_condition='获得真实使用反馈且容量允许',stop_condition='与意愿或容量冲突时暂停',unknown_refs=['N1']))
        tasks=[]
        for day in [7,30,90]:
            tasks.append(dict(day=day,name=f'{id}路径第{day}天验证',description=f'围绕“{case["mechanisms"][i]}”开展一个待确认最小实验',strength_ids=[],steps=['选择一件已做过的任务','脱敏整理一页材料','在允许分享且容量允许时请一位熟悉该任务的人反馈'],estimated_minutes=None,estimate_kind='unknown',resources=['现有记录；分享需本人同意'],deliverable='一页经历记录及反馈或明确未获得反馈',metric='能否复述本人贡献和适用条件',completion_rule='材料形成并记录一条反馈，或明确未获得反馈',feedback_method='征得同意后询问熟悉任务的人，不自动联系',risk='容量未知，不承诺日期内必完成',fallback='缩小为一段记录；无法实施则延期并保留未知',assumption_refs=[],unknown_refs=['N1']))
        d['action_plans'].append(dict(path_id=id,hypotheses=['此候选与本人意愿、能力及真实需要是否一致'],tasks=tasks,decision_rules={'continue':'有反馈且愿意继续','adjust':'有反馈但方向不匹配','pause':'容量或意愿不允许'},final_decision=None,decision_status='pending'))
    for key in ('ADVANTAGE_EVIDENCE_AUDITOR','INCOME_PATH_AUDITOR','ACTION_PLAN_AUDITOR'):
        d['reviews'][key]=dict(status='limited',issues=['仅合成少量输入；不作确定推荐或容量通过结论'],evidence_refs=['U1'],unknown_refs=['N1'])
    d['reports']=[dict(id=id,report_id=d['report_id'],revision=1) for id in ('REPORT_01','REPORT_02','REPORT_03')]
    return d

def run():
    result=[]
    for case in CASES:
        data=fixture(case)
        (ROOT/'tests'/f'{case["id"]}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
        errors=validate(data)
        result.append(dict(name=case['id'],type='synthetic_structure',passed=not errors,errors=errors))
    seed=fixture(CASES[0])
    def negative(name,mutate):
        d=copy.deepcopy(seed);mutate(d);errors=validate(d)
        result.append(dict(name=name,type='negative_mutation',passed=bool(errors),errors_detected=errors))
    negative('missing_Y4',lambda d:d['income_scenarios'][0]['annual'].pop(4))
    negative('fake_fact_without_source',lambda d:d['user_profile'].update(goal=dict(kind='fact',value='已成交百万',evidence_refs=[],assumption_refs=[],unknown_refs=[])))
    negative('dangling_evidence',lambda d:d['income_scenarios'][0].update(evidence_refs=['E999']))
    negative('superseded_evidence',lambda d:d['evidence_index'][0].update(status='superseded'))
    negative('unknown_becomes_zero',lambda d:d['income_scenarios'][0]['annual'][1].update(value=0))
    negative('baseline_disagrees',lambda d:d['income_scenarios'][1]['annual'][0].update(value=24))
    negative('all_paths_same',lambda d:[s.update(mechanism='同一个机制') for s in d['income_scenarios']])
    negative('plan_missing_C',lambda d:d['action_plans'].pop())
    negative('plan_missing_day30',lambda d:d['action_plans'][0]['tasks'].pop(1))
    negative('report_stale_revision',lambda d:d['reports'][2].update(revision=0))
    negative('premature_success',lambda d:d['action_plans'][0].update(final_decision='continue'))
    def unaccepted(d):
        d['income_scenarios'][0]['annual'][1].update(claim('assumption',30))
    negative('unaccepted_numeric_assumption',unaccepted)
    def bad_market(d):
        d['user_profile']['goal']=claim('market_reference','岗位年薪中位数50万元')
    negative('unverified_market',bad_market)
    def formula(d):
        d['assumptions'][0]['accepted']=True
        d['income_scenarios'][0]['annual'][1].update(**claim('assumption',30),formula={'operation':'net','inputs':[claim('assumption',30),claim('assumption',5)]})
    negative('revenue_misread_as_net',formula)
    def single_a(d):
        d['events']=[dict(id='E1',evidence_refs=['U1'])]
        d['strengths']=[dict(id='S1',name='组织选项',grade='A',evidence_refs=['U1'],event_refs=['E1'])]
    negative('single_event_is_not_grade_A',single_a)
    numeric=copy.deepcopy(seed)
    numeric['assumptions'][0]['accepted']=True
    numeric['assumptions'][0]['description']='合成用户明确接受的情景参数，仅测试用'
    numeric['income_baseline']=claim('fact',0)
    for i,s in enumerate(numeric['income_scenarios']):
        s['annual'][0].update(claim('fact',0))
        for a in s['annual'][1:]:
            a.update(claim('assumption',a['year']*(i+1)))
    errors=validate(numeric)
    result.append(dict(name='explicit_zero_and_accepted_scenarios',type='synthetic_structure',passed=not errors,errors=errors))
    (ROOT/'tests/explicit-zero.json').write_text(json.dumps(numeric,ensure_ascii=False,indent=2))
    (ROOT/'tests/cases.json').write_text(json.dumps({'note':'全部为合成输入及期望行为，不是豆包运行日志。模板报告用于检验结构，不是高质量个性化结论示范。','professions':CASES,'conversation_scenarios':[
        {'user':'我还没说完','expected':'等待补充，不发新题，不提前解释人格'},
        {'user':'生成报告','expected':'不追加必答题；审查后直接生成HTML，未知仍保留'},
        {'user':'结束','expected':'停止并保存可复制摘要，不追加问句'},
        {'user':'刚才不是我独立做的，是团队做的','expected':'旧证据标superseded，修正个人贡献并重审三模块'},
        {'user':'选择B','expected':'仅切换选择与计划主要展示，不修改收入事实，不自动执行任务'},
        {'user':'不提供收入，也不想做副业','expected':'年值null；适配路径定义，不强制组合副业'},
        {'user':'换个问法','expected':'保持当前主题，用具体记忆入口；不为凑两题增加无关问题'},
        {'user':'五问后出稿','expected':'预算改为5，第5次回答后审查并出稿，不问第6题'}]},ensure_ascii=False,indent=2))
    summary={'scope':'离线合成数据与错误注入；未调用豆包或其他模型','total':len(result),'passed':sum(r['passed'] for r in result),'results':result}
    (ROOT/'tests/results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps({'total':summary['total'],'passed':summary['passed']},ensure_ascii=False))
    assert all(r['passed'] for r in result),result

if __name__=='__main__':run()
