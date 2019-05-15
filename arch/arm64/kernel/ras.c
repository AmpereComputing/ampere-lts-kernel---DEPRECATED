// SPDX-License-Identifier: GPL-2.0

#include <linux/kernel.h>
#include <linux/cpu.h>
#include <linux/smp.h>

#include <asm/ras.h>
#include <ras/ras_event.h>

void arch_arm_ras_report_error(void)
{
	u64 num_records;
	unsigned int i, cpu_num;
	bool fatal = false;
	struct ras_ext_regs regs;

	if (!this_cpu_has_cap(ARM64_HAS_RAS_EXTN))
		return;

	cpu_num = get_cpu();
	num_records = read_sysreg_s(SYS_ERRIDR_EL1);

	for (i = 0; i < num_records; i++) {
		write_sysreg_s(i, SYS_ERRSELR_EL1);
		regs.err_status = read_sysreg_s(SYS_ERXSTATUS_EL1);

		if (!(regs.err_status & ERR_STATUS_V))
			continue;

		pr_err("CPU%u: ERR%uSTATUS: 0x%llx\n", cpu_num, i,
		       regs.err_status);

		if (regs.err_status & ERR_STATUS_AV) {
			regs.err_addr = read_sysreg_s(SYS_ERXSTATUS_EL1);
			pr_err("CPU%u: ERR%uADDR: 0x%llx\n", cpu_num, i,
			       regs.err_addr);
		} else {
			regs.err_addr = 0;
		}

		regs.err_fr = read_sysreg_s(SYS_ERXFR_EL1);
		pr_err("CPU%u: ERR%uFR: 0x%llx\n", cpu_num, i, regs.err_fr);
		regs.err_ctlr = read_sysreg_s(SYS_ERXCTLR_EL1);
		pr_err("CPU%u: ERR%uCTLR: 0x%llx\n", cpu_num, i, regs.err_ctlr);

		if (regs.err_status & ERR_STATUS_MV) {
			regs.err_misc0 = read_sysreg_s(SYS_ERXMISC0_EL1);
			pr_err("CPU%u: ERR%uMISC0: 0x%llx\n", cpu_num, i,
			       regs.err_misc0);
			regs.err_misc1 = read_sysreg_s(SYS_ERXMISC1_EL1);
			pr_err("CPU%u: ERR%uMISC1: 0x%llx\n", cpu_num, i,
			       regs.err_misc1);
		}

		trace_arm_ras_ext_event(0, cpu_num, &regs);

		/*
		 * In the future, we will treat UER conditions as potentially
		 * recoverable.
		 */
		if (regs.err_status & ERR_STATUS_UE)
			fatal = true;

		write_sysreg_s(regs.err_status, SYS_ERXSTATUS_EL1);
	}

	if (fatal)
		panic("uncorrectable error encountered");

	put_cpu();
}
