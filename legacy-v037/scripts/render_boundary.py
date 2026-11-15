"""Render fixed B-style income steps and their human-readable evidence, never example defaults."""
import html,math
from urllib.parse import urlsplit

def e(x):return html.escape(str(x),quote=True)
def plain(x):
    if x is None:return '待核验'
    if isinstance(x,dict):return plain(x.get('value')) if 'value' in x else '；'.join(plain(v) for v in x.values())
    if isinstance(x,list):return '；'.join(plain(v) for v in x) if x else '暂无已核实条目'
    return str(x)
def amount(x):return '待核验' if x is None else f'{x:,.2f}'.rstrip('0').rstrip('.')

def bands(key,level,phase=None):
    starts={'mind':180,'body':270,'spirit':90,'work':0}
    position={'dissonance':1,'uncertainty':2,'discovery':3}.get(phase)
    def point(r,a):
        a=math.radians(a);return 300+r*math.cos(a),300+r*math.sin(a)
    def arc(inner,outer,start,end,on,cls,attrs=''):
        a,b,c,d=point(outer,start),point(outer,end),point(inner,end),point(inner,start)
        path=f'M{a[0]:.3f} {a[1]:.3f} A{outer} {outer} 0 0 1 {b[0]:.3f} {b[1]:.3f} L{c[0]:.3f} {c[1]:.3f} A{inner} {inner} 0 0 0 {d[0]:.3f} {d[1]:.3f} Z'
        fill=f'url(#g-{key})' if on else '#172535'
        return f'<path class="{cls} {"observed" if on else "unfilled"}" {attrs} fill="{fill}" d="{path}"/>'
    out=''
    for i,(inner,outer) in enumerate([(140,176),(180,214),(218,252)],1):
        for j in range(1,4):
            on=level is not None and (i<level or (i==level and position is not None and j<=position))
            out+=arc(inner,outer,starts[key]+(j-1)*30+1,starts[key]+j*30-1,on,'level-band',f'data-level="{i}" data-phase-slice="{j}"')
    out+='<g class="phase-position" aria-label="阶段定位，不表示分数">'
    for j in range(1,4):
        out+=arc(111,130,starts[key]+(j-1)*30+1,starts[key]+j*30-1,position is not None and j<=position,'phase-band',f'data-phase-slice="{j}"')
    return out+'</g>'

def render_boundary(report):
    b=report.get('boundary_analysis',{})
    unit=report['income_basis']['unit']
    current=b.get('current_role_range',{})
    target=b.get('target_role_range',{})
    vals=[report['income_baseline']['value'],current.get('high'),target.get('high')]
    known=[v for v in vals if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0]
    quantitative=len(known)>=2 and max(known)>0
    maximum=max(known) if known else 1
    synthetic=any(x.get('source_type','').startswith('synthetic') for x in report['evidence_index'])
    simulation=any(x.get('status')=='simulation' for x in [current,target])
    tag='合成演示 · 非个人结论' if synthetic else '条件分析 · 非收入保证'
    titles=['本人当前收入','现职责可比样本上沿','新职责条件空间']
    statuses={'unknown':'资料待核验','limited':'少样本参考','reference':'可比样本参考','estimate':'AI条件估计','simulation':'虚构演示数据'}
    descriptions=['本人事实；不以行业均值替代',f'范围：{amount(current.get("low"))}—{amount(current.get("high"))}',f'范围：{amount(target.get("low"))}—{amount(target.get("high"))}']
    states=['本人陈述' if vals[0] is not None else '未提供起点',statuses.get(current.get('status'),'资料待核验'),statuses.get(target.get('status'),'资料待核验')]
    parts=[]
    for i,(v,title,desc,state) in enumerate(zip(vals,titles,descriptions,states)):
        is_known=isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0
        height=(v/maximum*180 if quantitative else 72) if is_known else 0
        state_class='' if is_known else 'is-unknown'
        column_class='' if is_known else 'unknown-value'
        parts.append(f'<article class="stair-proof-step {state_class}"><div class="stair-proof-caption"><small>{e(title)}</small><strong>{e(amount(v))}</strong><span>{e(desc)}</span><em>{e(state)}</em></div><div class="stair-proof-column {column_class}" style="height:{height:.3f}px" aria-hidden="true"></div></article>')
    note='已知金额按同一尺度绘制；待核验项不画数值柱。' if quantitative else '已知金额不足以比较，当前仅作信息展示；未知项不补金额。'
    if simulation:note+=' 图中金额均为虚构演示，不能作为岗位薪资参考。'
    graph=f'''<div class="boundary-exhibit"><div class="bc-top"><div><div class="bc-caption">收入边界与突破条件</div><h3>从当前职责，到下一种价值交付</h3></div><span class="bc-tag">{tag}</span></div><p class="bc-sub">{e(unit)} · {e(report['income_basis']['tax_basis'])}</p><div class="stair-proof" data-scaled="{str(quantitative).lower()}" role="img" aria-label="{e('；'.join(t+': '+amount(v) for t,v in zip(titles,vals)))}">{''.join(parts)}</div><p class="bc-foot">{e(note)} 样本上沿是观察范围，不是个人终身上限；第三档取决于职责变化和验证结果，不承诺一定高于现状。</p></div>'''
    index={x['id']:x for x in report['evidence_index']}
    def quotes(refs):
        es=[index[r] for r in refs if r in index]
        return '；'.join(f'{r["id"]}：{r["quote"]}' for r in es) or '尚无足够个人经历支持；不据此确定适配或上限。'
    def card(title,label,content):return f'<article class="proof-card"><small>{e(label)}</small><h3>{e(title)}</h3><p>{e(plain(content))}</p></article>'
    summary=card('为什么当前收入可能受限','当前结构',b.get('current_structure','当前职责、收入机制与市场窗口尚未完整核对。'))
    summary+=card('哪些能力有经历支持','个人证据',quotes(b.get('personal_evidence_refs',[])))
    summary+=card('跨到下一档要满足什么','成立条件',b.get('transition_conditions','先验证目标职责、真实需求与生活容量，不凭天赋标签涨薪。'))
    gaps=''
    for g in b.get('gap_analysis',[]):
        gaps+=f'<li><b>{e(g.get("capability","待核对能力"))}</b><br>已有依据：{e(quotes(g.get("personal_evidence_refs",[])))}<br>目标要求：{e(g.get("market_requirement","尚未核验"))}<br>要求来源：{e("、".join(g.get("market_evidence_refs",[])) or "暂无已核查来源")}<br>验证动作：{e(g.get("verification_task","需结合真实任务制定"))}</li>'
    gaps=gaps or '<li>目标职责尚未核对，不推断能力差距；先补真实任务要求和本人可复用的经历。</li>'
    market=[]
    for label,rng in [('现职责',current),('新职责',target)]:
        for ref in rng.get('source_refs',[]):
            src=index.get(ref)
            if not src:continue
            url=src.get('url') or ''
            title=src.get('publisher') or ref
            anchor=f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(title)}</a>' if urlsplit(url).scheme in ('https','http') else e(title)
            market.append(f'<li><span class="source-badge">{label} · {"已核查" if src.get("verified") else "未独立核查"}</span>{anchor}<br>{e(src.get("quote",""))}<br>地区：{e(src.get("region") or "未知")}；岗位/职责：{e(src.get("role") or "未知")}；口径：{e(src.get("basis") or "未知")}；访问：{e(src.get("access_date") or "未知")}<br>匹配与局限：{e(rng.get("comparability_note") or "尚未核对可比性")}</li>')
    market_html=''.join(market) or '<li>当前没有可用的岗位薪酬样本。保留待核验，不用宏观平均工资替代个人上限。</li>'
    assumptions=[]
    for ref in set(current.get('assumption_refs',[])+target.get('assumption_refs',[])):
        h=next((h for h in report['assumptions'] if h['id']==ref),None)
        if h:assumptions.append(h['description']+'；失效条件：'+h['failure_condition'])
    plan_attr=f' data-boundary-plan="{b["path_id"]}"' if b.get('path_id') in ('A','B','C') else ''
    proof=f'''<div class="boundary-proof"><div class="proof-grid">{summary}</div><div class="report-details"><details open><summary>从已有能力，到目标职责：差距与验证</summary><ul class="reference-list">{gaps}</ul></details><details open><summary>判断依据：实际样本与可比性</summary><ul class="reference-list">{market_html}</ul><p class="proof-note">现职责范围：{e(current.get('scope') or '待核验')}。新职责范围：{e(target.get('scope') or '待核验')}。</p></details><details open><summary>先验证什么，何时调整结论</summary><p class="proof-note">{e(plain(b.get('validation_plan','先确认一个目标任务，用实际交付和反馈检验，再扩大投入。')))}</p><p class="proof-note">{e(plain(b.get('limitations','市场窗口、个人贡献与可用容量仍可能改变；资料不足不做硬性上限判断。')))}</p><p class="proof-note">{'<br>'.join(e(x) for x in assumptions) or '当前未使用未说明的数值假设。'}</p><p class="proof-links"><a href="#journey"{plan_attr}>查看对应的7 / 30 / 90天验证计划 →</a></p></details><details><summary>方法参考，不是本人的薪资证据</summary><ul class="reference-list"><li><a href="https://www.stats.gov.cn/zs/tjws/tjzb/202301/t20230101_1903795.html" target="_blank" rel="noopener noreferrer">国家统计局：什么是平均工资</a><br>用于理解统计口径，不把平均工资当作某个人的上限。</li><li><a href="https://handbook.gitlab.com/handbook/total-rewards/compensation/" target="_blank" rel="noopener noreferrer">GitLab：公开薪酬方法</a><br>企业按角色、级别和地区匹配薪酬的实例，不证明本人的具体可得收入。</li></ul><p class="proof-note">方法页访问日期：2026-11-12。个人金额仍须另查同地区、同职责的实际资料。</p></details></div></div>'''
    return graph,proof
