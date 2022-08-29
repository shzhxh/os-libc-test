import pytz

from pygrading import *
from exception import CG
from utils import loge
from datetime import datetime

import os
import subprocess


def replace_testfile(config, job):
    # replace test file
    testcase_input_src = os.path.join(config["testcase_dir"])
    # we request that the submit code must have a dir named "test"
    testcase_replace_dst = os.path.join(config['submit_dir'], "test")

    if not os.path.exists(testcase_replace_dst):
        os.mkdir(testcase_replace_dst)

    testcases = os.listdir(testcase_input_src)
    loge("[os autotest]:"+str(testcases))
    for testcase in testcases:
        if not (testcase[-2:] in (".c", ".h") or testcase == "Makefile"):
            continue
        # if testcase == 'test.c':
        #     raise CG.CompileError("We don't allow testcase named test.c")
        testcase_input_code = os.path.join(testcase_input_src, testcase)
        testcase_replace_code = os.path.join(testcase_replace_dst, testcase)

        if os.path.exists(testcase_replace_code):
            rename_cmd = "mv " + testcase_replace_code + " "+testcase_replace_code+".ori"
            loge("[os autotest]: " + rename_cmd)
            exec(rename_cmd)
            job.add_log(rename_cmd)
        replace_cmd = "cp "+testcase_input_code + " " + testcase_replace_code
        loge("[os autotest]: "+replace_cmd)
        exec(replace_cmd)
        job.add_log(replace_cmd)


@CG.catch
def prework(job: Job):
    job.add_log(str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))), "START TIME")
    config = job.get_config()
    replace = config.get("replace_testcase", False)
    # need to be done when run in platform
    # config['submit_dir'] = os.path.join(config['submit_dir'], os.listdir(config['submit_dir'])[0])

    if len(os.listdir(config['submit_dir'])) == 0:
        raise CG.CompileError("No submit file")

    forbidden_files = ["os_flash_out.txt", "os_serial_out.txt", "sdcard_write.txt", "sdcard_flash.txt", "os.bin"]
    for file in os.listdir(config['submit_dir']):
        if file in forbidden_files:
            raise CG.CompileError(f"You cannot submit a {file}")

    # replace test file
    if replace:
        replace_testfile(config, job)

    # prepare sdcard
    # if sdcard:
    #     try:
    #         prepare_sdcard(config)
    #     except Exception as e:
    #         print(traceback.format_exc())
    #         raise e

    # loge(os.listdir(config['submit_dir']))
    compile_output_path = os.path.join(
        config['submit_dir'], "os_compile_out.txt")
    # start compile
    loge("\n[os autotest]: Compile Start\n")

    # execute make command
    loge("\n[os autotest]: call make to compile\n")
    # loge(os.listdir(os.path.join(config['submit_dir'])))
    # my_env = os.environ.copy()
    # my_env["PATH"] = "/root/.cargo/bin:" + my_env["PATH"]
    compile_result = subprocess.run("make all", shell=True,
                                    cwd=config['submit_dir'],
                                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    # compile_result = gg.utils.exec(compile_cmd)
    # loge("\ncompile STDOUT\n")
    # loge(compile_result.stdout)
    # with open(compile_output_path, "a+") as compile_output_file:
    #     compile_output_file.write("\ncompile STDERR\n")
    #     compile_output_file.write(compile_result.stderr.decode())
    job.add_log_detail(str(config), "CONFIG")
    job.add_log(compile_result.stdout.decode(), "编译STDOUT")
    job.add_log(compile_result.stderr.decode(), "编译STDERR")

    has_os_bin = os.path.exists(os.path.join(config['submit_dir'], 'os.bin'))
    has_sbi = os.path.exists(os.path.join(config['submit_dir'], 'sbi-qemu'))
    has_ker = os.path.exists(os.path.join(config['submit_dir'], 'kernel-qemu'))

    config['sbi_file'] = 'sbi-qemu' if has_sbi else 'none'

    if compile_result.returncode != 0:
        loge("compile error")
        loge(compile_result.stderr.decode())
        loge(compile_result.stdout.decode())
        raise CG.CompileError("编译出错")

    if (not has_os_bin) and (not has_ker):
        loge("compile error")
        loge(compile_result.stderr.decode())
        loge(compile_result.stdout.decode())
        raise CG.CompileError("未生成os.bin或未生成sbi-qemu和kernel-qemu")

    loge("[os autotest]: Compile Succeed")

    # # 准备私钥文件
    # with open("id_rsa", 'w') as f:
    #     f.write(id_rsa)
    # os.system("chmod 600 id_rsa")
    testcases = TestCases()
    testcases.append("TestCase 1", 100, "", "")
    job.set_testcases(testcases)
