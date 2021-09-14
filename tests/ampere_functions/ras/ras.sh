#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/ras.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

function ras_check_errors {
    modprobe einj || return 1
    # start record
    trace-cmd start -e mc_event -e non_standard_event -e arm_event || return 1
    # inject cpu errors
    echo 0x1 > /sys/kernel/debug/apei/einj/error_type || return 1
    echo 0x1 > /sys/kernel/debug/apei/einj/error_inject || return 1
    trace-cmd show | grep "ARM Processor Err"
    [ $? -ne 0 ] && return 1
    return 0
}

ras_check_errors
check_return altra:ras
