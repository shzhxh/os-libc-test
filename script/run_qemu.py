import subprocess
import threading
import os
import time

import pygrading as gg

error = None
process = None


def run_qemu_thread(job, sbi, os_file, fs, out):
    global error
    global process
    gg.exec(f"cp {fs} initrd.img")
    cmd = f"qemu-system-riscv64 -machine virt -kernel {os_file} -m 128M -nographic -smp 2 -bios {sbi} -drive file={fs},if=none,format=raw,id=x0  -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0 -serial file:{out}"
    job.add_log(cmd, "QEMU CMD")
    # cmd = f"qemu-system-riscv64 -machine virt -bios {os} -m 8M -nographic -smp 2 -drive file={fs},if=none,format=raw,id=x0 -serial file:{out}"
    try:
        process = gg.exec(cmd)
        # process = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # process.wait(120)
    except subprocess.TimeoutExpired as e:
        error = e
    except subprocess.CalledProcessError as e:
        error = e


def run_qemu1(job, sbi, os_file, fs, out):
    subprocess.check_output("gzip -d sdcard.img.gz", shell=True)
    thread = threading.Thread(target=run_qemu_thread, args=(job, sbi, os_file, fs, out))
    thread.start()
    time.sleep(3)
    if not os.path.exists(out):
        with open(out, "w") as f:
            f.write("FAIL to run QEMU")
            return
    last_change_time = time.time()
    last_size = os.path.getsize(out)
    global error
    while error is None:
        cur_time = time.time()
        cur_size = os.path.getsize(out)
        if cur_size != last_size:
            last_change_time = cur_time
            last_size = cur_size
        else:
            if cur_time - last_change_time > 10:
                break
    return error, process


def run_qemu(job, sbi, os_file, fs, out):
    subprocess.check_output("gzip -d sdcard.img.gz", shell=True)
    gg.exec(f"cp {fs} initrd.img")
    cmd = f"qemu-system-riscv64 -machine virt -kernel {os_file} -m 128M -nographic -smp 2 -bios {sbi} -drive file={fs},if=none,format=raw,id=x0  -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0"
    job.add_log(cmd, "QEMU CMD")
    try:
        p = gg.exec(cmd, time_out=120)
    except subprocess.TimeoutExpired as e:
        p = e
    except subprocess.CalledProcessError as e:
        p = e
    f = open(out, "w")
    if p:
        if p.stdout and isinstance(p.stdout, bytes):
            p.stdout = p.stdout.decode(errors='ignore')
        if p.stderr and isinstance(p.stderr, bytes):
            p.stderr = p.stderr.decode(errors='ignore')
    f.write(f"{p.stdout}\n\n{p.stderr}")
    f.close()
    return error, process
