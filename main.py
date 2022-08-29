import json
import os
import subprocess
import sys
import webbrowser

def clean_project(kernel_dir):
    file_list = ['initrd.img', 'kernel-qemu', 'os_serial_out.txt', 'sbi-qemu', 'sdcard.img']
    for file in file_list:
        path = os.path.join(kernel_dir, file)
        if os.path.exists(path):
            os.unlink(path)


def main():
    kernel = sys.argv[1]
    print(kernel)

    if kernel.startswith('http') or kernel.startswith('git@'):
        subprocess.call(f"git clone {kernel} kernel")

    kernel = os.path.join(os.getcwd(), kernel)
    print(kernel)

    clean_project(kernel)

    cmd = f"python3 script"
    print(cmd)
    output = subprocess.check_output(cmd, shell=True)

    result = json.loads(output)
    print(f"score: {result['score']}")
    with open("detail.html", "w", encoding='utf-8') as f:
        f.write(f"<div>{result['comment']}</div>")
        f.write(f"<div>{result['detail']}</div>")

    clean_project(kernel)
    webbrowser.open(os.path.join(os.getcwd(), "detail.html"))


if __name__ == '__main__':
    main()
