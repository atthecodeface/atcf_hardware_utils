Q=@
CDL_REGRESS = ${CDL_ROOT}/libexec/cdl/cdl_regress.py

SMOKE_OPTIONS ?= --only-tests 'smoke'
SMOKE_TESTS   ?= test_dprintf test_clock_divider test_fifo test_byte_fifo_multiaccess test_dbg_dprintf
SMOKE_TESTS   ?= test_async
REGRESS_TESTS ?= test_async test_byte_fifo_multiaccess test_clock_divider test_dprintf test_fifo test_dbg_dprintf
CDL_REGRESS_PACKAGE_DIRS = --package-dir regress:${SRC_ROOT}/python  --package-dir regress:${GRIP_ROOT_PATH}/atcf_hardware_utils/python --package-dir regress:${GRIP_ROOT_PATH}/atcf_hardware_apb/python

.PHONY:smoke
smoke:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT}  ${CDL_REGRESS_PACKAGE_DIRS} --suite-dir=python ${SMOKE_OPTIONS} ${SMOKE_TESTS} ${WAVES}

.PHONY:regress
regress:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT} ${CDL_REGRESS_PACKAGE_DIRS} --suite-dir=python ${REGRESS_TESTS}
