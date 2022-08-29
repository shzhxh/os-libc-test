目的
- 在github classroom上可以对任意OS进行libc-test测试，报告测试成绩

前提要求
- OS代码默认在kernel目录下，建议kernel目录以子模块的形式存在
- 在kernel目录下执行make命令要生成内核二进制文件：kernel
- OS要支持fat32文件系统，要能读出riscv.img里的测试程序

用法
```bash
pip3 install -r scripts/requirements.txt
make [PROJECT_PATH=<你的操作系统路径>]
```