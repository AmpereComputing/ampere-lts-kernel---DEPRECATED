// SPDX-License-Identifier: GPL-2.0

/* ARM Error Source Table Support */

#include <linux/acpi.h>
#include <linux/acpi_aest.h>
#include <linux/cpu.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/irq.h>
#include <linux/kernel.h>
#include <linux/percpu.h>
#include <linux/ratelimit.h>

#include <asm/ras.h>
#include <ras/ras_event.h>

#undef pr_fmt
#define pr_fmt(fmt) "ACPI AEST: " fmt

static struct acpi_table_header *aest_table;

static struct aest_node_data __percpu **ppi_data;
static int ppi_irqs[AEST_MAX_PPI];
static u8 num_ppi;
static u8 ppi_idx;

static void aest_print(struct aest_node_data *data, struct ras_ext_regs regs,
		       int index)
{
	/* No more than 2 corrected messages every 5 seconds */
	static DEFINE_RATELIMIT_STATE(ratelimit_corrected, 5*HZ, 2);

	if (regs.err_status & ERR_STATUS_UE ||
	    regs.err_status & ERR_STATUS_DE ||
	    __ratelimit(&ratelimit_corrected)) {
		switch (data->node_type) {
		case AEST_NODE_TYPE_PROC:
			pr_err("error from processor 0x%x\n",
			       data->data.proc.id);
			break;
		case AEST_NODE_TYPE_MEM:
			pr_err("error from memory domain 0x%x\n",
			       data->data.mem.domain);
			break;
		case AEST_NODE_TYPE_VENDOR:
			pr_err("error from vendor specific source 0x%x\n",
			       data->data.vendor.id);
		}

		pr_err("ERR%dSTATUS = 0x%llx\n", index, regs.err_status);
		if (regs.err_status & ERR_STATUS_AV)
			pr_err("ERR%dADDR = 0x%llx\n", index, regs.err_addr);

		pr_err("ERR%dFR = 0x%llx\n", index, regs.err_fr);
		pr_err("ERR%dCTLR = 0x%llx\n", index, regs.err_ctlr);

		if (regs.err_status & ERR_STATUS_MV) {
			pr_err("ERR%dMISC0 = 0x%llx\n", index, regs.err_misc0);
			pr_err("ERR%dMISC1 = 0x%llx\n", index, regs.err_misc1);
		}
	}
}

static void aest_proc(struct aest_node_data *data)
{
	struct ras_ext_regs *regs_p, regs;
	int i;
	bool fatal = false;

	/*
	 * Currently SR based handling is done through the architected
	 * discovery exposed through SRs. That may change in the future
	 * if there is supplemental information in the AEST that is
	 * needed.
	 */
	if (data->interface.type == AEST_SYSTEM_REG_INTERFACE) {
		arch_arm_ras_report_error();
		return;
	}

	regs_p = data->interface.regs;

	for (i = data->interface.start; i < data->interface.end; i++) {
		regs.err_status = readq(&regs_p[i].err_status);
		if (!(regs.err_status & ERR_STATUS_V))
			continue;

		if (regs.err_status & ERR_STATUS_AV)
			regs.err_addr = readq(&regs_p[i].err_addr);
		else
			regs.err_addr = 0;

		regs.err_fr = readq(&regs_p[i].err_fr);
		regs.err_ctlr = readq(&regs_p[i].err_ctlr);

		if (regs.err_status & ERR_STATUS_MV) {
			regs.err_misc0 = readq(&regs_p[i].err_misc0);
			regs.err_misc1 = readq(&regs_p[i].err_misc1);
		} else {
			regs.err_misc0 = 0;
			regs.err_misc1 = 0;
		}

		aest_print(data, regs, i);

		trace_arm_ras_ext_event(data->node_type, data->data.proc.id,
					&regs);

		if (regs.err_status & ERR_STATUS_UE)
			fatal = true;

		writeq(regs.err_status, &regs_p[i].err_status);
	}

	if (fatal)
		panic("AEST: uncorrectable error encountered");

}

static irqreturn_t aest_irq_func(int irq, void *input)
{
	struct aest_node_data *data = input;

	aest_proc(data);

	return IRQ_HANDLED;
}

static int __init aest_register_gsi(u32 gsi, int trigger, void *data)
{
	int cpu, irq;

	if (gsi < 16 || gsi >= 1020) {
		pr_err("invalid GSI %d\n", gsi);
		return -EINVAL;
	}

	irq = acpi_register_gsi(NULL, gsi, trigger, ACPI_ACTIVE_HIGH);
	if (irq == -EINVAL) {
		pr_err("failed to map AEST GSI %d\n", gsi);
		return -EINVAL;
	}

	if (gsi < 32) {
		if (ppi_idx >= AEST_MAX_PPI) {
			pr_err("Unable to register PPI %d\n", gsi);
			return -EINVAL;
		}
		ppi_irqs[ppi_idx] = irq;
		for_each_possible_cpu(cpu) {
			memcpy(per_cpu_ptr(ppi_data[ppi_idx], cpu), data,
			       sizeof(struct aest_node_data));
		}
		if (request_percpu_irq(irq, aest_irq_func, "AEST",
				       ppi_data[ppi_idx++])) {
			pr_err("failed to register AEST IRQ %d\n", irq);
			return -EINVAL;
		}
	} else if (gsi < 1020) {
		if (request_irq(irq, aest_irq_func, IRQF_SHARED, "AEST",
				data)) {
			pr_err("failed to register AEST IRQ %d\n", irq);
			return -EINVAL;
		}
	}

	return 0;
}

static int __init aest_init_interrupts(struct aest_type_header *node,
				       struct aest_node_data *data)
{
	struct aest_interrupt *interrupt;
	int i, trigger, ret = 0;

	interrupt = ACPI_ADD_PTR(struct aest_interrupt, node,
				 node->interrupt_offset);

	for (i = 0; i < node->interrupt_size; i++, interrupt++) {
		trigger = (interrupt->flags & AEST_INTERRUPT_MODE) ?
			  ACPI_LEVEL_SENSITIVE : ACPI_EDGE_SENSITIVE;
		if (aest_register_gsi(interrupt->gsiv, trigger, data))
			ret = -EINVAL;
	}

	return ret;
}

static int __init aest_init_interface(struct aest_type_header *node,
				       struct aest_node_data *data)
{
	struct aest_interface *interface;
	struct resource *res;
	int size;

	interface = ACPI_ADD_PTR(struct aest_interface, node,
				 node->interface_offset);

	if (interface->type > AEST_MEMORY_MAPPED_INTERFACE) {
		pr_err("invalid interface type: %d\n", interface->type);
		return -EINVAL;
	}

	data->interface.type = interface->type;

	/*
	 * Currently SR based handling is done through the architected
	 * discovery exposed through SRs. That may change in the future
	 * if there is supplemental information in the AEST that is
	 * needed.
	 */
	if (interface->type == AEST_SYSTEM_REG_INTERFACE)
		return 0;

	res = kzalloc(sizeof(struct resource), GFP_KERNEL);
	if (!res)
		return -ENOMEM;

	size = interface->num_records * sizeof(struct ras_ext_regs);
	res->name = "AEST";
	res->start = interface->address;
	res->end = res->start + size;
	res->flags = IORESOURCE_MEM;
	if (request_resource_conflict(&iomem_resource, res)) {
		pr_err("unable to request region starting at 0x%llx\n",
			res->start);
		kfree(res);
		return -EEXIST;
	}

	data->interface.start = interface->start_index;
	data->interface.end = interface->start_index + interface->num_records;

	data->interface.regs = ioremap(interface->address, size);
	if (data->interface.regs == NULL)
		return -EINVAL;

	return 0;
}

static int __init aest_init_node(struct aest_type_header *node)
{
	struct aest_node_data *data;
	union aest_node_spec *node_spec;
	int ret;

	data = kzalloc(sizeof(struct aest_node_data), GFP_KERNEL);
	if (!data)
		return -ENOMEM;

	data->node_type = node->type;

	node_spec = ACPI_ADD_PTR(union aest_node_spec, node, node->data_offset);

	switch (node->type) {
	case AEST_NODE_TYPE_PROC:
		memcpy(&data->data, node_spec, sizeof(struct aest_proc_data));
		break;
	case AEST_NODE_TYPE_MEM:
		memcpy(&data->data, node_spec, sizeof(struct aest_mem_data));
		break;
	case AEST_NODE_TYPE_VENDOR:
		memcpy(&data->data, node_spec, sizeof(struct aest_vendor_data));
		break;
	default:
		return -EINVAL;
	}

	ret = aest_init_interface(node, data);
	if (ret) {
		kfree(data);
		return ret;
	}

	return aest_init_interrupts(node, data);
}

static void aest_count_ppi(struct aest_type_header *node)
{
	struct aest_interrupt *interrupt;
	int i;

	interrupt = ACPI_ADD_PTR(struct aest_interrupt, node,
				 node->interrupt_offset);

	for (i = 0; i < node->interrupt_size; i++, interrupt++) {
		if (interrupt->gsiv >= 16 && interrupt->gsiv < 32)
			num_ppi++;
	}

}

static int aest_starting_cpu(unsigned int cpu)
{
	int i;

	for (i = 0; i < num_ppi; i++) {
		enable_percpu_irq(ppi_irqs[i], IRQ_TYPE_NONE);
	}

	return 0;
}

static int aest_dying_cpu(unsigned int cpu)
{
	return 0;
}

int __init acpi_aest_init(void)
{
	struct acpi_table_aest *aest;
	struct aest_type_header *aest_node, *aest_end;
	int i, ret = 0;

	if (acpi_disabled)
		return 0;

	if (ACPI_FAILURE(acpi_get_table(ACPI_SIG_AEST, 0, &aest_table))) {
		pr_err("Failed to get AEST table\n");
		return -EINVAL;
	}

	pr_info("Initializing AEST driver\n");
	aest = (struct acpi_table_aest *) aest_table;

	/* Get the first AEST node */
	aest_node = ACPI_ADD_PTR(struct aest_type_header, aest,
				 sizeof(struct acpi_table_aest));
	/* Pointer to the end of the AEST table */
	aest_end = ACPI_ADD_PTR(struct aest_type_header, aest,
				aest_table->length);

	while (aest_node < aest_end) {
		if (((u64)aest_node + aest_node->length) > (u64)aest_end) {
			pr_err("AEST node pointer overflow, bad table\n");
			return -EINVAL;
		}

		aest_count_ppi(aest_node);

		aest_node = ACPI_ADD_PTR(struct aest_type_header, aest_node,
					 aest_node->length);
	}

	if (num_ppi > AEST_MAX_PPI) {
		pr_warn("Limiting PPI support to %d PPIs\n", AEST_MAX_PPI);
		num_ppi = AEST_MAX_PPI;
	}

	ppi_data = kcalloc(num_ppi, sizeof(struct aest_node_data *),
			   GFP_KERNEL);

	for (i = 0; i < num_ppi; i++) {
		ppi_data[i] = alloc_percpu(struct aest_node_data);
		if (!ppi_data[i]) {
			ret = -ENOMEM;
			break;
		}
	}

	if (ret) {
		pr_err("Failed percpu allocation\n");
		for (i = 0; i < num_ppi; i++)
			free_percpu(ppi_data[i]);
		return ret;
	}

	aest_node = ACPI_ADD_PTR(struct aest_type_header, aest,
				 sizeof(struct acpi_table_aest));

	while (aest_node < aest_end) {
		ret = aest_init_node(aest_node);
		if (ret)
			pr_warn("failed to init node: %d", ret);

		aest_node = ACPI_ADD_PTR(struct aest_type_header, aest_node,
					 aest_node->length);
	}

	cpuhp_setup_state(CPUHP_AP_ARM_AEST_STARTING,
			  "drivers/acpi/arm64/aest:starting",
			  aest_starting_cpu, aest_dying_cpu);

	return 0;
}

early_initcall(acpi_aest_init);
