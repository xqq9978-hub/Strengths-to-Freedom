"""Offline structural and cross-reference validation, not factual verification."""
import json
import math
from pathlib import Path
import sys


def validate(data):
    errors = []
    schema = json.loads((Path(__file__).parents[1] / 'references/report.schema.json').read_text())

    def require(ok, message):
        if not ok:
            errors.append(message)

    # Only the subset used by the supplied schema is implemented; not a general JSON Schema engine.
    def structure(value, rule, path='$'):
        if '$ref' in rule:
            rule = schema['$defs'][rule['$ref'].split('/')[-1]]
        types = {'object':dict, 'array':list, 'string':str, 'integer':int, 'number':(int,float), 'null':type(None)}
        expected = rule.get('type')
        if expected:
            allowed = expected if isinstance(expected,list) else [expected]
            ok = any(isinstance(value,types[t]) and not (isinstance(value,bool) and t in ('integer','number')) for t in allowed)
            require(ok, path+': type')
            if not ok:
                return
        if 'const' in rule:
            require(value == rule['const'],path+': const')
        if 'enum' in rule:
            require(value in rule['enum'],path+': enum')
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            require(math.isfinite(value),path+': nonfinite')
            require(value >= rule.get('minimum',-math.inf),path+': minimum')
            require(value <= rule.get('maximum',math.inf),path+': maximum')
        if isinstance(value,dict):
            for key in rule.get('required',[]):
                require(key in value,path+': missing '+key)
            for key,r in rule.get('properties',{}).items():
                if key in value:
                    structure(value[key],r,path+'.'+key)
        if isinstance(value,list):
            require(len(value)>=rule.get('minItems',0),path+': too few items')
            require(len(value)<=rule.get('maxItems',math.inf),path+': too many items')
            for i,v in enumerate(value):
                structure(v,rule.get('items',{}),f'{path}[{i}]')

    structure(data,schema)
    if errors:
        return errors
    evidence = {x['id']:x for x in data['evidence_index']}
    assumptions = {x['id']:x for x in data['assumptions']}
    unknowns = {x['id']:x for x in data['unknowns']}
    strengths = {x['id']:x for x in data['strengths']}
    events = {x['id']:x for x in data['events']}
    for name, seq in [('evidence_index',data['evidence_index']),('assumptions',data['assumptions']),('unknowns',data['unknowns']),('strengths',data['strengths']),('events',data['events'])]:
        require(len({x['id'] for x in seq})==len(seq),'duplicate IDs in '+name)

    def claims(value,path='$'):
        if isinstance(value,list):
            for i,v in enumerate(value):
                claims(v,f'{path}[{i}]')
        elif isinstance(value,dict):
            for key,index in [('evidence_refs',evidence),('assumption_refs',assumptions),('unknown_refs',unknowns),('strength_ids',strengths),('event_refs',events)]:
                for ref in value.get(key,[]):
                    require(ref in index,path+': dangling '+key+' '+ref)
                    if key=='evidence_refs' and ref in evidence:
                        require(evidence[ref].get('status')=='active',path+': superseded evidence')
            if 'kind' in value and 'value' in value:
                kind=value['kind']
                if kind=='unknown':
                    require(value['value'] is None and bool(value.get('unknown_refs')),path+': unknown must be null with reference')
                else:
                    require(value['value'] is not None,path+': known claim cannot be null')
                if kind in ('fact','market_reference','inference'):
                    require(bool(value.get('evidence_refs')),path+': unsupported claim')
                if kind=='market_reference':
                    for ref in value.get('evidence_refs',[]):
                        e=evidence.get(ref,{})
                        require(e.get('verified') is True and all(e.get(k) for k in ('url','publisher','access_date','region','role','basis')),path+': unverified market source')
                if kind=='assumption':
                    require(bool(value.get('assumption_refs')),path+': missing assumption')
            for k,v in value.items():
                claims(v,path+'.'+k)
    claims(data)
    for key,q in data['quadrants'].items():
        coaching=q.get('coaching')
        if coaching:
            phase=q.get('development',{}).get('phase')
            require(coaching.get('phase')==phase,key+': coaching phase mismatch')
            expected={'uncertainty':'experiment','discovery':'consolidate'}.get(phase,'clarify')
            require(coaching.get('approach')==expected,key+': coaching approach does not match stage')
    boundary=data.get('boundary_analysis')
    if boundary:
        for ref in boundary.get('personal_evidence_refs',[]):
            require(ref in evidence and evidence[ref].get('status')=='active','boundary: invalid personal evidence')
        require(boundary.get('path_id') in (None,'A','B','C'),'boundary: invalid validation path')
        for key in ('current_role_range','target_role_range'):
            r=boundary.get(key,{})
            require(r.get('status') in ('unknown','limited','reference','estimate','simulation'),'boundary: invalid range status')
            require(r.get('unit',data['income_basis']['unit'])==data['income_basis']['unit'],'boundary: mixed unit')
            numbers=[r.get('low'),r.get('high')]
            for n in numbers:
                require(n is None or isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n),'boundary: invalid range number')
            if all(isinstance(n,(int,float)) and not isinstance(n,bool) for n in numbers):
                require(numbers[0]<=numbers[1],'boundary: reversed range')
            if any(n is not None for n in numbers):
                require(r.get('status')!='unknown','boundary: unknown range has numbers')
            refs=r.get('source_refs',[])
            for ref in refs:
                require(ref in evidence and evidence[ref].get('status')=='active','boundary: invalid market evidence')
            if r.get('status') in ('reference','limited'):
                require(bool(refs),'boundary: salary reference without sources')
                for ref in refs:
                    src=evidence.get(ref,{})
                    require(src.get('verified') is True and all(src.get(x) for x in ('url','publisher','access_date','role','region','basis')),'boundary: market source not verified')
                    require(src.get('sample_type') in ('employer_job','salary_survey','employer_band','actual_offer','transaction_quote'),'boundary: method or macro statistic is not role evidence')
                require(bool(r.get('comparability_note')),'boundary: missing comparability explanation')
                if r.get('status')=='reference':
                    groups={evidence.get(ref,{}).get('source_group') for ref in refs}-{None,''}
                    require(len(groups)>=2,'boundary: multiple independent samples required for reference status; use limited')
            if r.get('status')=='estimate':
                require(bool(r.get('assumption_refs')),'boundary: estimate missing assumptions')
            for ref in r.get('assumption_refs',[]):
                require(ref in assumptions,'boundary: missing assumption reference')
            if r.get('status')=='simulation':
                require(str(data.get('report_id','')).startswith('SYNTHETIC') and any(x.get('source_type','').startswith('synthetic') for x in evidence.values()),'boundary: simulation in personal report')
    for key,q in data['quadrants'].items():
        dev=q.get('development',{})
        require('life_context' in q,key+': missing life context')
        for field in ('level','phase','level_basis','phase_basis','evidence_refs','counterevidence_refs','support','next_transition','unknown_refs'):
            require(field in dev,key+': missing development '+field)
        require(dev.get('level') in (None,1,2,3),key+': invalid development level')
        require(dev.get('phase') in (None,'dissonance','uncertainty','discovery'),key+': invalid development phase')
        if dev.get('level') is not None:
            require(len(set(dev.get('evidence_refs',[])))>=2 and bool(dev.get('level_basis')),key+': insufficient evidence for level')
        if dev.get('phase') is not None:
            require(bool(dev.get('evidence_refs')) and bool(dev.get('phase_basis')),key+': unsupported development phase')
    require(len(strengths)<=3,'more than three strengths')
    for s in strengths.values():
        require(s.get('grade') in ('A','B','C'),'invalid evidence grade')
        require(bool(s.get('evidence_refs')),'strength without evidence')
        if s.get('grade') in ('A','B'):
            require(bool(s.get('event_refs')),'supported strength requires event')
        if s.get('grade')=='A':
            verified_feedback = any(evidence.get(ref,{}).get('verified') is True for ref in s.get('evidence_refs',[]))
            require(len(set(s.get('event_refs',[])))>=2 or verified_feedback,'grade A needs repeated events or verified independent feedback')
    require({s['id'] for s in data['income_scenarios']}=={'A','B','C'},'three unique paths required')
    require(len({s['mechanism'] for s in data['income_scenarios']})==3,'identical path mechanisms')
    required_path=['fit_reason','capacity_status','new_capabilities','market_feedback_needed','growth_conditions','inflection_reason','risk','continue_condition','stop_condition','unknown_refs']
    for s in data['income_scenarios']:
        for k in required_path:
            require(k in s,s['id']+': missing path '+k)
        require([a['year'] for a in s['annual']]==list(range(6)),s['id']+': Y0-Y5 order')
        require(s['annual'][0]['value']==data['income_baseline']['value'],s['id']+': baseline mismatch')
        require(s['annual'][0]['kind']==data['income_baseline']['kind'],s['id']+': baseline provenance mismatch')
        for a in s['annual']:
            require(a['value'] is None or isinstance(a['value'],(int,float)) and not isinstance(a['value'],bool) and math.isfinite(a['value']),s['id']+': invalid amount')
            if a['year']>0 and a['value'] is not None:
                require(a['kind']=='assumption' and bool(a['assumption_refs']),s['id']+': future value must be a conditional scenario')
                for ref in a['assumption_refs']:
                    h=assumptions.get(ref,{})
                    analyst=h.get('origin')=='analyst_estimate' and bool(h.get('rationale')) and bool(h.get('evidence_refs')) and h.get('accepted') is not False
                    require(h.get('accepted') is True or analyst,s['id']+': unsupported or rejected numeric assumption')
            f=a.get('formula')
            if f:
                require(f.get('operation') in ('sum','net'),s['id']+': unsupported formula')
                vals=[i.get('value') for i in f.get('inputs',[])]
                numeric=bool(vals) and all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in vals)
                require(numeric,s['id']+': unknown formula input')
                if numeric and f.get('operation') in ('sum','net'):
                    calc=sum(vals) if f['operation']=='sum' else vals[0]-sum(vals[1:])
                    require(a['value'] is not None and math.isclose(calc,a['value'],abs_tol=1e-8),s['id']+': formula mismatch')
    require({p['path_id'] for p in data['action_plans']}=={'A','B','C'},'plan/path mismatch')
    fields=['name','description','strength_ids','steps','estimated_minutes','estimate_kind','resources','deliverable','metric','completion_rule','feedback_method','risk','fallback','assumption_refs','unknown_refs']
    for p in data['action_plans']:
        require([t['day'] for t in p['tasks']]==[7,30,90],p['path_id']+': missing action stage')
        require(all(k in p for k in ('hypotheses','decision_rules','final_decision','decision_status')),p['path_id']+': plan fields')
        for t in p['tasks']:
            for k in fields:
                require(k in t,p['path_id']+': missing task '+k)
            for k in ('name','description','steps','resources','deliverable','metric','completion_rule','feedback_method','risk','fallback'):
                require(bool(t.get(k)),p['path_id']+': empty task '+k)
            if t.get('estimated_minutes') is None:
                require(bool(t.get('unknown_refs')),p['path_id']+': missing time uncertainty')
            else:
                require(isinstance(t['estimated_minutes'],(int,float)) and t['estimated_minutes']>=0,p['path_id']+': invalid estimated time')
        if p.get('decision_status')=='pending':
            require(p.get('final_decision') is None,p['path_id']+': premature final outcome')
    require({r['id'] for r in data['reports']}=={'REPORT_01','REPORT_02','REPORT_03'},'missing report part')
    for r in data['reports']:
        require(r['report_id']==data['report_id'] and r['revision']==data['revision'],'report revision mismatch')
    for k in ('ADVANTAGE_EVIDENCE_AUDITOR','INCOME_PATH_AUDITOR','ACTION_PLAN_AUDITOR'):
        require(k in data['reviews'],'missing review '+k)
    return errors


if __name__ == '__main__':
    try:
        issues=validate(json.loads(Path(sys.argv[1]).read_text()))
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        issues=['malformed input: '+str(exc)]
    print(json.dumps({'valid':not issues,'errors':issues},ensure_ascii=False,indent=2))
    sys.exit(bool(issues))
