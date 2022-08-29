

PROJECT_PATH ?= $(CURDIR)/kernel

test:
	echo $(PROJECT_PATH)
	python3 main.py $(PROJECT_PATH)
