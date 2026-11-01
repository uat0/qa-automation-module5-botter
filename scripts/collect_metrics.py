from collections import Counter, defaultdict
from pathlib import Path
import json
import statistics


def main():
    root=Path(__file__).resolve().parents[1]
    runs=[]
    by_browser=defaultdict(list)
    for directory in sorted((root/"results").iterdir()):
        if not (directory/"run.json").exists():
            continue
        run=json.loads((directory/"run.json").read_text(encoding="utf-8"))
        tests=json.loads((directory/"pytest-results.json").read_text(encoding="utf-8"))["tests"]
        features=json.loads((directory/"behave.json").read_text(encoding="utf-8"))
        scenarios=[s for f in features for s in f.get("elements",[]) if s.get("type")=="scenario"]
        counts=Counter(t["status"] for t in tests)
        bdd_counts=Counter(s["status"] for s in scenarios)
        total=len(tests)+len(scenarios)
        passed=counts["passed"]+bdd_counts["passed"]
        cov=json.loads((directory/"coverage.json").read_text(encoding="utf-8"))["totals"]
        metrics={**run,"pytest":dict(counts),"bdd":dict(bdd_counts),"total":total,"passed":passed,"pass_rate":100*passed/total,"unit":sum('/unit/' in t['id'] for t in tests),"api":sum('/api/' in t['id'] for t in tests),"ui":sum('/ui/' in t['id'] for t in tests),"c0":100*cov['covered_lines']/cov['num_statements'],"c1":100*cov['covered_branches']/cov['num_branches']}
        runs.append(metrics)
        by_browser[run['browser']].append({t['id']:t['status'] for t in tests})
    flakiness={}
    for browser, samples in by_browser.items():
        if len(samples)<2:
            continue
        common=set.intersection(*(set(s) for s in samples))
        changed=[key for key in common if len({s[key] for s in samples})>1]
        flakiness[browser]={"runs":len(samples),"common_tests":len(common),"changed":changed,"rate":100*len(changed)/len(common)}
    chromium_times=[r['seconds'] for r in runs if r['browser']=='chromium']
    auto_minutes=statistics.median(chromium_times)/60
    manual_minutes=45
    development_minutes=300
    savings=manual_minutes-auto_minutes
    import math
    result={"runs":runs,"flakiness":flakiness,"roi":{"manual_minutes_assumed":manual_minutes,"development_minutes_assumed":development_minutes,"automated_minutes_median":auto_minutes,"break_even_runs":math.ceil(development_minutes/savings),"net_saved_after_20_runs_minutes":20*savings-development_minutes,"roi_after_20_runs_percent":100*(20*savings-development_minutes)/development_minutes}}
    destination=root/'results/metrics.json'
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
