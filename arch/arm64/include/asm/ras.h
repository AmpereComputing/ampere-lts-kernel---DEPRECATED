/* SPDX-License-Identifier: GPL-2.0 */
#ifndef __ASM_RAS_H
#define __ASM_RAS_H

#define ERR_STATUS_AV		BIT(31)
#define ERR_STATUS_V		BIT(30)
#define ERR_STATUS_UE		BIT(29)
#define ERR_STATUS_ER		BIT(28)
#define ERR_STATUS_OF		BIT(27)
#define ERR_STATUS_MV		BIT(26)
#define ERR_STATUS_CE_SHIFT	24
#define ERR_STATUS_CE_MASK	0x3
#define ERR_STATUS_DE		BIT(23)
#define ERR_STATUS_PN		BIT(22)
#define ERR_STATUS_UET_SHIFT	20
#define ERR_STATUS_UET_MASK	0x3
#define ERR_STATUS_IERR_SHIFT	8
#define ERR_STATUS_IERR_MASK	0xff
#define ERR_STATUS_SERR_SHIFT	0
#define ERR_STATUS_SERR_MASK	0xff

#define ERR_FR_CEC_SHIFT	12
#define ERR_FR_CEC_MASK		0x7

#define ERR_FR_8B_CEC		BIT(1)
#define ERR_FR_16B_CEC		BIT(2)

struct ras_ext_regs {
	u64 err_fr;
	u64 err_ctlr;
	u64 err_status;
	u64 err_addr;
	u64 err_misc0;
	u64 err_misc1;
	u64 err_misc2;
	u64 err_misc3;
};

void arch_arm_ras_report_error(void);

#endif	/* __ASM_RAS_H */
