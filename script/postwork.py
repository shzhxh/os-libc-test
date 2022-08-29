import json

from pygrading import Job, render_template
from verdict import Verdict
from datetime import datetime
import pytz


def postwork(job: Job):
    job.add_log_detail(f"BEFORE_POSTWORK: {datetime.now()}", "time")
    summary = job.get_summary()[0]
    config = job.get_config()
    stage = config.get("stage", 1)
    # print(summary)
    job.detail(render_template("logs.html", logs=job.get_logs_detail()))
    comment = ""
    all_tests = 1
    passed_tests = 0
    score = 0
    lmbench_results = None
    if 'error' not in summary:
        if not config.get("final", False):
            test_results = summary['test_results']
            lmbench = []
        else:
            test_results = summary['lua_results']
            # lmbench_results = summary['scene_results']
            lmbench_results = summary["lmbench_results"]
            lmbench_baseline = summary["lmbench_baseline"]
            lmbench = [
                {
                    "name": name,
                    "res": lmbench_results.get(name, 0),
                    "baseline": baseline,
                    "score": 0
                }
                for name, baseline in lmbench_baseline.items()
            ]
            # lmbench = [
            #     {
            #         "name": k,
            #         "res": v
            #     }
            #     for k, v in lmbench_results.items()
            # ]
            for item in lmbench:
                if item["res"] > 0:
                    if "microseconds" in item["name"]:
                        item["score"] = item["baseline"] / item["res"]
                    else:
                        item["score"] = item["res"] / item["baseline"]
            # if stage == 2:
            if stage == 1:
                score += sum(item["score"] for item in lmbench)

        # test_results = [[dict(r, name=x['name']) for r in x['results']] for x in test_results]
        # test_results = sum(test_results, [])
        # test_results = [dict(r, arg0=r['arg'][0], arg1=r['arg'][1]) for r in test_results]
        all_tests = sum([x['all'] for x in test_results])
        if all_tests == 0:
            all_tests = 1
        passed_tests = sum([x['passed'] for x in test_results])
        # score += int(passed_tests / all_tests * 100 + 0.5)
        if stage == 1:
            score += passed_tests  # 阶段1
        info = {
            "all": all_tests,
            "passed": passed_tests,
            "start_time": job.get_log("START TIME"),
            "end_time": str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))),
            "device": job.get_config()['server_dev'],
            "score": score
        }
        comment = render_template("comment.html",
                                  results=test_results,
                                  info=info,
                                  final=config.get("final", False),
                                  lmbench=lmbench,
                                  stage=stage
                                  )
        # verdicts = [x['res'] for x in test_results]
        verdict = Verdict.AC if all_tests == passed_tests else Verdict.WA
    else:
        verdict = Verdict.RuntimeError
    if 'verdict' in summary:
        verdict = summary['verdict']

    # job.add_log("END TIME" + str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))))
    job.del_log("START TIME")
    comment += render_template("logs.html", logs=job.get_logs())
    # log_table = render_template("logs.html", logs=job.get_logs())
    job.comment(comment)

    job.verdict(verdict)
    job.score(int(score))
    if not lmbench_results:
        lmbench_results = {"rank": str(score)}
    else:
        lmbench_results["rank"] = "1"
    job.rank(lmbench_results)
    job.add_log_detail(f"AFTER_POSTWORK: {datetime.now()}", "time")


if __name__ == "__main__":
    job = Job()
    cmd = "cd D:\\codes\\PaddlePi\\riscv-syscalls-testing && python .\\user\\src\\oscomp\\test_runner.py .\\syscalls-test.txt"
    from pygrading import exec
    run = exec(cmd)
    print(run.stderr)
    result = json.loads(run.stdout)
    job.set_summary([{'test_results': result}])
    job.add_log("START TIME", "START TIME")
    job.set_config({"server_dev": "dev0"})
    postwork(job)
    with open("comment.html", "w", encoding="utf-8") as f:
        f.write(job._JobBase__comment)

