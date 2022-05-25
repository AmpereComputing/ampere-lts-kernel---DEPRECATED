#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <asm/memory.h>

#define ARMV8_PMUSERENR_EN_EL0  (1ULL << 0) /*  EL0 access enable */
#define ARMV8_PMCNTENSET_EL0_ENABLE (1ULL<<31) /* *< Enable Perf count reg */

/*
 *  * Per-CPU PMCR: config reg
 *   */
#define ARMV8_PMU_PMCR_E        (1 << 0) /* Enable all counters */
#define ARMV8_PMU_PMCR_P        (1 << 1) /* Reset all counters */
#define ARMV8_PMU_PMCR_C        (1 << 2) /* Cycle counter reset */
#define ARMV8_PMU_PMCR_D        (1 << 3) /* CCNT counts every 64th cpu cycle */
#define ARMV8_PMU_PMCR_X        (1 << 4) /* Export to ETM */
#define ARMV8_PMU_PMCR_DP       (1 << 5) /* Disable CCNT if non-invasive debug*/
#define ARMV8_PMU_PMCR_LC       (1 << 6) /* Overflow on 64 bit cycle counter */
#define ARMV8_PMU_PMCR_LP       (1 << 7) /* Long event counter enable */
#define ARMV8_PMU_PMCR_N_SHIFT  11       /* Number of counters supported */
#define ARMV8_PMU_PMCR_N_MASK   0x1f
#define ARMV8_PMU_PMCR_MASK     0xff     /* Mask for writable bits */

static inline u32 armv8pmu_pmcr_read(void)
{
	u64 val=0;
	asm volatile("mrs %0, pmcr_el0" : "=r" (val));
	return (u32)val;
}
static inline void armv8pmu_pmcr_write(u32 val)
{
        val &= ARMV8_PMU_PMCR_MASK;
        isb();
        asm volatile("msr pmcr_el0, %0" : : "r" ((u64)val));
}

SYSCALL_DEFINE1(bhi_addr, uint64_t, pfn) {
    uint64_t addr;
    
    //addr = __va((pfn) << PAGE_SHIFT);
    addr = (uint64_t)pfn_to_kaddr(pfn);
    printk("pfn: 0x%llx, addr: 0x%llx, PAGE_OFFSET: 0x%llx, PHYS_OFFSET: 0x%llx\n", pfn, addr, PAGE_OFFSET, PHYS_OFFSET);
    return addr;
}

SYSCALL_DEFINE1(bhi_hit, uint64_t *, ptr) {
    return *ptr;
}

SYSCALL_DEFINE0(bhi_enable) {
    uint64_t val;

    /*  Enable user-mode access to counters. */
    isb();
    asm volatile("msr pmuserenr_el0, %0" : : "r"((u64)ARMV8_PMUSERENR_EN_EL0));
    isb();
    asm volatile("mrs %0, pmuserenr_el0" : "=r" (val));
    armv8pmu_pmcr_write(armv8pmu_pmcr_read() | ARMV8_PMU_PMCR_E);
    printk("pmuserenr_el0 = 0x%016lx, pmcr: = 0x%x, on core: %d\n", val, armv8pmu_pmcr_read(), smp_processor_id());

    /* Enables the cycle counter register */
    asm volatile("msr pmcntenset_el0, %0" : : "r" (ARMV8_PMCNTENSET_EL0_ENABLE));

    /* Print register id_aa64pfr0_el1 to verify if CSV2 is supported */
    asm volatile("mrs %0, id_aa64pfr0_el1" : "=r" (val));
    printk("id_aa64pfr0_el1 = 0x%016lx\n", val);

    return val;
}
