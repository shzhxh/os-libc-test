# 变量
#   PROJECT_PATH : OS源码目录。默认值：kernel。
#   ARCH : 编译工具链的架构。默认值：riscv64。
# 目标
#   libc-test : 生成libc-test测试程序。放在repo/libc-test/disk目录。
#   image : 从repo/libc-test/disk生成镜像文件。
#   test : 运行测例。
#   clean : 清空编译生成的文件。

PROJECT_PATH ?= $(CURDIR)/kernel
ARCH ?= riscv64

# CC := $(ARCH)-linux-musl-gcc
# CACHE_URL := musl.cc
# CACHE_URL := https://github.com/YdrMaster/zCore/releases/download/musl-cache
# TOOLCHAIN_TGZ := $(ARCH)-linux-musl-cross.tgz
CC := $(ARCH)-buildroot-linux-musl-gcc
CACHE_URL := https://toolchains.bootlin.com/downloads/releases/toolchains/riscv64/tarballs
TOOLCHAIN_TGZ := $(ARCH)--musl--bleeding-edge-2020.08-1.tar.bz2
TOOLCHAIN_URL := $(CACHE_URL)/$(TOOLCHAIN_TGZ)
export PATH=$(shell printenv PATH):$(CURDIR)/toolchain/$(ARCH)--musl--bleeding-edge-2020.08-1/bin

.PHONY: toolchian libc-test test clean

toolchain: 
	if [ ! -f toolchain/$(TOOLCHAIN_TGZ) ]; then wget -P toolchain $(TOOLCHAIN_URL); fi
	tar -xf toolchain/$(TOOLCHAIN_TGZ) -C toolchain

libc-test:
	git submodule update --init repo/libc-test
	cd repo/libc-test && make disk

image: libc-test
	sudo mkfs.fat -C -F 32 $(ARCH).img 100000
	rm -rf tmp && mkdir tmp
	sudo mount $(ARCH).img ./tmp
	sudo cp -r repo/libc-test/disk/* ./tmp
	sync && sudo umount ./tmp
	rmdir tmp
	mv $(ARCH).img testdata/sdcard.img

test: image
	rm -rf output
	python3 main.py $(PROJECT_PATH)

clean:
	rm -f testdata/sdcard.img

