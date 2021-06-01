#!/bin/sh

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
TMPDIR="/tmp/ampere_tests_tmp"

. lib/sh-test-lib

! check_root && echo "Should run as root" && exit 1

# clean last tmp dir
rm -rf ${TMPDIR}
mkdir -pv ${TMPDIR}

if [ ! -f /opt/kselftests/run_kselftest.sh ]; then
	rm -rf /opt/kselftests && mkdir -pv /opt/kselftests
	cd ${TMPDIR} && git clone --depth 1 https://github.com/AmpereComputing/ampere-lts-kernel.git -b linux-5.4.y
	cd ampere-lts-kernel
	# root don't have a .gitconfig
	git config user.email "local@local.com"
	git config user.name "local"
	git am ${SCRIPTPATH}/patches/0001-kselftests-add-skipfile-check-in-test-runner.patch
	cd tools/testing/selftests && ./kselftest_install.sh /opt/kselftests
	[ $? -ne 0 ] && echo "Install kselftests failed !!!" && exit 1
fi

if [ ! -f /opt/ltp/runltp ]; then
	# install dependencies first
	apt-get install -y keyutils exfat-utils exfat-fuse quota kexec-tools dump wireguard-tools inetutils-traceroute isc-dhcp-server nftables expect xinetd libaio1 libaio-dev libmnl0 libmnl-dev
	rm -rf /opt/ltp
	cd ${TMPDIR} && git clone --depth 1 https://github.com/linux-test-project/ltp.git
	cd ltp
	make autotools && ./configure --prefix=/opt/ltp --with-linux-dir=/lib/modules/`uname -r`/build && make -j && make install
	[ $? -ne 0 ] && echo "Install ltp failed !!!" && exit 1
fi

cd ${SCRIPTPATH}/lkft/kselftest
./kselftest.sh -p /opt/kselftests -g 5.4 -S skipfile-lkft.yaml -s true
echo "Test lkft/kselftest finished, please check lkft/kselftest/output/result.csv"

cd ${SCRIPTPATH}/lkft/ltp
./ltp.sh -S skipfile-lkft.yaml -g 5.4 -s true -i /opt/ltp -d ltptmp
echo "Test lkft/ltp finished, please check lkft/ltp/output/result.csv"

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

