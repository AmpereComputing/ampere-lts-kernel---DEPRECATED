#!/bin/bash

sys_time=`TIME="%S" time ./read_tsc 2>&1`
[ 1 -eq "$(echo "${sys_time} != 0" | bc)" ] && echo "non-zero systime in CNTVCT_EL1 reading before test" && exit 1

./test_32bit > /dev/null

sys_time=`TIME="%S" time ./read_tsc 2>&1`
[ 1 -eq "$(echo "${sys_time} != 0" | bc)" ] && echo "non-zero systime in CNTVCT_EL1 reading" && exit 1

exit 0
