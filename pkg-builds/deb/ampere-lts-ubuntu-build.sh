#!/bin/bash

[ ! -d ampere-lts-kernel ] && git clone https://github.com/AmpereComputing/ampere-lts-kernel.git
cd ampere-lts-kernel

git clean -fd && git reset --hard HEAD && git checkout origin/linux-5.4.y
rm -rf debian
git am ../0001-base-packaging.patch || exit 1

# modify changelog
FILE_CHANGE_LOG=debian.master/changelog
source <(cat Makefile | head -4 | sed 's/ \= /\=/g')
echo "linux (${VERSION}.${PATCHLEVEL}.${SUBLEVEL}-amperelts) focal; urgency=low" > ${FILE_CHANGE_LOG}
echo >> ${FILE_CHANGE_LOG}
echo "  ampere-lts-kernel build at commit: $(git rev-parse HEAD)" >> ${FILE_CHANGE_LOG}
echo >> ${FILE_CHANGE_LOG}
echo " -- Bobo <lmw.bobo@gmail.com>  $(date -R)" >> ${FILE_CHANGE_LOG}

# adjust defconfig
sed -i 's/^defconfig.*=.*defconfig/defconfig = altra_5.4_defconfig/g' debian.master/rules.d/arm64.mk

# start building debs
LANG=C fakeroot debian/rules clean || exit 1
LANG=C fakeroot debian/rules binary || exit 1

# copy debs
rm -rf ../5.4_debs
mkdir -pv ../5.4_debs
mv ../*.deb ../*.udeb ../5.4_debs
echo "build ampere-lts 5.4 debs success"

git clean -fd && git reset --hard HEAD && git checkout origin/linux-5.10.y
rm -rf debian
git am ../0001-5.10-base-packaging.patch || exit 1

# modify changelog
FILE_CHANGE_LOG=debian.master/changelog
source <(cat Makefile | head -4 | sed 's/ \= /\=/g')
echo "linux (${VERSION}.${PATCHLEVEL}.${SUBLEVEL}-amperelts) focal; urgency=low" > ${FILE_CHANGE_LOG}
echo >> ${FILE_CHANGE_LOG}
echo "  ampere-lts-kernel build at commit: $(git rev-parse HEAD)" >> ${FILE_CHANGE_LOG}
echo >> ${FILE_CHANGE_LOG}
echo " -- Bobo <lmw.bobo@gmail.com>  $(date -R)" >> ${FILE_CHANGE_LOG}

# adjust defconfig
sed -i 's/^defconfig.*=.*defconfig/defconfig = altra_5.10_defconfig/g' debian.master/rules.d/arm64.mk

# start building debs
LANG=C fakeroot debian/rules clean || exit 1
LANG=C fakeroot debian/rules binary || exit 1

rm -rf ../5.10_debs
mkdir -pv ../5.10_debs
mv ../*.deb ../*.udeb ../5.10_debs
echo "build ampere-lts 5.10 debs success"

