#!/bin/bash

. ../../lib/sh-test-lib
OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"
LOGFILE="${OUTPUT}/altra_pmu.txt"

! check_root && error_msg "You need to be root to run this script."
create_out_dir "${OUTPUT}"

function pmu_check_arm_cmn {
	tmpresult=/tmp/pmu_check_arm_cmn.log
	rm -f $tmpresult
	perf stat -I 1000 --interval-count 1 -D 200 -C 0 -e 'arm_cmn/dtc_cycles/' &> $tmpresult || return 1
	grep "not supported" $tmpresult && return 1
	dct_cycles=$(cat $tmpresult | grep "arm_cmn\/dtc_cycles\/" | awk '{print $2}' | sed "s/,//g")
	mesh_freq_in_GHz=$(echo "scale=2; $dct_cycles/1000000000" | bc) 
	echo "Mesh Freq: ${mesh_freq_in_GHz} GHz"
}

function pmu_check_arm_dmc {
	tmpresult=/tmp/pmu_check_arm_dmc.log
	rm -f $tmpresult
	events_list='dmc620_0/clk_cycle_count/,dmc620_8/clk_cycle_count/,dmc620_0/clkdiv2_rdwr/,dmc620_1/clkdiv2_rdwr/,dmc620_2/clkdiv2_rdwr/,dmc620_3/clkdiv2_rdwr/,dmc620_4/clkdiv2_rdwr/,dmc620_5/clkdiv2_rdwr/,dmc620_6/clkdiv2_rdwr/,dmc620_7/clkdiv2_rdwr/,dmc620_8/clkdiv2_rdwr/,dmc620_9/clkdiv2_rdwr/,dmc620_10/clkdiv2_rdwr/,dmc620_11/clkdiv2_rdwr/,dmc620_12/clkdiv2_rdwr/,dmc620_13/clkdiv2_rdwr/,dmc620_14/clkdiv2_rdwr/,dmc620_15/clkdiv2_rdwr/'
	perf stat -I 1000 --interval-count 1 -D 200 -C 0 -e $events_list &> $tmpresult || return 1
	grep "not supported" $tmpresult && return 1

	dct_0_cycle=$(cat $tmpresult | grep "dmc620_0\/clk_cycle_count\/" | awk '{print $2}' | sed "s/,//g")
	node_0_DIMM_freq_in_GHz=$(echo "scale=1; $dct_0_cycle/1000000000*2" | bc)
	echo "Node 0 Mem Freq: ${node_0_DIMM_freq_in_GHz} GHz"

	dct_8_cycle=$(cat $tmpresult | grep "dmc620_8\/clk_cycle_count\/" | awk '{print $2}' | sed "s/,//g")
	node_1_DIMM_freq_in_GHz=$(echo "scale=1; $dct_8_cycle/1000000000*2" | bc)
	echo "Node 1 Mem Freq: ${node_1_DIMM_freq_in_GHz} GHz"

	chan_sum=$(for i in $(seq 0 7); do 
		cat $tmpresult | grep "dmc620_${i}\/clkdiv2_rdwr\/" | awk '{print $2}' | sed "s/,//g" 
	done | awk '{s+=$1}END{print s}')
	node_0_mem_bw=$(echo "scale=1; $chan_sum * 64 / 1000000" | bc)
	echo "Node 0 Mem BW: $node_0_mem_bw MB/sec"

	chan_sum=$(for i in $(seq 8 15); do
		cat $tmpresult | grep "dmc620_${i}\/clkdiv2_rdwr\/" | awk '{print $2}' | sed "s/,//g" 
	done | awk '{s+=$1}END{print s}')
	node_1_mem_bw=$(echo "scale=1; $chan_sum * 64 / 1000000" | bc)
	echo "Node 1 Mem BW: $node_1_mem_bw MB/sec"
}

function pmu_check_arm_dsu {
	tmpresult=/tmp/pmu_check_arm_dsu.log
	rm -f $tmpresult
	dsu_events_count=$(perf list | grep 'arm_dsu_.*/cycles' | wc -l)
	[ $dsu_events_count -eq 0 ] && return 1
	dsu_events=$(perf list | grep 'arm_dsu_.*/cycles' | awk '{print $1}' | tr '\n' ',')
	perf stat -a -e "${dsu_events%?}" -- sleep 1 &> $tmpresult || return 1
	grep "not supported" $tmpresult && return 1
	return 0
}

function pmu_check_arm_smmuv3 {
	tmpresult=/tmp/pmu_check_arm_smmuv3.log
	rm -f $tmpresult
	smmu_events_count=$(perf list | grep 'smmuv3_pmcg_.*/cycles' | wc -l)
	[ $smmu_events_count -eq 0 ] && return 1
	smmu_events=$(perf list | grep 'smmuv3_pmcg_.*/cycles' | awk '{print $1}' | tr '\n' ',')
	perf stat -a -e "${smmu_events%?}" -- sleep 1 &> $tmpresult || return 1
	grep "not supported" $tmpresult && return 1
	return 0
}

function pmu_check_arm_spe {
	spe_events=$(perf list | grep arm_spe | wc -l)
	[ $spe_events -eq 0 ] && return 1
	perf record -e arm_spe/ts_enable=1,pa_enable=1/ dd if=/dev/zero of=/dev/null count=10000 &> /dev/null
	perf report --dump-raw-trace | grep "ARM SPE"
	[ $? -ne 0 ] && return 1
	return 0
}

pmu_check_arm_cmn
check_return altra_pmu:arm_cmn

pmu_check_arm_dmc
check_return altra_pmu:arm_dmc

pmu_check_arm_dsu
check_return altra_pmu:arm_dsu

pmu_check_arm_smmuv3
check_return altra_pmu:arm_smmuv3

pmu_check_arm_spe
check_return altra_pmu:arm_spe

rm -f /tmp/pmu_check_*
