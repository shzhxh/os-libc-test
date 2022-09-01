import datetime
import json
import re
import os
import time

import pygrading as gg

from utils import loge

server_run = False

from run_qemu import run_qemu


def pe(e: exec):
    loge(f"CMD: {e.cmd}\nOUT:\n{e.stdout}\nERR:\n{e.stderr}\nRETCODE:{e.returncode}")


def is_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def parse_lmbench(output):
    result = {}
    units = ("microseconds", "KB/sec", "MB/sec")
    lst = ["lat_mmap:(microseconds)", "bw_file_rd io_only", "bw_file_rd open2close", "bw_mmap_rd mmap_only", "bw_mmap_rd open2close"]
    lst_cnt = 0
    ctx = (2, 4, 8, 16, 24, 32, 64, 96)
    for line in output.split("\n"):
        sep = line.strip().split()
        if not sep:
            continue
        if len(sep) >= 3 and sep[-1] in units and is_float(sep[-2]):
            result[' '.join(sep[:-2]) + f"({sep[-1]})"] = float(sep[-2])
        if len(sep) == 4 and sep[0][-1] == 'k':
            result[f"fs latency {sep[0]} create"] = int(sep[2])
            result[f"fs latency {sep[0]} remove"] = int(sep[3])
        if len(sep) == 2 and is_float(sep[0]) and is_float(sep[1]):
            if float(sep[0]) in ctx:
                result[f"context switch {sep[0]}:(microseconds)"] = float(sep[1])
            else:
                result[lst[lst_cnt]] = float(sep[1])
                lst_cnt += 1
    return result


def check_n(line, n):
    lst = line.split(' ')
    if len(lst) == n:
        try:
            for i in range(n):
                float(lst[i])
        except ValueError:
            return False
        return True
    return False


def parse_scene(output):
    state = 0
    keys = (
        "bw_file_rd_io_only",
        "bw_file_rd_open2close",
        "lat_proc_fork",
        "lat_proc_exec",
        "bw_pipe",
        "lat_pipe",
        "lat_pagefault",
        "lat_mmap",
        "lat_ctx"
    )
    result_keys = (
        "bw_file_rd_io_only",
        "bw_file_rd_open2close",
        "lat_proc_fork",
        "lat_proc_exec",
        "bw_pipe",
        "lat_pipe",
        "lat_pagefault",
        "lat_mmap",
        "lat_ctx_2",
        "lat_ctx_4",
        "lat_ctx_8",
        "lat_ctx_16",
        "lat_ctx_24",
        "lat_ctx_32"
    )
    result = {}
    key = ""
    for line in output.split("\n"):
        if state == 0:
            if line[:5] == "START":
                if line[6:] in keys:
                    key = line[6:]
                    state = 1
        elif state == 1:
            if line[:3] == "END":
                state = 0
                if line.split(' ')[-1] != "0":
                    result[key] = "0"
            elif line[:5] == "START":
                if line[6:] in keys:
                    result[key] = "0"
                    key = line[6:]
                    state = 1
            elif key in ("bw_file_rd_io_only", "bw_file_rd_open2close", "lat_mmap"):
                if check_n(line, 2):
                    result[key] = line.split(' ')[1]
            elif key in ("lat_proc_fork", "lat_proc_exec", "bw_pipe", "lat_pipe"):
                lst = line.split(' ')
                if len(lst) == 4:
                    try:
                        result[key] = str(float(lst[2]))
                    except ValueError:
                        pass
            elif key == "lat_ctx":
                if check_n(line, 2):
                    lst = line.split(' ')
                    if lst[0] in ("2", "4", "8", "16", "24", "32"):
                        result[key + "_" + lst[0]] = lst[1]
            elif key == "lat_pagefault":
                lst = line.split(' ')
                if len(lst) == 5:
                    try:
                        result[key] = str(float(lst[3]))
                    except ValueError:
                        pass
    for k in result_keys:
        if k not in result.keys():
            result[k] = "0"
    for k in result.keys():
        if k[:2] == "bw" and float(result[k]) != 0:
            result[k] = str(1 / float(result[k]))
    return result


def run(job: gg.Job, testcase: gg.TestCases.SingleTestCase):
    job.add_log_detail(f"BEFORE_RUN: {datetime.datetime.now()}", "time")
    config = job.get_config()
    result = {'name': testcase.name, 'score': 0}
    # -- check bin file ---

    # ---FLASH---
    # input_str = utils.readfile(str(testcase.input_src))0
    loge("\n[os autotest]: Flash Start:\n")

    serial_out_path = os.path.join(config["submit_dir"], "os_serial_out.txt")
    serial_flash_path = os.path.join(config['submit_dir'], "os_flash_out.txt")
    sdcard_flash_path = os.path.join(config['submit_dir'], "sdcard_flash.txt")
    sdcard_write_path = os.path.join(config['submit_dir'], "sdcard_write.txt")
    # # input_str = utils.readfile(str(testcase.input_src))
    server = config['server_ip']
    port = config['server_port']
    password = config['server_password']
    user = config['server_user']
    ssh_pass = f'sshpass -p "{password}"'
    host = f'{user}@{server}'
    dev = config['server_dev']
    ssh_cmd = f"-o StrictHostKeyChecking=no -p {port}"
    scp_cmd = f"-o StrictHostKeyChecking=no -P {port}"

    port_dir = dev.split('/')[-1]
    port_dir = f"/cg/{port_dir}"

    # # gg.exec(f"ssh-keygen -R {server}")

    def logexec(cmd):
        job.add_log_detail(cmd, "cmd")
        loge("[os autotest]:" + cmd)
        start_time = time.time()
        res = gg.exec(cmd)
        job.add_log_detail(f"STDOUT:\n{res.stdout}\nSTDERR:{res.stderr}\nTIME:{datetime.datetime.now()}\nDURATION:{time.time() - start_time}", cmd)
        if res.returncode != 0:
            raise RuntimeError(f"run command error {cmd} \n{res.stdout}\n{res.stderr}")
        return res

    # logexec(f"{ssh_pass} ssh {ssh_cmd} {host} mkdir -p /cg/")
    if config['board_type'] != 'qemu':
        logexec(f"{ssh_pass} ssh {ssh_cmd} {host} mkdir -p {port_dir}")
        logexec(f"{ssh_pass} ssh {ssh_cmd} {host} rm -f {port_dir}/*")

    if config['board_type'] == 'k210':
        logexec(f"{ssh_pass} scp {scp_cmd} {config['testcase_dir']}/ssh_run_k210.py {host}:{port_dir}/ssh_run.py")
        logexec(f"{ssh_pass} scp {scp_cmd} {config['testcase_dir']}/ktool.py {host}:{port_dir}/ktool.py")
        logexec(f"{ssh_pass} scp {scp_cmd} {config['testcase_dir']}/img.kfpkg {host}:{port_dir}/img.kfpkg")
    elif config['board_type'] == 'unmatched':
        logexec(f"{ssh_pass} scp {scp_cmd} {config['testcase_dir']}/ssh_run_unmatched.py {host}:{port_dir}/ssh_run.py")
    #     logexec(f"{ssh_pass} scp {scp_cmd} {config['testcase_dir']}/sdcard.img.gz {host}:{port_dir}/sdcard.img.gz")
    elif config['board_type'] == 'qemu':
        os.chdir(config['submit_dir'])
        logexec(f"cp {config['testcase_dir']}/sdcard.img sdcard.img")
        qemu_out, process = run_qemu(job, config["sbi_file"], "kernel-qemu", "sdcard.img", "os_serial_out.txt")
        # if qemu_out:
        #     if qemu_out.stdout:
        #         job.add_log(qemu_out.stdout.decode(), "QEMU STDOUT")
        #     if qemu_out.stderr:
        #         job.add_log(qemu_out.stderr.decode(), "QEMU STDERR")
        # if process:
        #     if process.stdout:
        #         job.add_log(process.stdout, "QEMU STDOUT")
        #     if process.stderr:
        #         job.add_log(process.stderr, "QEMU STDERR")

    else:
        raise RuntimeError("Unknown board_type")

    if config['board_type'] != 'qemu':
        logexec(f"{ssh_pass} scp {scp_cmd} {config['submit_dir']}/os.bin {host}:{port_dir}")
        ssh_run_result = logexec(f"{ssh_pass} ssh {ssh_cmd} {host} python3 {port_dir}/ssh_run.py {dev}")
    else:
        ssh_run_result = None
    if config['board_type'] == 'k210':
        logexec(f"{ssh_pass} scp {scp_cmd} {host}:{port_dir}/os_flash_out.txt {serial_flash_path}")
        logexec(f"{ssh_pass} scp {scp_cmd} {host}:{port_dir}/sdcard_write.txt {sdcard_write_path}")
        logexec(f"{ssh_pass} scp {scp_cmd} {host}:{port_dir}/sdcard_flash.txt {sdcard_flash_path}")

    if config['board_type'] != 'qemu':
        logexec(f"{ssh_pass} scp {scp_cmd} {host}:{port_dir}/os_serial_out.txt {serial_out_path}")

    # ssh_run_result = gg.exec(f"{ssh_pass} ssh {ssh_cmd} {host} python3 /cg/ssh_run_os.py {dev}")
    # gg.exec(f"{ssh_pass} scp {scp_cmd} {host}:/cg/os_flash_out.txt {config['submit_dir']}/os_flash_out.txt")
    # gg.exec(f"{ssh_pass} scp {scp_cmd} {host}:/cg/os_serial_out.txt {config['submit_dir']}/os_serial_out.txt")
    if ssh_run_result:
        result['output'] = ssh_run_result.stdout
        result['stderr'] = ssh_run_result.stderr
        result['time'] = ssh_run_result.exec_time
    if config['board_type'] == 'k210':
        file_list = [serial_out_path, serial_flash_path, sdcard_flash_path, sdcard_write_path]
    else:
        file_list = [serial_out_path]

    for p in file_list:
        if not os.path.exists(p):
            job.add_log(result['stderr'], "ssh_run stderr")
            job.add_log(f"Can not read {p}, please contact with administrator.", "error")
            result['error'] = True
            return result

    try:
        serial_out = open(serial_out_path, encoding='utf-8').read()
    except UnicodeDecodeError:
        serial_out = open(serial_out_path, 'rb').read().decode(errors='ignore')
    # serial_flash_out = open(serial_flash_path, encoding='utf-8').read()
    # job.add_log(serial_flash_out, "烧写OS日志")
    job.add_log(serial_out, "raw output")

    if config['board_type'] == 'k210':
        serial_flash = open(serial_flash_path).read()
        sdcard_write = open(sdcard_write_path).read()
        sdcard_flash = open(sdcard_flash_path).read()
        job.add_log_detail(serial_flash, "flash log")
        job.add_log_detail(sdcard_flash, "sdcard flash")
        job.add_log(sdcard_write, "烧写SD卡日志")

    # loge(serial_out)
    runner_path = config["testcase_dir"]

    if not config.get("final", False):
        # 初赛
        test_result = logexec(f"cd {runner_path} && python3 test_runner.py {serial_out_path}")
        job.add_log(test_result.stderr, "test_runner stderr")

        try:
            test_result = json.loads(test_result.stdout)
        except Exception:
            test_result = []
        result['test_results'] = test_result

    else:
        # 复赛
        # serial_out = open(serial_out_path).read()
        pattern = re.compile(r"testcase (.+) (\bsuccess\b|\bfail\b)")
        results = pattern.findall(serial_out)
        results = {x[0].strip(): x[1] == 'success' for x in results}

        # names = set(x["name"] for x in results)

        def append_miss(name, prefix):
            with open(f"{config['testcase_dir']}/{name}") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if f"{prefix} {line}" not in results.keys():
                        results[f"{prefix} {line}"] = False
                        # results.append({"name": f"{prefix} {line}", "passed": 0, "all": 1})

        append_miss("luas.txt", "lua")
        append_miss("busybox_cmd.txt", "busybox")

        job.add_log_detail(str(results), "RESULTS??")

        results = [{
            "name": k,
            "passed": 1 if v else 0,
            "all": 1
        }
            for k, v in results.items()
        ]
        results = sorted(results, key=lambda x: x["name"])
        result['lua_results'] = results
        import baseline_output
        result['lmbench_results'] = parse_lmbench(serial_out)
        result['lmbench_baseline'] = parse_lmbench(baseline_output.serial_out)
        # result['scene_results'] = parse_scene(serial_out)

    job.add_log_detail(f"AFTER_RUN: {datetime.datetime.now()}", "time")
    return result


if __name__ == '__main__':
    # from baseline_output import serial_out
    # lua_pattern = re.compile(r"testcase (.+) (\bsuccess\b|\bfail\b)")
    # lua_results = lua_pattern.findall(serial_out)
    # lua_results = {x[0]: x[1] == 'success' for x in lua_results}
    # lua_results = [{
    #     "name": k,
    #     "passed": 1 if v else 0,
    #     "all": 1
    # }
    #     for k, v in lua_results.items()
    # ]
    # print(lua_results)
    # print(parse_lmbench(serial_out))
    from scene_output import scene_output
    r = parse_scene(scene_output)
    print(len(r))
    print(r)
