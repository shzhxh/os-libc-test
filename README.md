目的
- 在github classroom上可以对任意OS进行libc-test测试，报告测试成绩

前提要求
- OS代码默认在kernel目录下，建议kernel目录以子模块的形式存在
- 在kernel目录下执行make命令要生成内核二进制文件：kernel-qemu
- OS要支持fat32文件系统，要能读出sdcard.img里的测试程序

用法
```bash
git submodule add <os_url> kernel   # 待测OS代码作为子模块
git submodule update --init # 下载repo目录下的子模块
make image
pip3 install -r scripts/requirements.txt
make test
```

结果
- 在网页 : https://<org_name>.github.io/<repo_name>/detail.html

  注：需要先在设置里把gh-pages分支作为本仓库的Pages。