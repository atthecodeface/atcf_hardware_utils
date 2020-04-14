CDL_ROOT=/Users/gavinprivate/Git/cdl_tools_grip/tools
include ${CDL_ROOT}/lib/cdl/cdl_templates.mk
BUILD_ROOT=$(abspath ${CURDIR})/build

SIM ?= $(abspath ${CURDIR})/sim
ATCF_HARDWARE_UTILS ?= $(abspath ${CURDIR})

all: sim

smoke: sim
	(cd test && PATH=${ATCF_HARDWARE_UTILS}/python:${PATH} ${MAKE} SIM=${SIM} smoke)

-include ${BUILD_ROOT}/Makefile

verilog: ${VERILOG_FILES}

${BUILD_ROOT}/Makefile:
	./cdl_desc.py > $@

clean:
	rm -rf ${BUILD_ROOT}/Makefile
	mkdir -p ${BUILD_ROOT}
