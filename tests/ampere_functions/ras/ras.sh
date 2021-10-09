#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/ras.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

function ras_check_errors {
    dmesg -C
    modprobe einj || return 1
    # start record
    trace-cmd start -e mc_event -e non_standard_event -e arm_event || return 1
    # inject cpu errors
    echo 0x1 > /sys/kernel/debug/apei/einj/error_type || return 1
    echo 0x1 > /sys/kernel/debug/apei/einj/error_inject || return 1
    trace-cmd show | grep "ARM Processor Err"
    if [ $? -ne 0 ]; then
        # Hardware EINJ enabled in BIOS
        dmesg | egrep "CPU[0-9]+: ERR"
        [ $? -ne 0 ] && return 1
    fi
    trace-cmd stop
    return 0
}

function ras_check_ext_errors {
    dmesg -C
    modprobe einj || return 1
    # start record
    trace-cmd start -e mc_event -e non_standard_event -e arm_event -e arm_ras_ext_event || return 1
    # inject cpu errors
    echo 0x1 > /sys/kernel/debug/apei/einj/error_type || return 1
    echo 0x0 > /sys/kernel/debug/apei/einj/param3 || return 1
    echo 0x1 > /sys/kernel/debug/apei/einj/flags || return 1
    echo 0x1 > /sys/kernel/debug/apei/einj/error_inject || return 1
    trace-cmd show | grep "ARM Processor Err"
    if [ $? -ne 0 ]; then
        # Hardware EINJ enabled in BIOS
        dmesg | egrep "CPU[0-9]+: ERR"
        [ $? -ne 0 ] && return 1
    fi
    trace-cmd stop
    return 0
}

ras_check_errors
check_return altra:ras

ras_check_ext_errors
check_return altra:ras_ext