import copy,json,sys
from pathlib import Path
P=Path(__file__).parents[1];sys.path.insert(0,str(P/'scripts'))
from project_income import calculate,project,FIELDS

def c(v):return dict(kind='assumption',value=v,evidence_refs=[],assumption_refs=['H1'],unknown_refs=[])
inputs={k:c(0) for k in FIELDS}
inputs.update(salary_monthly=c(2),paid_months=c(10),bonus=c(1),service_units=c(4),service_unit_price=c(1),service_variable_cost=c(.2),service_fixed_cost=c(.5),hours_per_unit=c(5),service_hours_budget=c(30))
amount,parts=calculate(inputs)
assert abs(amount-23.7)<1e-8
print('PASS: salary + service revenue - explicit costs = 23.7')
bad=copy.deepcopy(inputs);bad['service_hours_budget']['value']=10
try:calculate(bad);raise AssertionError('capacity not checked')
except ValueError:pass
print('PASS: service demand beyond capacity rejected')
missing=copy.deepcopy(inputs);missing['service_variable_cost'].update(value=None,kind='unknown',unknown_refs=['N1'])
assert calculate(missing)[0] is None
print('PASS: unknown cost is not zero')
negative=copy.deepcopy(inputs);negative['service_fixed_cost']['value']=30
assert calculate(negative)[0]<0
print('PASS: negative total contribution allowed')
report=json.loads((P/'tests/sales.json').read_text())
report['assumptions'][0].update(origin='analyst_estimate',accepted=None,rationale='合成测试：根据已给资料提出的参数，不代表真实市场',evidence_refs=['U1'])
for s in report['income_scenarios']:
 s['projection_model']=dict(years=[dict(year=y,inputs=copy.deepcopy(inputs),explanation='合成模型，非真实市场估计') for y in range(1,6)],sensitivity_cases=[])
out=project(report)
assert out['income_scenarios'][0]['annual'][5]['value']==23.7
assert out['income_baseline']['value'] is None
print('PASS: analyst estimates calculated without user-set future income or invented Y0')
print('PASS: all three paths retain Y0-Y5 and unknown baseline')
