import copy,json,sys
from pathlib import Path
P=Path(__file__).parents[1];sys.path.insert(0,str(P/'scripts'))
from validate_report import validate
from render_boundary import render_boundary,bands
data=json.loads((P/'tests/sales.json').read_text())
data['report_id']='SYNTHETIC-boundary-check'
for r in data['reports']:r['report_id']=data['report_id']
unknown={'low':None,'high':None,'status':'unknown','unit':data['income_basis']['unit'],'source_refs':[],'assumption_refs':[],'scope':'待核验','comparability_note':'尚无资料'}
b=dict(current_structure='合成测试',personal_evidence_refs=['U1'],current_role_range=copy.deepcopy(unknown),target_role_range=copy.deepcopy(unknown),gap_analysis=[],transition_conditions=['需验证真实职责'],validation_plan='先交付一个真实任务',path_id='B',limitations=['没有市场样本'])
data['boundary_analysis']=b
assert not validate(data)
graph,proof=render_boundary(data)
assert 'data-scaled="false"' in graph
assert 'data-boundary-plan="B"' in proof
assert '没有可用的岗位薪酬样本' in proof
print('PASS unknown ranges do not invent steps; validation link points to B')
tests=[]
def negative(name,change):
 d=copy.deepcopy(data);change(d);errors=validate(d);assert errors,name;tests.append(dict(name=name,passed=True,errors=errors))
negative('reference_without_salary_source',lambda d:d['boundary_analysis']['current_role_range'].update(low=20,high=28,status='reference'))
negative('range_not_ordered',lambda d:d['boundary_analysis']['current_role_range'].update(low=28,high=20,status='estimate',assumption_refs=['H1']))
negative('mixed_unit',lambda d:d['boundary_analysis']['current_role_range'].update(unit='美元/月'))
negative('unknown_with_amount',lambda d:d['boundary_analysis']['current_role_range'].update(high=28))
def macro(d):
 d['evidence_index'].append(dict(id='M1',status='active',source_type='synthetic_market',verified=True,url='https://www.stats.gov.cn/zs/tjws/tjzb/202301/t20230101_1903795.html',publisher='统计口径说明，非薪资样本',access_date='2026-11-12',region='全国',role='非特定岗位',basis='统计方法',sample_type='macro_method',source_group='stats',quote='合成测试：方法页不能当个人岗位薪资数据'))
 d['boundary_analysis']['current_role_range'].update(status='limited',source_refs=['M1'],comparability_note='测试不得使用方法页')
negative('macro_method_is_not_salary_evidence',macro)
simulation=copy.deepcopy(data)
simulation['income_baseline'].update(value=24,kind='fact',evidence_refs=['U1'],unknown_refs=[])
for s in simulation['income_scenarios']:s['annual'][0].update(value=24,kind='fact',evidence_refs=['U1'],unknown_refs=[])
for key,lo,hi in [('current_role_range',22,28),('target_role_range',30,38)]:simulation['boundary_analysis'][key].update(low=lo,high=hi,status='simulation')
assert not validate(simulation)
graph,proof=render_boundary(simulation)
assert 'data-scaled="true"' in graph and '虚构演示' in graph
assert 'observed' not in bands('mind',None)
assert bands('mind',2,'discovery').count('level-band observed')==6
print('PASS labelled demo scales consistently; unknown rings empty; level 2 stops at ring 2')
print('PASS five injected boundary errors rejected')
(P/'tests/boundary-results.json').write_text(json.dumps(tests,ensure_ascii=False,indent=2))
