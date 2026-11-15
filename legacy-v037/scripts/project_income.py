"""Calculate evidence-linked income scenarios. Does not invent parameters or verify markets."""
import copy,json,math,sys
from pathlib import Path
from validate_report import validate

FIELDS=('salary_monthly','paid_months','bonus','service_units','service_unit_price','service_variable_cost','service_fixed_cost','hours_per_unit','service_hours_budget')

def calculate(inputs):
    missing=[k for k in FIELDS if k not in inputs or inputs[k].get('value') is None]
    if missing:return None,{'status':'unknown','missing_parameters':missing}
    v={k:inputs[k]['value'] for k in FIELDS}
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in v.values()):raise ValueError('nonfinite/non-numeric parameter')
    if not 0<=v['paid_months']<=12:raise ValueError('paid months must be 0..12')
    if any(x<0 for x in v.values()):raise ValueError('negative input: use positive costs and explicit subtraction')
    if v['service_units']>0 and v['hours_per_unit']<=0:raise ValueError('positive service units require positive total unit hours')
    if v['service_units']*v['hours_per_unit']>v['service_hours_budget']+1e-9:raise ValueError('service demand exceeds time capacity')
    wage=v['salary_monthly']*v['paid_months']+v['bonus']
    revenue=v['service_units']*v['service_unit_price']
    costs=v['service_units']*v['service_variable_cost']+v['service_fixed_cost']
    return round(wage+revenue-costs,8),dict(status='calculated',salary=wage,service_revenue=revenue,service_cost=costs,service_net=revenue-costs,service_hours=v['service_units']*v['hours_per_unit'],formula='salary_monthly * paid_months + bonus + service_units * (service_unit_price - service_variable_cost) - service_fixed_cost')

def project(report):
    d=copy.deepcopy(report)
    for s in d['income_scenarios']:
        model=s.get('projection_model')
        if not model:continue
        years=model.get('years',[])
        if [y['year'] for y in years]!=[1,2,3,4,5]:raise ValueError('model requires years 1..5')
        annual=[dict(year=0,formula=None,**copy.deepcopy(d['income_baseline']))]
        for y in years:
            if not y.get('explanation'):raise ValueError('missing annual model explanation')
            inputs=y['inputs'];value,parts=calculate(inputs)
            refs=sorted({r for p in inputs.values() for r in p.get('assumption_refs',[])})
            facts=sorted({r for p in inputs.values() for r in p.get('evidence_refs',[])})
            unknown=sorted({r for p in inputs.values() for r in p.get('unknown_refs',[])})
            if value is None:
                if not unknown:raise ValueError('missing model parameters must reference unknowns')
                a=dict(year=y['year'],value=None,kind='unknown',evidence_refs=facts,assumption_refs=refs,unknown_refs=unknown,formula=None)
            else:
                if not refs:raise ValueError('future scenario requires explicit assumptions, not factual prediction')
                def term(v):return dict(kind='assumption',value=v,evidence_refs=[],assumption_refs=refs,unknown_refs=[])
                a=dict(year=y['year'],value=value,kind='assumption',evidence_refs=facts,assumption_refs=refs,unknown_refs=unknown,formula={'operation':'sum','inputs':[term(parts['salary']),term(parts['service_net'])]})
            a['calculation_details']=parts
            annual.append(a)
        s['annual']=annual;s['analysis_source']='ai_model';s['sensitivity']=[]
        for case in model.get('sensitivity_cases',[]):
            value,parts=calculate(case['inputs'])
            s['sensitivity'].append(dict(name=case['name'],year=case['year'],value=value,explanation=case['explanation'],calculation_details=parts,note='条件敏感性，不是概率或置信区间'))
    errors=validate(d)
    if errors:raise ValueError('; '.join(errors))
    return d

if __name__=='__main__':
    try:
        out=project(json.loads(Path(sys.argv[1]).read_text()))
        Path(sys.argv[2]).write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
        print(sys.argv[2])
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        print('Projection failed: '+str(exc),file=sys.stderr);sys.exit(1)
