#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/smmu_filter_fix.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

# check https://github.com/AmpereComputing/ampere-lts-kernel/issues/53 if test failed
function smmuv3_global_filter_check {
    result=$(perf stat -e smmuv3_pmcg_27ffe0202/transaction/,smmuv3_pmcg_27ffe0202/tlb_miss/ -a sleep 5 2>&1 | grep smmuv3_pmcg | awk '{print $1}')
    for i in $result
    do
        [ $i -ne 0 ] && echo "Except zero counter" && return 1
    done
    return 0
}

smmuv3_global_filter_check
check_return altra:smmu_filter_fix
