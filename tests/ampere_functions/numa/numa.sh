#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/altra_leds.txt"

create_out_dir "${OUTPUT}"

function numa_check_node {
    cat /boot/config-`uname -r` | grep -q "CONFIG_NODES_SHIFT=6"
    [ $? -ne 0 ] && echo "CONFIG_NODES_SHIFT not set in current kernel" && return 1
    node_cnt=$(numactl -H | grep "node .* cpus:" | wc -l)
    info_msg "Found $node_cnt numa node"
    [ $node_cnt -ne 8 ] && echo "expected 8 numa nodes" && return 1
    return 0
}

numa_check_node
check_return altra:numa

./srat_overlap_check.py
check_return altra:srat_overlap_check
