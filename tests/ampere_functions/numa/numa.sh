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
    [ $node_cnt -lt 8 ] && echo "This test expected more than 8 numa nodes. In BIOS please set: Chipset -> CPU Configuration -> ANC mode -> Quadrant" && return 1
    return 0
}

function numa_device_alloc {
    mount /dev/nvme1n1 /mnt/fiotest/
    echo 3 > /proc/sys/vm/drop_caches
    tmplog=`mktemp`
    numactl -N 1 -m 1 fio --ioengine=libaio --randrepeat=0 --norandommap --thread --direct=0 --buffered=1 --group_reporting --name=seqdztest --ramp_time=5 --runtime=20 --time_based --numjobs=5 --iodepth=32 --directory=/mnt/fiotest --size=50G --rw=read --bs=256k --output=${tmplog}
    echo
    bw=`cat ${tmplog} | grep -oP '(?<=READ: bw=)(\d+)(?=MiB/s )'`
    rm -f ${tmplog}
    [ $bw -lt 2000 ] && return 1
    return 0
}

numa_check_node
check_return altra:numa

./srat_overlap_check.py
check_return altra:srat_overlap_check

numa_device_alloc
check_return altra:device_alloc
