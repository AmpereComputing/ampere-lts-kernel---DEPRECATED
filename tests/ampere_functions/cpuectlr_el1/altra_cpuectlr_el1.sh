#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/cpuectlr_el1.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

function cpuectlr_el1_driver_check {
    modprobe altra_cpuectlr_el1 || return 1
    [ ! -f /sys/firmware/altra_cpuectlr/cpuectlr_el1_value ] && echo "/sys/firmware/altra_cpuectlr not exist" && return 1

    signature=`cat /sys/firmware/altra_cpuectlr/signature`
    [ "$signature" != "0x43504d41" ] && echo "signature not match" && return 1

    echo 0xffff > /sys/firmware/altra_cpuectlr/cpuectlr_el1_wen_mask
    mask=`cat /sys/firmware/altra_cpuectlr/cpuectlr_el1_wen_mask`
    [ "$mask" != "0xb1a0" ] && echo "cpuectlr_el1_wen_mask should only allow prefetcher bits" && return 1

    echo 0xff > /sys/firmware/altra_cpuectlr/cpuectlr_el1_value
    value=`cat /sys/firmware/altra_cpuectlr/cpuectlr_el1_value`
    [ "$value" != "0xff" ] && echo "cpuectlr_el1_value not match" && return 1

    return 0
}

cpuectlr_el1_driver_check
check_return altra:cpuectlr_el1
