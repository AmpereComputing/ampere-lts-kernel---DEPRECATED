// SPDX-License-Identifier: GPL-2.0
#include <linux/debugfs.h>
#include <linux/iommu.h>
#include <linux/io-pgtable.h>
#include <linux/pci.h>
#include "arm-smmu-v3.h"
#include "../../io-pgtable-arm.h"

#undef pr_fmt
#define pr_fmt(fmt)	"SMMUv3 debug: " fmt

#define NAME_BUF_LEN 32

static struct dentry *arm_smmu_debug;
static char dump_pci_dev[NAME_BUF_LEN];
static u32 pasid;
static struct mutex lock;

static ssize_t master_pdev_read(struct file *filp, char __user *buf,
				size_t count, loff_t *pos)
{
	char pdev_name[NAME_BUF_LEN];
	char name[NAME_BUF_LEN];
	int ret;

	mutex_lock(&lock);
	strncpy(pdev_name, dump_pci_dev, NAME_BUF_LEN);
	mutex_unlock(&lock);

	if (!strlen(pdev_name)) {
		pr_err("Please set pci_dev firstly\n");
		return 0;
	}

	ret = scnprintf(name, NAME_BUF_LEN, "%s\n", pdev_name);
	return simple_read_from_buffer(buf, count, pos, name, ret);
}

static ssize_t master_pdev_write(struct file *filp, const char __user *buf,
				 size_t count, loff_t *pos)
{
	char name[NAME_BUF_LEN];
	struct device *dev;
	int len;

	if (*pos != 0)
		return 0;

	if (count >= NAME_BUF_LEN)
		return -ENOSPC;

	len = simple_write_to_buffer(name, NAME_BUF_LEN - 1, pos, buf, count);
	if (len < 0)
		return len;
	name[len] = '\0';

	dev = bus_find_device_by_name(&pci_bus_type, NULL, name);
	if (!dev) {
		pr_err("Failed to find device\n");
		return -EINVAL;
	}

	mutex_lock(&lock);
	strncpy(dump_pci_dev, dev_name(dev), NAME_BUF_LEN);
	mutex_unlock(&lock);

	put_device(dev);

	return count;
}

static const struct file_operations master_pdev_fops = {
	.owner = THIS_MODULE,
	.open = simple_open,
	.read = master_pdev_read,
	.write = master_pdev_write,
};

static struct arm_smmu_master *arm_smmu_get_master(struct device *dev)
{
	struct arm_smmu_master *master;

	if (!dev->iommu) {
		pr_err("master device driver may not be loaded!\n");
		return NULL;
	}

	master = dev_iommu_priv_get(dev);
	if (!master) {
		pr_err("Failed to find master dev\n");
		return NULL;
	}

	return master;
}

static void ste_dump(struct seq_file *m, struct device *dev, __le64 *ste)
{
	int i;

	seq_printf(m, "SMMUv3 STE values for device: %s\n", dev_name(dev));
	for (i = 0; i < STRTAB_STE_DWORDS; i++) {
		seq_printf(m, "0x%016llx\n", *ste);
		ste++;
	}
}

static int ste_show(struct seq_file *m, void *unused)
{
	struct arm_smmu_master *master;
	struct arm_smmu_device *smmu;
	struct device *dev;
	__le64 *ste;

	mutex_lock(&lock);

	dev = bus_find_device_by_name(&pci_bus_type, NULL, dump_pci_dev);
	if (!dev) {
		mutex_unlock(&lock);
		pr_err("Failed to find device\n");
		return -EINVAL;
	}

	master = arm_smmu_get_master(dev);
	if (!master) {
		put_device(dev);
		mutex_unlock(&lock);
		return -ENODEV;
	}
	smmu = master->smmu;

	/* currently only support one master one sid */
	ste = arm_smmu_get_step_for_sid(smmu, master->sids[0]);
	ste_dump(m, dev, ste);

	put_device(dev);
	mutex_unlock(&lock);

	return 0;
}
DEFINE_SHOW_ATTRIBUTE(ste);

static void cd_dump(struct seq_file *m, struct device *dev, __le64 *cd)
{
	int i;

	seq_printf(m, "SMMUv3 CD values for device: %s, ssid: 0x%x\n",
		   dev_name(dev), pasid);
	for (i = 0; i < CTXDESC_CD_DWORDS; i++) {
		seq_printf(m, "0x%016llx\n", *cd);
		cd++;
	}
}

static int cd_show(struct seq_file *m, void *unused)
{
	struct arm_smmu_master *master;
	struct arm_smmu_domain *domain;
	struct device *dev;
	__le64 *cd;
	int ret;

	mutex_lock(&lock);

	dev = bus_find_device_by_name(&pci_bus_type, NULL, dump_pci_dev);
	if (!dev) {
		mutex_unlock(&lock);
		pr_err("Failed to find device\n");
		return -EINVAL;
	}

	master = arm_smmu_get_master(dev);
	if (!master) {
		ret = -ENODEV;
		goto err_out;
	}
	domain = master->domain;

	cd = arm_smmu_get_cd_ptr(domain, pasid);
	if (!cd) {
		ret = -EINVAL;
		pr_err("Failed to find cd(ssid: %u)\n", pasid);
		goto err_out;
	}
	cd_dump(m, dev, cd);

	put_device(dev);
	mutex_unlock(&lock);

	return 0;

err_out:
	put_device(dev);
	mutex_unlock(&lock);
	return ret;
}
DEFINE_SHOW_ATTRIBUTE(cd);

static void __ptdump(arm_lpae_iopte *ptep, int lvl, u64 va,
		     struct arm_lpae_io_pgtable *data, struct seq_file *m)
{
	arm_lpae_iopte pte, *ptep_next;
	u64 i, tmp_va = 0;
	int entry_num;

	entry_num = 1 << (data->bits_per_level + ARM_LPAE_PGD_IDX(lvl, data));

	for (i = 0; i < entry_num; i++) {
		pte = READ_ONCE(*(ptep + i));
		if (!pte)
			continue;

		tmp_va = va | (i << ARM_LPAE_LVL_SHIFT(lvl, data));

		if (iopte_leaf(pte, lvl, data->iop.fmt)) {
			/* To do: print prot */
			seq_printf(m, "va: %llx -> pa: %llx\n", tmp_va,
				   iopte_to_paddr(pte, data));
			continue;
		}

		ptep_next = iopte_deref(pte, data);
		__ptdump(ptep_next, lvl + 1, tmp_va, data, m);
	}
}

static void ptdump(struct seq_file *m, struct arm_smmu_domain *domain,
		   void *pgd, int stage)
{
	struct arm_lpae_io_pgtable *data, data_sva;
	int levels, va_bits, bits_per_level;
	struct io_pgtable_ops *ops;
	arm_lpae_iopte *ptep = pgd;

	if (stage == 1 && !pasid) {
		ops = domain->pgtbl_ops;
		data = io_pgtable_ops_to_data(ops);
	} else {
		va_bits = VA_BITS - PAGE_SHIFT;
		bits_per_level = PAGE_SHIFT - ilog2(sizeof(arm_lpae_iopte));
		levels = DIV_ROUND_UP(va_bits, bits_per_level);

		data_sva.start_level = ARM_LPAE_MAX_LEVELS - levels;
		data_sva.pgd_bits = va_bits - (bits_per_level * (levels - 1));
		data_sva.bits_per_level = bits_per_level;
		data_sva.pgd = pgd;

		data = &data_sva;
	}

	__ptdump(ptep, data->start_level, 0, data, m);
}

static int pt_dump_s1_show(struct seq_file *m, void *unused)
{
	struct arm_smmu_master *master;
	struct arm_smmu_domain *domain;
	struct device *dev;
	__le64 *cd;
	void *pgd;
	u64 ttbr;
	int ret;

	mutex_lock(&lock);

	dev = bus_find_device_by_name(&pci_bus_type, NULL, dump_pci_dev);
	if (!dev) {
		mutex_unlock(&lock);
		pr_err("Failed to find device\n");
		return -EINVAL;
	}

	master = arm_smmu_get_master(dev);
	if (!master) {
		ret = -ENODEV;
		goto err_out;
	}
	domain = master->domain;

	cd = arm_smmu_get_cd_ptr(domain, pasid);
	if (!cd || !(le64_to_cpu(cd[0]) & CTXDESC_CD_0_V)) {
		ret = -EINVAL;
		pr_err("Failed to find valid cd(ssid: %u)\n", pasid);
		goto err_out;
	}

	/* CD0 and other CDx are all using ttbr0 */
	ttbr = le64_to_cpu(cd[1]) & CTXDESC_CD_1_TTB0_MASK;
	pgd = phys_to_virt(ttbr);

	if (ttbr) {
		seq_printf(m, "SMMUv3 dump page table for device %s, stage 1, ssid 0x%x:\n",
			   dev_name(dev), pasid);
		ptdump(m, domain, pgd, 1);
	}

	put_device(dev);
	mutex_unlock(&lock);

	return 0;

err_out:
	put_device(dev);
	mutex_unlock(&lock);
	return ret;
}
DEFINE_SHOW_ATTRIBUTE(pt_dump_s1);

static int pt_dump_s2_show(struct seq_file *m, void *unused)
{
	struct arm_smmu_master *master;
	struct arm_smmu_device *smmu;
	struct device *dev;
	__le64 *ste;
	u64 vttbr;
	void *pgd;
	int ret;

	mutex_lock(&lock);

	dev = bus_find_device_by_name(&pci_bus_type, NULL, dump_pci_dev);
	if (!dev) {
		mutex_unlock(&lock);
		pr_err("Failed to find device\n");
		return -EINVAL;
	}

	master = arm_smmu_get_master(dev);
	if (!master) {
		ret = -ENODEV;
		goto err_out;
	}
	smmu = master->smmu;

	/* currently only support one master one sid */
	ste = arm_smmu_get_step_for_sid(smmu, master->sids[0]);
	if (!(le64_to_cpu(ste[0]) & (1UL << 2))) {
		ret = -EINVAL;
		pr_err("Stage 2 translation is not valid\n");
		goto err_out;
	}

	vttbr = le64_to_cpu(ste[3]) & STRTAB_STE_3_S2TTB_MASK;
	pgd = phys_to_virt(vttbr);

	if (vttbr) {
		seq_printf(m, "SMMUv3 dump page table for device %s, stage 2:\n",
			   dev_name(dev));
		ptdump(m, 0, pgd, 2);
	}

	put_device(dev);
	mutex_unlock(&lock);

	return 0;

err_out:
	put_device(dev);
	mutex_unlock(&lock);
	return ret;
}
DEFINE_SHOW_ATTRIBUTE(pt_dump_s2);

void arm_smmu_debugfs_init(void)
{
	mutex_init(&lock);

	arm_smmu_debug = debugfs_create_dir("smmuv3", iommu_debugfs_dir);

	debugfs_create_file("pci_dev", 0644, arm_smmu_debug, NULL,
			    &master_pdev_fops);
	/*
	 * Problem here is we need to know dump which cd, currently my idea
	 * is we can get related pasid by smmu_bond_get trace point or by
	 * debug interface of master device specific driver, then here we
	 * use pasid to dump related cd.
	 *
	 * Or there is no need to dump page table about s1(pasid != 0) and s2
	 * as they can be got by /proc/<pid>/pagemap.
	 */
	debugfs_create_u32("pasid", 0644, arm_smmu_debug, &pasid);

	debugfs_create_file("ste", 0444, arm_smmu_debug, NULL, &ste_fops);

	debugfs_create_file("cd", 0444, arm_smmu_debug, NULL, &cd_fops);

	debugfs_create_file("pt_dump_s1", 0444, arm_smmu_debug, NULL,
			    &pt_dump_s1_fops);

	debugfs_create_file("pt_dump_s2", 0444, arm_smmu_debug, NULL,
			    &pt_dump_s2_fops);
}

void arm_smmu_debugfs_uninit(void)
{
	debugfs_remove_recursive(arm_smmu_debug);
	mutex_destroy(&lock);
}
