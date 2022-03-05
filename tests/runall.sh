#!/bin/sh

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
TMPDIR="/tmp/ampere_tests_tmp"

. lib/sh-test-lib

! check_root && echo "Should run as root" && exit 1

# clean last tmp dir
rm -rf ${TMPDIR}
mkdir -pv ${TMPDIR}

kversion=$(uname -r | awk -F . '{print $1 "." $2}')

amp_functions_test() {
	echo "=============================="
	echo " Start ampere function tests"
	echo "=============================="

	cd ${SCRIPTPATH}/ampere_functions/hw_monitor
	./altra_hw_monitor.sh
	cd ${SCRIPTPATH}/ampere_functions/leds
	./altra_leds.sh
	cd ${SCRIPTPATH}/ampere_functions/pmu
	./altra_pmu.sh
	cd ${SCRIPTPATH}/ampere_functions/numa
	./numa.sh
	cd ${SCRIPTPATH}/ampere_functions/smmu_filter_fix
	./smmu_filter_fix.sh
	cd ${SCRIPTPATH}/ampere_functions/perf_kvm_stat
	./perf_kvm_stat.sh
	cd ${SCRIPTPATH}/ampere_functions/ras
	./ras.sh
	cd ${SCRIPTPATH}/ampere_functions/cpuectlr_el1
	./altra_cpuectlr_el1.sh
	cd ${SCRIPTPATH}/ampere_functions/exec
	./exec.sh
}

install_ltp_deps() {
	dist_name
	case "${dist}" in
		debian|ubuntu)
			apt-get install -y keyutils exfat-utils exfat-fuse quota kexec-tools dump wireguard-tools inetutils-traceroute isc-dhcp-server nftables expect xinetd libaio1 libaio-dev libmnl0 libmnl-dev
			;;
		centos)
			yum install -y clang llvm libmount libmount-devel libaio libaio-devel libtirpc libtirpc-devel iproute-tc psmisc exfatprogs ntfsprogs btrfs-progs wireguard-tools keyutils dump sysstat traceroute nfs-utils bind dhcp-server telnet dnsmasq fuse expect kexec-tools nftables xinetd libmnl libmnl-devel quotatool quota quota-devel xfsprogs xfsprogs-devel libattr libattr-devel libacl libacl-devel lksctp-tools lksctp-tools-devel perl-JSON perl-libwww-perl libhugetlbfs libhugetlbfs-devel telnet-server
			rpm -q btrfs-progs || rpm -i http://mirror.centos.org/altarch/7/os/aarch64/Packages/btrfs-progs-4.9.1-1.el7.aarch64.rpm
			ps aux | grep "[r]pc.mountd" || systemctl enable nfs-server.service && systemctl start nfs-server.service
			;;
		*)
			echo "Unsupported distro: ${dist}!"
			;;
	esac
}

run_kselftest() {
	if [ ! -f /opt/kselftests/version_${kversion} ]; then
		apt-get install libhugetlbfs-dev jq ipvsadm conntrack netsniff-ng tshark smcroute libteam-utils -y
		rm -rf /opt/kselftests && mkdir -pv /opt/kselftests
		cd ${TMPDIR} && git clone --depth 1 https://github.com/AmpereComputing/ampere-lts-kernel.git -b linux-${kversion}.y || exit 1
		cd ampere-lts-kernel
		# root don't have a .gitconfig
		git config user.email "local@local.com"
		git config user.name "local"
		git am ${SCRIPTPATH}/patches/0001-kselftests-add-skipfile-check-in-test-runner.patch
		cd tools/testing/selftests && ./kselftest_install.sh /opt/kselftests && touch /opt/kselftests/version_${kversion}
		[ $? -ne 0 ] && echo "Install kselftests failed !!!" && exit 1
		cp -f /opt/kselftests/net/forwarding/forwarding.config.sample /opt/kselftests/net/forwarding/forwarding.config
	fi

	cd ${SCRIPTPATH}/lkft/kselftest
	./kselftest.sh -p /opt/kselftests -g ${kversion} -S skipfile-lkft.yaml -s true
	echo "Test lkft/kselftest finished, please check lkft/kselftest/output/result.csv"
}

run_ltp() {
	if [ ! -f /opt/ltp/version_${kversion} ]; then
		install_ltp_deps
		rm -rf /opt/ltp
		cd ${TMPDIR} && git clone --depth 1 https://github.com/linux-test-project/ltp.git -b 20210524 || exit 1
		cd ltp
		# To fix broken aiodio tests, see https://patchwork.ozlabs.org/project/ltp/patch/20210601155427.996321-1-zlang@redhat.com/
		git apply ${SCRIPTPATH}/patches/ltp-aiodio-help-aiodio-test-work-normally.diff || exit 1
		make autotools && ./configure --prefix=/opt/ltp --with-linux-dir=/lib/modules/`uname -r`/build && make -j && make install && touch /opt/ltp/version_${kversion}
		[ $? -ne 0 ] && echo "Install ltp failed !!!" && exit 1
	fi

	cd ${SCRIPTPATH}/lkft/ltp
	./ltp.sh -S skipfile-lkft.yaml -g ${kversion} -s true -i /opt/ltp -d `pwd`/ltptmp
	echo "Test lkft/ltp finished, please check lkft/ltp/output/result.csv"
}

amp_functions_test
run_kselftest
run_ltp
