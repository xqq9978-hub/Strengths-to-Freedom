from pathlib import Path
import copy,json,sys,re,math
P=Path(__file__).parents[1];sys.path.insert(0,str(P/'scripts'))
from render_boundary import render_boundary
d=json.loads((P/'tests/sales.json').read_text())
d['income_baseline'].update(value=15,kind='fact',evidence_refs=['U1'],unknown_refs=[])
d['boundary_analysis']={'current_role_range':{'low':None,'high':None,'status':'unknown'},'target_role_range':{'low':18,'high':24,'status':'estimate'}}
graph,_=render_boundary(d)
heights=[float(x) for x in re.findall(r'style="height:([\d.]+)px"',graph)]
assert len(heights)==3 and math.isclose(heights[0]/heights[2],15/24,abs_tol=1e-6),heights
assert heights[1]==0 and 'is-unknown' in graph
assert '固定样式' not in graph
s=(P/'assets/report-template.html').read_text();assert s.count('class="wheel-phase-badge"')==4
assert 'fill:#f5fbff!important' in s and 'fill:#07111f' in s
assert '.wheel .sector:focus,.wheel .sector:focus-visible{outline:none!important}' in s
assert 'id="allPaths"' in (P/'assets/income-template.html').read_text()
# Contrast check for text and solid badge background; not an actual screenshot measurement.
def lum(color):
 a=[int(color[i:i+2],16)/255 for i in (0,2,4)];a=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in a]
 return sum(x*y for x,y in zip(a,[.2126,.7152,.0722]))
contrast=(lum('f5fbff')+.05)/(lum('07111f')+.05);assert contrast>12
print('PASS 15:24 known-height ratio, unknown no bar, no internal B label, four independent badges; contrast',round(contrast,2))
