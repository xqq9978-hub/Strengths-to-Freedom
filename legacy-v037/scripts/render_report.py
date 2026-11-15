"""Generate one offline HTML report using the supplied visual references."""
import html
import json
from pathlib import Path
import sys
import copy
from validate_report import validate
from render_boundary import render_boundary,bands
from render_reader_proof import proof as reader_proof
from audit_report_quality import audit

ROOT=Path(__file__).parents[1]

def safe_json(value):
    return json.dumps(value,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')

def render(data,destination):
    errors=validate(data)
    if errors:
        raise ValueError('Report did not pass validation: '+ '; '.join(errors))
    data=copy.deepcopy(data)
    data['reader_quality']=audit(data)
    selected=data.get('selected_path_id') or data.get('recommended_path_id') or 'A'
    colors=['#79b5ff','#f3cd7c','#89d5b1']
    routes={s['id']:dict(name=s['name'],color=colors[i],values=[a['value'] for a in s['annual']],steps=[t['name'] for t in next(p for p in data['action_plans'] if p['path_id']==s['id'])['tasks']]) for i,s in enumerate(data['income_scenarios'])}
    unit=data['income_basis']['unit']
    basis='；'.join(f'{k}：{data["income_basis"].get(k,"未知")}' for k in ('currency','unit','tax_basis','period','composition'))
    choices='<div class="choices" role="group" aria-label="选择路径">'
    for id,r in routes.items():
        value='金额待定' if r['values'][5] is None else str(r['values'][5])
        choices+=f'<button class="choice" data-path="{id}" style="--c:{r["color"]}" aria-pressed="{str(id==selected).lower()}"><div class="choice-top"><span class="letter">PATH {id}</span><span class="radio" aria-hidden="true"></span></div><div class="choice-name">{html.escape(r["name"])}</div><div class="choice-foot"><span><b>{value}</b> {html.escape(unit)}</span></div></button>'
    choices+='</div>'
    income=(ROOT/'assets/income-template.html').read_text().replace('__INCOME_RUNTIME__',(ROOT/'assets/income-runtime.js').read_text())
    # Replace fixed template slots before inserting user-controlled JSON.
    for key,val in [('__INCOME_CHOICES__',choices),('__UNIT_TEXT__',html.escape(unit)),('__INCOME_UNIT__',safe_json(unit)),('__INCOME_BASIS__',safe_json(basis)),('__INITIAL_PATH__',safe_json(selected))]:
        income=income.replace(key,val)
    income=income.replace('__INCOME_DATA__',safe_json(routes))
    shell=(ROOT/'assets/report-template.html').read_text()
    graph,proof=render_boundary(data)
    proof=reader_proof(data)
    shell=shell.replace('__BOUNDARY_GRAPH__',graph).replace('__BOUNDARY_PROOF__',proof)
    for key in ('mind','body','spirit','work'):
        q=data['quadrants']['vocation' if key=='work' else key]
        shell=shell.replace('__BANDS_'+key.upper()+'__',bands(key,q.get('development',{}).get('level'),q.get('development',{}).get('phase')))
    shell=shell.replace('__REPORT_RUNTIME__',(ROOT/'assets/report-runtime.js').read_text())
    shell=shell.replace('__INCOME_DOCUMENT__',html.escape(income,quote=True))
    shell=shell.replace('__REPORT_DATA__',safe_json(data))
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    (destination/'report.html').write_text(shell)
    (destination/'report.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False))
    return destination/'report.html'

if __name__=='__main__':
    try:
        print(render(json.loads(Path(sys.argv[1]).read_text()),sys.argv[2]))
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        print('Generation failed: '+str(exc),file=sys.stderr);sys.exit(1)
