/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef IO_PGTABLE_ARM_H_
#define IO_PGTABLE_ARM_H_

#include <linux/io-pgtable.h>

#define ARM_LPAE_TCR_TG0_4K		0
#define ARM_LPAE_TCR_TG0_64K		1
#define ARM_LPAE_TCR_TG0_16K		2

#define ARM_LPAE_TCR_TG1_16K		1
#define ARM_LPAE_TCR_TG1_4K		2
#define ARM_LPAE_TCR_TG1_64K		3

#define ARM_LPAE_TCR_SH_NS		0
#define ARM_LPAE_TCR_SH_OS		2
#define ARM_LPAE_TCR_SH_IS		3

#define ARM_LPAE_TCR_RGN_NC		0
#define ARM_LPAE_TCR_RGN_WBWA		1
#define ARM_LPAE_TCR_RGN_WT		2
#define ARM_LPAE_TCR_RGN_WB		3

#define ARM_LPAE_TCR_PS_32_BIT		0x0ULL
#define ARM_LPAE_TCR_PS_36_BIT		0x1ULL
#define ARM_LPAE_TCR_PS_40_BIT		0x2ULL
#define ARM_LPAE_TCR_PS_42_BIT		0x3ULL
#define ARM_LPAE_TCR_PS_44_BIT		0x4ULL
#define ARM_LPAE_TCR_PS_48_BIT		0x5ULL
#define ARM_LPAE_TCR_PS_52_BIT		0x6ULL

#define ARM_LPAE_MAX_LEVELS		4

struct arm_lpae_io_pgtable {
	struct io_pgtable	iop;

	int			pgd_bits;
	int			start_level;
	int			bits_per_level;

	void			*pgd;
};

/* Struct accessors */
#define io_pgtable_to_data(x)						\
	container_of((x), struct arm_lpae_io_pgtable, iop)

#define io_pgtable_ops_to_data(x)					\
	io_pgtable_to_data(io_pgtable_ops_to_pgtable(x))

/* IOPTE accessors */
#define iopte_deref(pte, d) __va(iopte_to_paddr(pte, d))

/*
 * Calculate the index at level l used to map virtual address a using the
 * pagetable in d.
 */
#define ARM_LPAE_PGD_IDX(l, d)						\
	((l) == (d)->start_level ? (d)->pgd_bits - (d)->bits_per_level : 0)
/*
 * Calculate the right shift amount to get to the portion describing level l
 * in a virtual address mapped by the pagetable in d.
 */
#define ARM_LPAE_LVL_SHIFT(l, d)						\
	(((ARM_LPAE_MAX_LEVELS - (l)) * (d)->bits_per_level) +		\
	ilog2(sizeof(arm_lpae_iopte)))

typedef u64 arm_lpae_iopte;

bool iopte_leaf(arm_lpae_iopte pte, int lvl, enum io_pgtable_fmt fmt);
phys_addr_t iopte_to_paddr(arm_lpae_iopte pte,
			   struct arm_lpae_io_pgtable *data);
#endif /* IO_PGTABLE_ARM_H_ */
