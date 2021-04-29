#!/bin/env python3

import subprocess
import sys
import re

def get_sysfs_node_size(idx):
    cmd_out = subprocess.check_output("cat /sys/devices/system/node/node%d/meminfo | grep MemTotal" % idx, shell=True).decode('utf-8')
    mem_total = cmd_out.split()[3]
    return int(mem_total) * 1024

def MB(size):
    return size / 1024 / 1024

ret = subprocess.run('cat /boot/config-`uname -r` | grep -q "CONFIG_NODES_SPAN_OTHER_NODES=y"', shell=True)
if ret.returncode != 0:
    print("CONFIG_NODES_SPAN_OTHER_NODES is not set")
    sys.exit(1)

srat_out = subprocess.check_output('dmesg | grep "SRAT: Node"', shell=True).decode('utf-8')
nodes_size = {}
for line in srat_out.split('\n'):
    matched = re.match(".*ACPI: SRAT: Node (\d+) PXM \d+ \[mem 0x([0-9a-fA-F]+)-0x([0-9a-fA-F]+)\]$", line)
    if matched:
        node_num = int(matched.group(1))
        start_addr = int(matched.group(2), 16)
        end_addr = int(matched.group(3), 16)
        if node_num not in nodes_size:
            nodes_size[node_num] = end_addr - start_addr
        else:
            nodes_size[node_num] += end_addr - start_addr

for idx, nsize in sorted(nodes_size.items()):
    sysfs_size = get_sysfs_node_size(idx)
    delta = abs(nsize - sysfs_size)
    print("Numa Node %d: ACPI SRAT size %d MB, Kernel Reported %d MB, Delta %d MB" % (idx, MB(nsize), MB(sysfs_size), MB(delta)))

sys.exit(0)