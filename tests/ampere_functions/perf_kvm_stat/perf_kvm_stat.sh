#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/perf_kvm_stat.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

# check if perf kvm stat command is supported in arm64
function perf_kvm_stat_check {
    perf kvm stat record -a sleep 1 > /dev/null 2>&1
    [ $? -ne 0 ] && echo "perf kvm stat is not supported" && return 1
    return 0
}

perf_kvm_stat_check
check_return altra:perf_kvm_stat
