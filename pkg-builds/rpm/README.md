## How to build

	cd pkg-builds/rpm
	./ampere-lts-centos-build.sh

## How to install

	tar xvf amp_sw_centos_8.0-20210510-5.4.93.tar.xz
	cd aarch64
	yum -y localinstall kernel*

## How to activate new kernel

	grubby --set-default /boot/vmlinuz-5.4.93-amp_lts.el8.20210510+amp.aarch64

## How to upgrade kernel version

To upgrade kernel sublevel in 5.4 and 5.10. E.g. upgrading from v5.4.93 to v5.4.100, Change "rpmversion" in SPECS/kernel-ampere-lts-5.4.spec is enough.

To upgrade to a new PATCHLEVEL, you should copy a new spec file from the closest spec file. And change "rpmversion" and "kversion" in spec file. Besides this, the shebang patchfix list in spec file need to update as well.