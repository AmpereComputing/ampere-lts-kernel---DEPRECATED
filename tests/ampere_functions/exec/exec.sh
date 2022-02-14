#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/exec.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

# Test patch https://github.com/torvalds/linux/commit/38e0257e0e6f4fef2aa2966b089b56a8b1cfb75c
exec_erratum_1418040_check()
{
	numactl -C 2 ./clock_test.sh
	return $?
}

exec_erratum_1418040_check
check_return altra:exec

