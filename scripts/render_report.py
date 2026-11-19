#!/usr/bin/env python3
"""Render V1.1 standalone report from validated 0.4.0 data; standard library only."""
import sys,json,html,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def validate(d):
 def fail(s): raise ValueError(s)
 def obj(x,p):
  if not isinstance(x,dict):fail(p+' 必须是对象')
 def arr(x,p,n=None):
  if not isinstance(x,list) or (n is not None and len(x)!=n):fail(p+' 数组长度不合要求')
 def fields(x,p,fields):
  obj(x,p)
  for k in fields:
   if k not in x:fail(p+' 缺少 '+k)
 def txt(x,p,nullable=True):
  if not isinstance(x,str) and not (nullable and x is None):fail(p+' 应为文本'+('或 null' if nullable else ''))
 def texts(o,p,keys):
  for k in keys: txt(o[k],p+'.'+k)
 fields(d,'报告',['schema_version','meta','evidence','vision','starting','dimensions','strengths','paths'])
 if d['schema_version']!='0.4.0':fail('schema_version 必须为 0.4.0')
 m=d['meta'];fields(m,'meta',['demo','income_unit','income_basis','selected_path','recommended_path']);
 if not isinstance(m['demo'],bool): fail('meta.demo 必须是布尔值')
 texts(m,'meta',['income_unit','income_basis']);
 if m['selected_path'] not in (None,'A','B','C') or m['recommended_path'] not in (None,'A','B','C'):fail('路径选择必须为 A/B/C 或 null')
 arr(d['evidence'],'evidence');lookup={}
 for e in d['evidence']:
  fields(e,'evidence',['id','kind','quote','url','access_date']);texts(e,'evidence',['id','kind','quote','url','access_date']);
  if not e['id'] or e['id'] in lookup or e['kind'] not in ('user','market'):fail('证据 ID 需唯一且 kind 为 user / market')
  if e['url'] and not re.match(r'^https?://',e['url'],re.I): fail('来源 URL 只允许 http/https')
  lookup[e['id']]=e
 def refs(o,p):
  arr(o['evidence_refs'],p+'.evidence_refs')
  if any(not isinstance(x,str) or x not in lookup for x in o['evidence_refs']):fail(p+' 包含不存在的证据 ID')
 v=d['vision'];fields(v,'vision',['words','priority','boundaries']);arr(v['words'],'vision.words');arr(v['boundaries'],'vision.boundaries')
 if len(v['words'])>6:fail('愿景最多6项')
 if v['priority'] is not None and (type(v['priority'])!=int or not 0<=v['priority']<len(v['words'])):fail('priority 应为有效下标或 null')
 for x in v['boundaries']:txt(x,'boundary',False)
 for x in v['words']:
  fields(x,'word',['title','meaning','quote','evidence_refs']);txt(x['title'],'word.title',False);texts(x,'word',['meaning','quote']);refs(x,'word')
 s=d['starting'];fields(s,'starting',['title','observation','nodes','stats','caveat']);texts(s,'starting',['title','observation','caveat']);arr(s['nodes'],'starting.nodes',3);arr(s['stats'],'starting.stats')
 for x in s['nodes']:
  fields(x,'node',['label','title','summary','detail','evidence_refs']);texts(x,'node',['label','title','summary','detail']);refs(x,'node')
 for x in s['stats']:
  fields(x,'stat',['label','value']);texts(x,'stat',['label','value'])
 fields(d['dimensions'],'dimensions',['mind','body','spirit','vocation'])
 for k,x in d['dimensions'].items():
  fields(x,'dimension.'+k,['observation','action','signal','limit','detail','phase','level','evidence_refs']);texts(x,'dimension',['observation','action','signal','limit','detail']);refs(x,'dimension')
  if x['phase'] not in (None,'dissonance','uncertainty','discovery') or (x['level'] is not None and (type(x['level'])!=int or x['level'] not in (1,2,3))): fail('维度阶段或层级无效')
 arr(d['strengths'],'strengths');
 if len(d['strengths'])>3:fail('最多3项优势')
 for x in d['strengths']:
  fields(x,'strength',['name','summary','action','signal','limitation','detail','evidence_refs','fragments']);texts(x,'strength',['name','summary','action','signal','limitation','detail']);refs(x,'strength');arr(x['fragments'],'fragments')
  if len(x['fragments'])>4:fail('优势碎片最多4条')
  for f in x['fragments']:
   fields(f,'fragment',['label','text','evidence_refs']);texts(f,'fragment',['label','text']);refs(f,'fragment')
 arr(d['paths'],'paths',3)
 if [p.get('id') for p in d['paths']]!=['A','B','C']:fail('paths 必须按 A、B、C 顺序排列')
 baselines=[]
 for p in d['paths']:
  fields(p,'path',['id','name','where','value','income','requirements','risk','lifestyle','detail','evidence_refs','assumptions','annual','plan']);texts(p,'path',['name','where','value','income','requirements','risk','lifestyle','detail']);refs(p,'path');arr(p['assumptions'],'assumptions');
  for a in p['assumptions']:txt(a,'assumption',False)
  arr(p['annual'],'annual',6);arr(p['plan'],'plan',3)
  for i,x in enumerate(p['annual']):
   fields(x,'annual',['year','value','basis','evidence_refs']);refs(x,'annual');txt(x['basis'],'annual.basis')
   if type(x['year'])!=int or x['year']!=i:fail('年度必须依次为 0–5')
   if x['value'] is not None:
    if type(x['value']) not in (int,float) or not math.isfinite(x['value']):fail('收入只能为有限数字或 null')
    if not x['basis'] or not x['evidence_refs']:fail('已填收入须提供计算依据与证据引用')
    if i and (not p['assumptions'] or not any(lookup[r]['kind']=='market' and lookup[r]['url'] and lookup[r]['access_date'] for r in x['evidence_refs'])):fail('未来收入数值须有条件假设及可追溯市场资料；不足时请填 null')
   if i==0:baselines.append(x['value'])
  for day,t in zip([30,90,365],p['plan']):
   fields(t,'plan',['day','title','action','output','feedback','time','detail','evidence_refs']);texts(t,'plan',['title','action','output','feedback','time','detail']);refs(t,'plan')
   if type(t['day'])!=int or t['day']!=day:fail('计划天数应依次为30、90、365')
 if len(set(baselines))>1: fail('三条路径 Y0 必须为同一已知基线或均为 null')
 return d

def safe_json(x):return json.dumps(x,ensure_ascii=True,allow_nan=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
def render(d):
 validate(d)
 income=(ROOT/'assets/income-template.html').read_text(encoding='utf8')
 data={p['id']:{'name':p['name'] or '待确认','color':c,'values':[x['value'] for x in p['annual']],'steps':[x['title'] or '待补充' for x in p['plan']]} for p,c in zip(d['paths'],['#79b5ff','#f3cd7c','#89d5b1'])}
 const='const DATA='+safe_json(data)+',UNIT='+safe_json(d['meta']['income_unit'] or '单位待确认')+',BASIS='+safe_json((d['meta']['income_basis'] or '收入口径待确认')+'；条件情景，非预测。未知数值不插值。')+',INITIAL='+safe_json(d['meta']['selected_path'] or 'A')+';'
 income,n=re.subn(r'const DATA=.*?,INITIAL="A";',lambda m:const,income,count=1,flags=re.S)
 if n!=1:raise ValueError('收入图模板标记不匹配')
 tpl=(ROOT/'assets/report-template.html').read_text(encoding='utf8');runtime=(ROOT/'assets/runtime.js').read_text(encoding='utf8')
 for token in ['__REPORT_JSON__','__RUNTIME_JS__','__INCOME_SRCDOC__']:
  if tpl.count(token)!=1:raise ValueError('模板标记异常：'+token)
 return tpl.replace('__REPORT_JSON__',safe_json(d)).replace('__RUNTIME_JS__',runtime).replace('__INCOME_SRCDOC__',html.escape(income,quote=True))
if __name__=='__main__':
 try:
  if len(sys.argv)!=3:raise ValueError('用法：python scripts/render_report.py 数据.json 报告.html')
  d=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'));out=Path(sys.argv[2]);out.write_text(render(d),encoding='utf8');print('已生成：',out)
 except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e: print('数据校验未通过：',e,file=sys.stderr);sys.exit(2)
