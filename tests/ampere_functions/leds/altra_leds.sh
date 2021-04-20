#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/altra_leds.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

function write_note {
    echo $1 > $2
}

function leds_check_led {
    # blink test
    write_note 000b:03 /sys/class/leds/altra:led/address || return 1
    write_note 4 /sys/class/leds/altra:led/blink || return 1
    write_note 0 /sys/class/leds/altra:led/shot || return 1
    sleep 1
    # on/off test
    write_note 000b:03 /sys/class/leds/altra:led/address || return 1
    write_note 1 /sys/class/leds/altra:led/brightness || return 1
    write_note 0 /sys/class/leds/altra:led/brightness || return 1
    return 0
}

leds_check_led
check_return altra:led
