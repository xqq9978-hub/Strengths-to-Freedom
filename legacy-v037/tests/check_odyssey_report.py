from pathlib import Path
from html.parser import HTMLParser
import sys,copy,json,tempfile
P=Path(__file__).parents[1];sys.path.insert(0,str(P/'scripts'))
from render_boundary import bands
from render_report import render
from audit_report_quality import audit
from validate_report import validate
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.paths=[];self.sections=[];self.boundary_tag=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='path':self.paths.append(a)
  if tag=='section' and a.get('id'):self.sections.append(a['id'])
  if a.get('id')=='incomeBoundary':self.boundary_tag=tag
def counts(level,phase):
 s=Scan();s.feed(bands('body',level,phase))
 return [sum('level-band observed' in p.get('class','') and p.get('data-level')==str(i) for p in s.paths) for i in [1,2,3]],sum('phase-band observed' in p.get('class','') for p in s.paths)
assert counts(None,'discovery')==([0,0,0],3)
assert counts(2,'uncertainty')==([3,2,0],2)
assert counts(2,'discovery')==([3,3,0],3)
assert counts(3,'discovery')==([3,3,3],3)
assert counts(None,None)==([0,0,0],0)
assert counts(2,None)==([3,0,0],0)
d=json.loads((P/'examples/projector-report.json').read_text())
assert not validate(d),validate(d)
q=audit(d);assert q['passed'];assert all(v['status']=='limited' and 'milestones' in v['missing_fields'] for v in q['life_blueprints'].values())
bad=copy.deepcopy(d);bad['income_scenarios'][0]['growth_checkpoint'].pop('pass_signal');assert validate(bad)
bad=copy.deepcopy(d);bad['income_scenarios'][0]['growth_checkpoint']['pass_signal']['assumption_refs']=['INVALID'];assert validate(bad)
bad=copy.deepcopy(d)
for s in bad['income_scenarios']:s['life_blueprint']['daily_life']=copy.deepcopy(d['income_scenarios'][0]['life_blueprint']['daily_life'])
assert any(i['code']=='identical_life_blueprints' for i in audit(bad)['issues'])
with tempfile.TemporaryDirectory() as tmp:
 doc=render(d,tmp).read_text();s=Scan();s.feed(doc)
 assert s.sections==['future','profile','valueMap'],s.sections
 assert s.boundary_tag=='details'
 assert 'id="mapPathControls"' in doc
 # Paint order: the central disc must not hide the new inner phase arc (r111-130).
 assert '<circle cx="300" cy="300" r="104"' in doc
 assert d['quadrants']['body']['development']['level'] is None
 assert [a['value'] for a in d['income_scenarios'][0]['annual']]==[15,15.6,16.8,18,19.2,20.4]
print('PASS phase/level geometry, unknown discovery full inner arc, 3-part report, explicit ABC map, life-data limits and negative provenance cases')
