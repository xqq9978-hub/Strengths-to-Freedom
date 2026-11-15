from pathlib import Path
from html.parser import HTMLParser
import copy,json,re,sys,tempfile
P=Path(__file__).parents[1];sys.path.insert(0,str(P/'scripts'))
from validate_report import validate
from render_report import render
from audit_report_quality import audit
d=json.loads((P/'examples/projector-report.json').read_text())
assert not validate(d),validate(d)
assert audit(d)['passed']
for key,q in d['quadrants'].items():
 c=q['coaching'];assert c['phase']==q['development']['phase']
 assert c['judgment']['evidence_refs'] and c['action']['assumption_refs']
 for field in ['judgment','bottleneck']:
  assert '邀约和消息边界还不稳定' not in c[field]['value']
assert '朋友' in d['quadrants']['spirit']['coaching']['judgment']['value']
assert '工作消息' not in d['quadrants']['spirit']['coaching']['judgment']['value']
assert d['quadrants']['body']['coaching']['approach']=='consolidate'
def rejected(fn):
 x=copy.deepcopy(d);fn(x);assert validate(x)
rejected(lambda x:x['quadrants']['body']['coaching'].update(phase='uncertainty'))
rejected(lambda x:x['quadrants']['body']['coaching'].update(approach='experiment'))
rejected(lambda x:x['quadrants']['spirit']['coaching']['judgment'].update(evidence_refs=[]))
rejected(lambda x:x['quadrants']['mind']['coaching']['action'].update(assumption_refs=['MISSING']))
x=copy.deepcopy(d)
for q in x['quadrants'].values():q['coaching']['action']['value']='提升能力'
codes={i['code'] for i in audit(x)['issues']};assert {'generic_quadrant_advice','identical_quadrant_advice'}<=codes
with tempfile.TemporaryDirectory() as tmp:
 doc=render(d,tmp).read_text()
 route=re.search(r'<div class="reading-breadcrumb"[^>]*>(.*?)</div>',doc,re.S).group(1)
 links=re.findall(r'<a href="([^"]+)">([^<]+)</a>',route)
 assert links==[('#future','01 收入可能'),('#profile','02 认识自己'),('#valueMap','03 变现与行动')],links
 assert '02 收入台阶' not in route
 assert 'id="dimensionAdvice"' in doc and 'id="phaseNext"' not in doc
print('PASS three-step breadcrumb, sourced advice, stage-specific approach; four invalid cases and generic advice rejected')
