"""Run one measured regression; retain every run and genuine Allure history."""
from pathlib import Path
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",default="run01")
    parser.add_argument("--browser",default="chromium",choices=["chromium","firefox"])
    parser.add_argument("--allure",default=shutil.which("allure"))
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    os.chdir(root)
    out=root/"results"/args.run
    if out.exists():
        parser.error(f"Run directory already exists: {out}; use a new --run identifier")
    out.mkdir(parents=True)
    allure_results=out/"allure-results"
    allure_results.mkdir()
    env={**os.environ,"RESULTS_DIR":str(out),"BDD_BROWSER":args.browser,"PYTHONIOENCODING":"utf-8"}
    started=time.perf_counter()
    commands=[
        [sys.executable,"-m","pytest","--browser",args.browser,"--alluredir",str(allure_results),"--junitxml",str(out/"pytest.xml"),"--html",str(out/"pytest.html"),"--self-contained-html","--cov=app","--cov-branch","--cov-report",f"json:{out/'coverage.json'}","--cov-report",f"html:{out/'coverage-html'}","--cov-fail-under=90"],
        [sys.executable,"-m","behave","--format","allure_behave.formatter:AllureFormatter","--outfile",str(allure_results),"--format","json","--outfile",str(out/"behave.json"),"--format","pretty"]
    ]
    codes=[]
    for i,command in enumerate(commands):
        result=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
        (out/("pytest.log" if i==0 else "behave.log")).write_text(result.stdout,encoding="utf-8")
        print(result.stdout)
        codes.append(result.returncode)
    elapsed=time.perf_counter()-started
    (out/"run.json").write_text(json.dumps({"run":args.run,"browser":args.browser,"seconds":elapsed,"exitcodes":codes,"python":platform.python_version(),"platform":platform.platform()},indent=2),encoding="utf-8")
    (allure_results/"environment.properties").write_text(f"Browser={args.browser}\nPython={platform.python_version()}\nBase.URL={os.getenv('BASE_URL','https://demoqa.com')}\nAuthor=Vadim Botter\n",encoding="utf-8")
    previous=root/"results"/"allure-report"/"history"
    if previous.exists():
        shutil.copytree(previous,allure_results/"history")
    (allure_results/"categories.json").write_text(json.dumps([{"name":"Known DemoQA defects","matchedStatuses":["skipped"],"messageRegex":".*BUG-.*"},{"name":"Assertion failures","matchedStatuses":["failed"]},{"name":"Infrastructure or test errors","matchedStatuses":["broken"]}]),encoding="utf-8")
    (allure_results/"executor.json").write_text(json.dumps({"name":"GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "Local regression","type":"github" if os.getenv("GITHUB_ACTIONS") else "local","buildName":args.run,"buildOrder":int(os.getenv("GITHUB_RUN_NUMBER",''.join(filter(str.isdigit,args.run)) or '1')),"buildUrl":os.getenv("GITHUB_SERVER_URL","")+('/'+os.getenv('GITHUB_REPOSITORY','')+'/actions/runs/'+os.getenv('GITHUB_RUN_ID','') if os.getenv('GITHUB_ACTIONS') else '')}),encoding="utf-8")
    if args.allure:
        command=[args.allure,"generate",str(allure_results),"--clean","-o",str(root/"results"/"allure-report")]
        result=subprocess.run(command,shell=os.name=="nt" and str(args.allure).endswith(".bat"))
        if result.returncode:
            return result.returncode
    return max(codes)


if __name__ == "__main__":
    raise SystemExit(main())
