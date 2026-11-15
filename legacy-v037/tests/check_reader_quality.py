import copy,json,sys
from pathlib import Path
P=Path(__file__).parents[1];sys.path.insert(0,str(P/'scripts'))
from audit_report_quality import audit
from render_report import render
import tempfile

d=json.loads((P/'examples/synthetic-report.json').read_text())
assert audit(d)['passed']
tasks=[t for p in d['action_plans'] for t in p['tasks']]
assert len({json.dumps(t['steps'],ensure_ascii=False) for t in tasks})==9
assert len({t['metric'] for t in tasks})==9
cases=[]
def check(name,fn,code):
    sample=copy.deepcopy(d);fn(sample);q=audit(sample)
    assert not q['passed'] and code in [i['code'] for i in q['issues']],(name,q)
    cases.append(dict(name=name,detected=True))
check('相同匹配理由',lambda x:[s.update(fit_reason=copy.deepcopy(x['income_scenarios'][0]['fit_reason'])) for s in x['income_scenarios']],'identical_path_reason')
check('九项同指标',lambda x:[t.update(metric='得到反馈') for p in x['action_plans'] for t in p['tasks']],'all_tasks_share_metric')
check('已知时间仍称未知',lambda x:x['action_plans'][0]['tasks'][0].update(risk='容量未知'),'known_capacity_called_unknown')
check('首周工时超额',lambda x:x['action_plans'][0]['tasks'][0].update(estimated_minutes=999),'plan_exceeds_time')
check('有建议无结论卡',lambda x:x.pop('decision_brief'),'missing_decision_brief')
check('结论引用失效',lambda x:x['decision_brief'].update(evidence_refs=['U999']),'untraceable_decision')
# Rendering legacy limited data preserves all content but marks recommendation quality as limited.
legacy=json.loads((P/'tests/sales.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
    render(legacy,tmp);r=json.loads((Path(tmp)/'report.json').read_text());assert r['reader_quality']['passed'] is False
runtime=(P/'assets/report-runtime.js').read_text()
assert '内部审查结果' not in runtime and 'e.quote' in runtime
assert 'evidence(s.evidence_refs)' not in runtime
print('PASS: nine distinct task steps and metrics, six content regressions detected, limited content not labelled approved')
(P/'tests/reader-quality-tests.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
