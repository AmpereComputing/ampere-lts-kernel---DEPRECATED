#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/altra_hwmon.txt"

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
    return 0
}

function hw_monitor_check_perm {
    hwmon_list=`find /sys/devices/platform -name "hwmon[0-9]"`
    for hwmon in $hwmon_list
    do
        echo "check permission in $hwmon"
        check_list=`find $hwmon -type f \( -name "power[0-9]_input" -o -name "energy*" \)`
        for file in $check_list
        do
            perm=`stat -c '%a' $file`
            [ "$perm" != "400" ] && echo "Wrong file permission in $file" && return 1
        done
    done
    return 0
}

# Verify patches in https://github.com/AmpereComputing/ampere-lts-kernel/issues/106"

hw_monitor_check_hwmon
check_return altra:hwmon

hw_monitor_check_perm
check_return altra:hwmon_perm
