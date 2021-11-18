// SPDX-License-Identifier: GPL-2.0
/* Ampere Altra SoC CPUECTLR_EL1 Config Driver
 *
 * Copyright (C) 2021 Ampere Computing LLC
 * Author: Hoan Tran <hoan@os.amperecomputing.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, see <http://www.gnu.org/licenses/>.
 *
 */

#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/bitmap.h>
#include <linux/bitfield.h>
#include <linux/device.h>
#include <linux/io.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/types.h>

#define CPU_CONFIG_SHARED_BUFFER		0x88990000
#define CPU_CONFIG_SHARED_BUFFER_SIZE		0x20
#define CPU_CONFIG_SIGNATURE_OFF		0x0
#define CPU_CONFIG_CPUECTLR_EL1_WEN_MASK_OFF	0x8
#define CPU_CONFIG_CPUECTLR_EL1_VALUE_OFF	0x10
#define CPU_CONFIG_SIGNATURE			0x43504D41

#define CPU_CONFIG_CPUECTLR_EL1_RPF_DIS_MASK	(ULL(0x1) << 5)
#define CPU_CONFIG_CPUECTLR_EL1_PF_STS_DIS_MASK	(ULL(0x1) << 7)
#define CPU_CONFIG_CPUECTLR_EL1_PF_STI_DIS_MASK	(ULL(0x1) << 8)
#define CPU_CONFIG_CPUECTLR_EL1_PF_DIS_MASK	(ULL(0x1) << 15)
#define CPU_CONFIG_CPUECTLR_EL1_PF_SS_L2_DIST_MASK	(ULL(0x3) << 12)
#define CPU_CONFIG_CPUECTLR_EL1_MASK \
	(CPU_CONFIG_CPUECTLR_EL1_RPF_DIS_MASK | \
	CPU_CONFIG_CPUECTLR_EL1_PF_STS_DIS_MASK | \
	CPU_CONFIG_CPUECTLR_EL1_PF_STI_DIS_MASK | \
	CPU_CONFIG_CPUECTLR_EL1_PF_SS_L2_DIST_MASK | \
	CPU_CONFIG_CPUECTLR_EL1_PF_DIS_MASK)

struct kobject *cpuectlr_el1_kobj;
static void __iomem *cpuectlr_el1_addr;

static u32 altra_config_read32(void __iomem *base, u32 reg)
{
	return readl_relaxed(base + reg);
}

static void altra_config_write32(void __iomem *base, u32 reg, u32 val)
{
	writel_relaxed(val, base + reg);
}

static u64 altra_config_read64(void __iomem *base, u32 reg)
{
	return readq_relaxed(base + reg);
}

static void altra_config_write64(void __iomem *base, u32 reg, u64 val)
{
	writeq_relaxed(val, base + reg);
}

static ssize_t signature_show(struct device *dev,
				 struct device_attribute *attr,
				 char *buf)
{
	return sprintf(buf, "0x%x\n",
		       altra_config_read32(cpuectlr_el1_addr, CPU_CONFIG_SIGNATURE_OFF));
}

static ssize_t cpuectlr_el1_wen_mask_show(struct device *dev,
				 struct device_attribute *attr,
				 char *buf)
{
	return sprintf(buf, "0x%llx\n",
		       altra_config_read64(cpuectlr_el1_addr, CPU_CONFIG_CPUECTLR_EL1_WEN_MASK_OFF));
}

static ssize_t cpuectlr_el1_wen_mask_store(struct device *device,
				struct device_attribute *attr,
				const char *buf,
				size_t count)
{
	ssize_t rc;
	long long val;

	rc = kstrtoll(buf, 0, &val);
	if (rc)
		return rc;
	altra_config_write64(cpuectlr_el1_addr, CPU_CONFIG_CPUECTLR_EL1_WEN_MASK_OFF,
			     val & CPU_CONFIG_CPUECTLR_EL1_MASK);

	return count;
}

static ssize_t cpuectlr_el1_value_show(struct device *dev,
				 struct device_attribute *attr,
				 char *buf)
{
	return sprintf(buf, "0x%llx\n",
		       altra_config_read64(cpuectlr_el1_addr, CPU_CONFIG_CPUECTLR_EL1_VALUE_OFF));
}

static ssize_t cpuectlr_el1_value_store(struct device *device,
				struct device_attribute *attr,
				const char *buf,
				size_t count)
{
	ssize_t rc;
	long long val;

	rc = kstrtoll(buf, 0, &val);
	if (rc)
		return rc;
	altra_config_write64(cpuectlr_el1_addr, CPU_CONFIG_CPUECTLR_EL1_VALUE_OFF, val);

	return count;
}

static DEVICE_ATTR_RO(signature);
static DEVICE_ATTR_RW(cpuectlr_el1_wen_mask);
static DEVICE_ATTR_RW(cpuectlr_el1_value);

static struct attribute *cpuectlr_el1_attrs[] = {
	&dev_attr_signature.attr,
	&dev_attr_cpuectlr_el1_wen_mask.attr,
	&dev_attr_cpuectlr_el1_value.attr,
	NULL,
};

static const struct attribute_group cpuectlr_el1_group = {
	.attrs = cpuectlr_el1_attrs,
};

static int __init altra_cpuectlr_init(void)
{
	int error;

	/* We register the efi directory at /sys/firmware/altra_cpuectlr */
	cpuectlr_el1_kobj = kobject_create_and_add("altra_cpuectlr", firmware_kobj);
	if (!cpuectlr_el1_kobj) {
		pr_err("Altra cpuectlr_el1: Firmware registration failed.\n");
		return -ENOMEM;
	}

	error = sysfs_create_group(cpuectlr_el1_kobj, &cpuectlr_el1_group);
	if (error) {
		pr_err("Altra cpuectlr_el1: Sysfs attribute export failed with error %d.\n",
		       error);
	}

	cpuectlr_el1_addr = (void __force *)ioremap(CPU_CONFIG_SHARED_BUFFER,
						    CPU_CONFIG_SHARED_BUFFER_SIZE);

	if (!cpuectlr_el1_addr) {
		pr_err("Altra cpuectlr_el1: Failed to ioremap cpu config region\n");
		error = -ENOMEM;
	}

	altra_config_write32(cpuectlr_el1_addr, CPU_CONFIG_SIGNATURE_OFF, CPU_CONFIG_SIGNATURE);

	return error;
}

static void __exit altra_cpuectlr_exit(void)
{
	sysfs_remove_group(cpuectlr_el1_kobj, &cpuectlr_el1_group);
	kobject_put(cpuectlr_el1_kobj);
	if (cpuectlr_el1_addr)
		iounmap(cpuectlr_el1_addr);
}

module_init(altra_cpuectlr_init);
module_exit(altra_cpuectlr_exit);

MODULE_DESCRIPTION("Altra SoC CPUECTLR_EL1 config");
MODULE_LICENSE("GPL v2");
