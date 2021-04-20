#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/altra_leds.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

function hw_monitor_check_hwmon {
    echo "Found hw monitor modules: $(lsmod | grep hwmon | awk '{printf $1" "}')"
    hwmon_devices=$(ls -l /sys/class/hwmon | wc -l)
    [ ${hwmon_devices} -lt 1 ] && return 1
    for hwmon_path in /sys/class/hwmon/hwmon*; do
        mod_name=$(cat ${hwmon_path}/name)
        temp_label=$(cat ${hwmon_path}/temp1_label)
        temp=$(cat ${hwmon_path}/temp1_input)
        echo "${temp_label}(${mod_name}): ${temp}"
    done
}

hw_monitor_check_hwmon
check_return altra:hwmon
