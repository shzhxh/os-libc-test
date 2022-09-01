# 变量
#   PROJECT_PATH : OS源码目录。默认值：kernel。
#   ARCH : 编译工具链的架构。默认值：riscv64。
# 目标
#   libc-test : 生成libc-test测试程序。放在rootfs/$(ARCH)目录。
#   image : 从rootfs/$(ARCH)生成镜像文件。
#   test : 运行测例。

PROJECT_PATH ?= $(CURDIR)/kernel
ARCH ?= riscv64

CC := $(ARCH)-linux-musl-gcc
# CACHE_URL := musl.cc
CACHE_URL := https://github.com/YdrMaster/zCore/releases/download/musl-cache
TOOLCHAIN_TGZ := $(ARCH)-linux-musl-cross.tgz
TOOLCHAIN_URL := $(CACHE_URL)/$(TOOLCHAIN_TGZ)
export PATH=$(shell printenv PATH):$(CURDIR)/toolchain/$(ARCH)-linux-musl-cross/bin

.PHONY: libc-test test

libc-test: 
ifneq ($(shell which $(CC)), 0)
	if [ ! -f toolchain/$(TOOLCHAIN_TGZ) ]; then wget -P toolchain $(TOOLCHAIN_URL); fi
endif
	tar -xf toolchain/$(TOOLCHAIN_TGZ) -C toolchain
	echo $(PATH)
	cd libc-test && make disk

image: libc-test
	sudo mkfs.fat -C -F 32 $(ARCH).img 100000
	rm -rf tmp && mkdir tmp
	sudo mount $(ARCH).img ./tmp
	sudo cp -r libc-test/disk/* ./tmp
	sync && sudo umount ./tmp
	rmdir tmp
	mv $(ARCH).img testdata/sdcard.img

test: image
	rm -rf output
	python3 main.py $(PROJECT_PATH)

