/* SPDX-License-Identifier: GPL-2.0 */
#ifndef AEST_H
#define AEST_H

#include <acpi/actbl.h>

#define ACPI_SIG_AEST			"AEST"	/* ARM Error Source Table */

#define AEST_NODE_TYPE_PROC		0
#define AEST_NODE_TYPE_MEM		1
#define AEST_NODE_TYPE_VENDOR		2

#define AEST_SYSTEM_REG_INTERFACE	0x0
#define AEST_MEMORY_MAPPED_INTERFACE	0x1

#define AEST_INTERRUPT_MODE		BIT(0)

#define AEST_MAX_PPI			4

#pragma pack(1)

struct acpi_table_aest {
	struct acpi_table_header header;
};

struct aest_type_header {
	u8 type;
	u16 length;
	u8 reserved;
	u32 revision;
	u32 data_offset;
	u32 interface_offset;
	u32 interface_size;
	u32 interrupt_offset;
	u32 interrupt_size;
	u64 timestamp_rate;
	u64 timestamp_start;
	u64 countdown_rate;
};

struct aest_proc_data {
	u32 id;
	u32 level;
	u32 cache_type;
};

struct aest_mem_data {
	u32 domain;
};

struct aest_vendor_data {
	u32 id;
	u32 data;
};

struct aest_interface {
	u8 type;
	u8 reserved[3];
	u32 flags;
	u64 address;
	u16 start_index;
	u16 num_records;
};

struct aest_interrupt {
	u8 type;
	u16 reserved;
	u8 flags;
	u32 gsiv;
	u8 iort_id[20];
};

#pragma pack()

struct aest_interface_data {
	u8 type;
	u16 start;
	u16 end;
	struct ras_ext_regs *regs;
};

union aest_node_spec {
	struct aest_proc_data proc;
	struct aest_mem_data mem;
	struct aest_vendor_data vendor;
};

struct aest_node_data {
	u8 node_type;
	struct aest_interface_data interface;
	union aest_node_spec data;
};

#endif /* AEST_H */
