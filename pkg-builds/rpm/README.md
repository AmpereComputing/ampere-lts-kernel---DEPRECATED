## How to build

	cd pkg-builds/rpm
	./ampere-lts-centos-build.sh

## How to install

	tar xvf amp_sw_centos_8.0-20210510-5.4.93.tar.xz
	cd aarch64
	yum -y localinstall kernel*

## How to activate new kernel

	grubby --set-default /boot/vmlinuz-5.4.93-amp_lts.el8.20210510+amp.aarch64

