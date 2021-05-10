# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a kernel released for public testing, released_kernel should be 1.
# For internal testing builds during development, it should be 0.
%global released_kernel 1

%global distro_build amp_lts

# Sign the x86_64 kernel for secure boot authentication
%ifarch x86_64
%global signkernel 1
%else
%global signkernel 0
%endif

# Sign modules on all arches
%global signmodules 0

# Compress modules only for architectures that build modules
%ifarch noarch
%global zipmodules 0
%else
%global zipmodules 1
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
%endif

# define buildid .local

%define rpmversion 5.4.93
%define pkgrelease amp_lts

# allow pkg_release to have configurable %%{?dist} tag
%define specrelease amp_lts%{?dist}

%define pkg_release %{specrelease}%{?buildid}

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

%define _with_kabidupchk 1
# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
%define with_cross_headers   %{?_without_cross_headers:   0} %{?!_without_cross_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# bpf tool
%define with_bpftool   %{?_without_bpftool:   0} %{?!_without_bpftool:   1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# kernel-zfcpdump (s390 specific kernel for zfcpdump)
%define with_zfcpdump  %{?_without_zfcpdump:  0} %{?!_without_zfcpdump:  1}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_without_kernel_abi_whitelists: 0} %{?!_without_kernel_abi_whitelists: 1}
#
# Optional packages
#
%define with_bpf_samples %{?_with_bpf_samples: 1} %{?!_with_bpf_samples: 0}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}
# Control whether we perform a compat. check against DUP ABI.
%define with_kabidupchk %{?_with_kabidupchk:  1} %{?!_with_kabidupchk:   0}
#
# Control whether to run an extensive DWARF based kABI check.
# Note that this option needs to have baseline setup in SOURCE300.
%define with_kabidwchk %{?_without_kabidwchk: 0} %{?!_without_kabidwchk: 1}
%define with_kabidw_base %{?_with_kabidw_base: 1} %{?!_with_kabidw_base: 0}
#
# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}
#
# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}
#
# build a release kernel on rawhide
%define with_release   %{?_with_release:      1} %{?!_with_release:      0}

# The kernel tarball/base version
%define kversion 5.4

%define with_gcov %{?_with_gcov: 1} %{?!_with_gcov: 0}

# turn off debug kernel and kabichk for gcov builds
%if %{with_gcov}
%define with_debug 0
%define with_kabichk 0
%define with_kabidupchk 0
%define with_kabidwchk 0
%endif

# turn off kABI DWARF-based check if we're generating the base dataset
%if %{with_kabidw_base}
%define with_kabidwchk 0
%endif

%define make_target bzImage
%define image_install_path boot

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define KVERREL_RE %(echo %KVERREL | sed 's/+/[+]/g')
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug
# Needed because we override almost everything involving build-ids
# and debuginfo generation. Currently we rely on the old alldebug setting.
%global _build_id_links alldebug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_up 0
%define with_tools 0
%define with_perf 0
%define with_bpftool 0
%endif

# turn off kABI DUP check and DWARF-based check if kABI check is disabled
%if !%{with_kabichk}
%define with_kabidupchk 0
%define with_kabidwchk 0
%endif

%ifnarch noarch
%define with_kernel_abi_whitelists 0
%endif

# Overrides for generic default options

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define doc_build_fail true
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_cross_headers 0
%define with_tools 0
%define with_perf 0
%define with_bpftool 0
%define with_bpf_samples 0
%define with_debug 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# sparse blows up on ppc
%ifnarch ppc64le
%define with_sparse 0
%endif

# zfcpdump mechanism is s390 only
%ifnarch s390x
%define with_zfcpdump 0
%endif

# Per-arch tweaks

%ifarch i686
%define asmarch x86
%define hdrarch i386
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define all_arch_configs kernel-%{version}-ppc64le*.config
%define kcflags -O3
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define kernel_image arch/s390/boot/bzImage
%endif

%ifarch aarch64
%define all_arch_configs kernel-%{version}-aarch64-altra*.config
%define asmarch arm64
%define hdrarch arm64
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386 i686

%ifarch %nobuildarches
%define with_up 0
%define with_debug 0
%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_bpf_samples 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs x86_64 ppc64le aarch64


#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  coreutils, systemd >= 203-2, /usr/bin/kernel-install
%define initrd_prereq  dracut >= 027


Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2 and Redistributable, no modification permitted
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch i386 i686 x86_64 s390x aarch64 ppc64le
ExclusiveOS: Linux
%ifnarch %{nobuildarches}
Requires: kernel-core-uname-r = %{KVERREL}%{?variant}
Requires: kernel-modules-uname-r = %{KVERREL}%{?variant}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, sh-utils, tar, git
BuildRequires: bzip2, xz, findutils, gzip, m4, perl-interpreter, perl-Carp, perl-devel, perl-generators, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc, python3-devel
BuildRequires: net-tools, hostname, bc, bison, flex, elfutils-devel
%if %{with_doc}
BuildRequires: xmlto, asciidoc, python3-sphinx
%endif
%if %{with_sparse}
BuildRequires: sparse
%endif
%if %{with_perf}
BuildRequires: zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison flex xz-devel
BuildRequires: audit-libs-devel
BuildRequires: java-devel
%ifnarch s390x
BuildRequires: numactl-devel
%endif
%endif
%if %{with_tools}
BuildRequires: gettext ncurses-devel
%ifnarch s390x
BuildRequires: pciutils-devel
%endif
%endif
%if %{with_bpftool}
BuildRequires: python3-docutils
BuildRequires: zlib-devel binutils-devel
%endif
%if %{with_bpf_samples}
BuildRequires: libcap-devel libcap-ng-devel glibc-static rsync llvm-toolset
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
BuildConflicts: rpm < 4.13.0.1-19
# Most of these should be enabled after more investigation
%undefine _include_minidebuginfo
%undefine _find_debuginfo_dwz_opts
%undefine _unique_build_ids
%undefine _unique_debug_names
%undefine _unique_debug_srcs
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%undefine _include_gdb_index
%global _find_debuginfo_opts -r
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%endif
%if %{with_kabidwchk} || %{with_kabidw_base}
BuildRequires: kabi-dw
%endif

%if %{signkernel}%{signmodules}
BuildRequires: openssl openssl-devel
%if %{signkernel}
BuildRequires: nss-tools
BuildRequires: pesign >= 0.10-4
%endif
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%endif

# These below are required to build man pages
%if %{with_perf}
BuildRequires: xmlto
%endif
%if %{with_perf} || %{with_tools}
BuildRequires: asciidoc
%endif

Source0: linux-%{rpmversion}-%{pkgrelease}.tar.xz

Source11: x509.genkey
%if %{?released_kernel}
Source13: securebootca.cer
Source14: secureboot.cer
%define pesign_name redhatsecureboot301
%else
Source13: redhatsecurebootca2.cer
Source14: redhatsecureboot003.cer
%define pesign_name redhatsecureboot003
%endif
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-sign.sh
Source19: mod-extra-blacklist.sh
Source90: filter-x86_64.sh
Source93: filter-aarch64.sh
Source96: filter-ppc64le.sh
Source97: filter-s390x.sh
Source99: filter-modules.sh
%define modsign_cmd %{SOURCE18}

Source20: kernel-aarch64.config
Source21: kernel-aarch64-debug.config
# Source22: kernel-aarch64-emag.config
Source32: kernel-ppc64le.config
Source33: kernel-ppc64le-debug.config
Source36: kernel-s390x.config
Source37: kernel-s390x-debug.config
Source38: kernel-s390x-zfcpdump.config
Source39: kernel-x86_64.config
Source40: kernel-x86_64-debug.config
Source41: generate_all_configs.sh

Source42: process_configs.sh
Source43: generate_bls_conf.sh

Source200: check-kabi

Source201: Module.kabi_aarch64
Source202: Module.kabi_ppc64le
Source203: Module.kabi_s390x
Source204: Module.kabi_x86_64

Source210: Module.kabi_dup_aarch64
Source211: Module.kabi_dup_ppc64le
Source212: Module.kabi_dup_s390x
Source213: Module.kabi_dup_x86_64

Source300: kernel-abi-whitelists-%{rpmversion}-%{distro_build}.tar.bz2
Source301: kernel-kabi-dw-%{rpmversion}-%{distro_build}.tar.bz2

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

## Patches needed for building this package

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

# END OF PATCH DEFINITIONS

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

%description
The kernel meta package

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:+%{1}}\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20150904-56.git6ebf5d57\
Requires(preun): systemd >= 200\
Conflicts: xfsprogs < 4.3.0-1\
Conflicts: xorg-x11-drv-vmmouse < 13.0.99\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%if "0%{?variant}"
Obsoletes: kernel-headers < %{rpmversion}-%{pkg_release}
Provides: kernel-headers = %{rpmversion}-%{pkg_release}
%endif
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc
Group: Development/System
%description cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.


%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
Provides: installonlypkg(kernel)
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|.*%%{_libdir}/traceevent/plugins/.*|.*%%{_libdir}/libperf-jvmti.so(\.debug)?|XXX' -o perf-debuginfo.list}

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python3-perf
The python3-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%package -n python3-perf-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python3-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{python3_sitearch}/perf.*so(\.debug)?|XXX' -o python3-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%endif
%define __requires_exclude ^%{_bindir}/python
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
Group: Development/System
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
%endif
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|.*%%{_bindir}/lsgpio(\.debug)?|.*%%{_bindir}/gpio-hammer(\.debug)?|.*%%{_bindir}/gpio-event-mon(\.debug)?|.*%%{_bindir}/iio_event_monitor(\.debug)?|.*%%{_bindir}/iio_generic_buffer(\.debug)?|.*%%{_bindir}/lsiio(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

%endif # with_tools

%if %{with_bpftool}

%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps
License: GPLv2
%description -n bpftool
This package contains the bpftool, which allows inspection and simple
manipulation of eBPF programs and maps.

%package -n bpftool-debuginfo
Summary: Debug information for package bpftool
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n bpftool-debuginfo
This package provides debug information for the bpftool package.

%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%%{_sbindir}/bpftool(\.debug)?|XXX' -o bpftool-debuginfo.list}

%endif # with_bpftool

%if %{with_bpf_samples}

%package -n bpf-samples
Summary: eBPF samples and selftests
License: GPLv2
%description -n bpf-samples
eBPF sample programs and selftests.

%endif # with_bpf_samples

%if %{with_gcov}
%package gcov
Summary: gcov graph and source files for coverage data collection.
Group: Development/System
%description gcov
kernel-gcov includes the gcov graph and source files for gcov coverage collection.
%endif

%package -n kernel-abi-whitelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol whitelists
Group: System Environment/Kernel
AutoReqProv: no
%description -n kernel-abi-whitelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

%if %{with_kabidw_base}
%package kabidw-base
Summary: The baseline dataset for kABI verification using DWARF data
Group: System Environment/Kernel
AutoReqProv: no
%description kabidw-base
The kabidw-base package contains data describing the current ABI of the Red Hat
Enterprise Linux kernel, suitable for the kabi-dw tool.
%endif

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
%description %{?1:%{1}-}debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '/.*/%%{KVERREL_RE}%{?1:[+]%{1}}/.*|/.*%%{KVERREL_RE}%{?1:\+%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl-interpreter\
%description %{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-extra package.
#	%%kernel_modules_extra_package <subpackage> <pretty-name>
#
%define kernel_modules_extra_package() \
%package %{?1:%{1}-}modules-extra\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules package.
#	%%kernel_modules_package <subpackage> <pretty-name>
#
%define kernel_modules_package() \
%package %{?1:%{1}-}modules\
Summary: kernel modules to match the %{?2:%{2}-}core kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules\
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.\
%{nil}

#
# this macro creates a kernel-<subpackage> meta package.
#	%%kernel_meta_package <subpackage>
#
%define kernel_meta_package() \
%package %{1}\
summary: kernel meta-package for the %{1} kernel\
group: system environment/kernel\
Requires: kernel-%{1}-core-uname-r = %{KVERREL}%{?variant}+%{1}\
Requires: kernel-%{1}-modules-uname-r = %{KVERREL}%{?variant}+%{1}\
Provides: installonlypkg(kernel)\
%description %{1}\
The meta-package for the %{1} kernel\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%{nil}

# Now, each variant package.

%if %{with_zfcpdump}
%define variant_summary The Linux kernel compiled for zfcpdump usage
%kernel_variant_package zfcpdump
%description zfcpdump-core
The kernel package contains the Linux kernel (vmlinuz) for use by the
zfcpdump infrastructure.
%endif # with_zfcpdump

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug-core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

# And finally the main -core package

%define variant_summary The Linux kernel
%kernel_variant_package
%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-4." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz)  gunzip  < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.xz)  unxz    < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

%setup -q -n kernel-%{rpmversion}-%{pkgrelease} -c
mv linux-%{rpmversion}-%{pkgrelease} linux-%{KVERREL}

cd linux-%{KVERREL}

ApplyOptionalPatch linux-kernel-test.patch

# END OF PATCH APPLICATIONS

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl
mv COPYING COPYING-%{version}

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# Do not use "ambiguous" python shebangs. RHEL 8 now has a new script
# (/usr/lib/rpm/redhat/brp-mangle-shebangs), which forces us to specify a
# "non-ambiguous" python shebang for scripts we ship in buildroot. This
# script throws an error like below:
# *** ERROR: ambiguous python shebang in /usr/bin/kvm_stat: #!/usr/bin/python. Change it to python3 (or python2) explicitly.
# We patch all sources below for which we got a report/error.
pathfix.py -i %{__python3} -p -n \
	tools/kvm/kvm_stat/kvm_stat \
	scripts/show_delta \
	scripts/diffconfig \
	scripts/bloat-o-meter \
	scripts/gen_compile_commands.py \
	tools/perf/tests/attr.py \
	tools/perf/scripts/python/stat-cpi.py \
	tools/perf/scripts/python/sched-migration.py \
	Documentation

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
fi
mkdir configs
cd configs

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-aarch64-altra*.config .
cp %{SOURCE41} .
VERSION=%{version} ./generate_all_configs.sh

# Note we need to disable these flags for cross builds because the flags
# from redhat-rpm-config assume that host == target so target arch
# flags cause issues with the host compiler.
%if !%{with_cross}
%define build_hostcflags  ${RPM_OPT_FLAGS}
%define build_hostldflags %{__global_ldflags}
%endif

%define make make %{?cross_opts} HOSTCFLAGS="%{?build_hostcflags}" HOSTLDFLAGS="%{?build_hostldflags}"

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
%endif

cp %{SOURCE42} .
./process_configs.sh -w -c kernel %{rpmversion}

# end of kernel config
%endif

cd ..
# # End of Configs stuff

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$4
    DoVDSO=$3
    Flav=${Flavour:++${Flavour}}
    InstallName=${5:-vmlinuz}

    DoModules=1
    if [ "$Flavour" = "zfcpdump" ]; then
	    DoModules=0
    fi

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}-altra.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flav}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flav}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flav}/" Makefile

    # and now to start the build process

    %{make} -s mrproper
    cp configs/$Config .config

    %if %{signkernel}%{signmodules}
    cp %{SOURCE11} certs/.
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    %{make} -s ARCH=$Arch olddefconfig >/dev/null
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    if [ $DoModules -eq 1 ]; then
	%{make} -s ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" modules %{?sparse_mflags} || exit 1
    fi

    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif

%ifarch aarch64
    %{make} -s ARCH=$Arch V=1 dtbs dtbs_install INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    cp -r $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/dtb
    find arch/$Arch/boot/dts -name '*.dtb' -type f | xargs rm -f
%endif

    # Start installing the results
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/config
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/System.map

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/lib/modules/$KernelVer/zImage.stub-$KernelVer || :
    fi
    %if %{signkernel}
    # Sign the image if we're using EFI
    # aarch64 kernels are gziped EFI images
    KernelExtension=${KernelImage##*.}
    if [ "$KernelExtension" == "gz" ]; then
        SignImage=${KernelImage%.*}
    else
        SignImage=$KernelImage
    fi
    %pesign -s -i $SignImage -o vmlinuz.signed -a %{SOURCE13} -c %{SOURCE14} -n %{pesign_name}
    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $SignImage
    if [ "$KernelExtension" == "gz" ]; then
        gzip -f9 $SignImage
    fi
    %endif
    $CopyKernel $KernelImage \
                $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    cp $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/$InstallName

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;
    cp $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac $RPM_BUILD_ROOT/lib/modules/$KernelVer/.vmlinuz.hmac

    if [ $DoModules -eq 1 ]; then
	# Override $(mod-fw) because we don't want it to install any firmware
	# we'll get it from the linux-firmware package and we don't want conflicts
	%{make} -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
    fi

%if %{with_gcov}
    # install gcov-needed files to $BUILDROOT/$BUILD/...:
    #   gcov_info->filename is absolute path
    #   gcno references to sources can use absolute paths (e.g. in out-of-tree builds)
    #   sysfs symlink targets (set up at compile time) use absolute paths to BUILD dir
    find . \( -name '*.gcno' -o -name '*.[chS]' \) -exec install -D '{}' "$RPM_BUILD_ROOT/$(pwd)/{}" \;
%endif

    if [ $DoVDSO -ne 0 ]; then
        %{make} -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
        if [ ! -s ldconfig-kernel.conf ]; then
          echo > ldconfig-kernel.conf "\
    # Placeholder file, no vDSO hwcap entries used in this kernel."
        fi
        %{__install} -D -m 444 ldconfig-kernel.conf \
            $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
        rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
    fi

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    cp $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz $RPM_BUILD_ROOT/lib/modules/$KernelVer/symvers.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidupchk}
    echo "**** kABI DUP checking is enabled in kernel SPEC file. ****"
    if [ -e $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_dup_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find DUP reference Module.kabi file. ****"
    fi
%endif

%if %{with_kabidw_base}
    # Don't build kabi base for debug kernels
    if [ "$Flavour" != "kdump" -a "$Flavour" != "debug" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf

        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/whitelists
        tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/whitelists

        echo "**** GENERATING DWARF-based kABI baseline dataset ****"
        chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
        $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
            "$RPM_BUILD_ROOT/kabi-dwarf/whitelists/kabi-current/kabi_whitelist_%{_target_cpu}" \
            "$(pwd)" \
            "$RPM_BUILD_ROOT/kabidw-base/%{_target_cpu}${Flavour:+.${Flavour}}" || :

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

%if %{with_kabidwchk}
    if [ "$Flavour" != "kdump" ]; then
        mkdir -p $RPM_BUILD_ROOT/kabi-dwarf
        tar xjvf %{SOURCE301} -C $RPM_BUILD_ROOT/kabi-dwarf
        if [ -d "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}" ]; then
            mkdir -p $RPM_BUILD_ROOT/kabi-dwarf/whitelists
            tar xjvf %{SOURCE300} -C $RPM_BUILD_ROOT/kabi-dwarf/whitelists

            echo "**** GENERATING DWARF-based kABI dataset ****"
            chmod 0755 $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh generate \
                "$RPM_BUILD_ROOT/kabi-dwarf/whitelists/kabi-current/kabi_whitelist_%{_target_cpu}" \
                "$(pwd)" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}.tmp" || :

            echo "**** kABI DWARF-based comparison report ****"
            $RPM_BUILD_ROOT/kabi-dwarf/run_kabi-dw.sh compare \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}" \
                "$RPM_BUILD_ROOT/kabi-dwarf/base/%{_target_cpu}${Flavour:+.${Flavour}}.tmp" || :
            echo "**** End of kABI DWARF-based comparison report ****"
        else
            echo "**** Baseline dataset for kABI DWARF-BASED comparison report not found ****"
        fi

        rm -rf $RPM_BUILD_ROOT/kabi-dwarf
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/tracing
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/spdxcheck.py
    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    if [ -f arch/%{asmarch}/kernel/module.lds ]; then
      cp -a --parents arch/%{asmarch}/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc64le
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # arch/arm64/include/asm/xen references arch/arm
    cp -a --parents arch/arm/include/asm/xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    # arch/arm64/include/asm/opcodes.h references arch/arm
    cp -a --parents arch/arm/include/asm/opcodes.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
%ifarch x86_64
    # files for 'make prepare' to succeed with kernel-devel
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscalltbl.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscallhdr.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_32.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_64.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_common.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents tools/include/tools/le_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/setup-x86_64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/entry64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/ctype.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    eu-readelf -n vmlinux | grep "Build ID" | awk '{print $NF}' > vmlinux.id
    cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
        LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking \
      'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
      'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm \
      'drm_open|drm_init'
    collect_modules_list modesetting \
      'drm_crtc_init'

    # detect missing or incorrect license tags
    ( find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' | xargs /sbin/modinfo -l | \
        grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1

    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # Call the modules-extra script to move things around.  Note cleanup below.
    %{SOURCE17} $RPM_BUILD_ROOT /lib/modules/$KernelVer %{SOURCE16}
    # Blacklist net autoloadable modules in modules-extra
    %{SOURCE19} $RPM_BUILD_ROOT/modules-extra.list
    cat $RPM_BUILD_ROOT/modules-extra.list | xargs rm -f

    # If we're signing modules, we can't leave the .mod files for the .ko files
    # we've moved in .tmp_versions/.  Remove them so the Kbuild 'modules_sign'
    # target doesn't try to sign a non-existent file.  This is kinda ugly, but
    # so is modules-extra.
    popd
    for mod in `cat $RPM_BUILD_ROOT/modules-extra.list`
	do
	  modfile=`basename $mod | sed -e 's/.ko/.mod/'`
	  [ -f "$modfile" ] && rm .tmp_versions/$modfile
	done
    pushd $RPM_BUILD_ROOT

    if [ $DoModules -eq 1 ]; then
	# Find all the module files and filter them out into the core and
	# modules lists.  This actually removes anything going into -modules
	# from the dir.
	find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
	cp $RPM_SOURCE_DIR/filter-*.sh .
	%{SOURCE99} modules.list %{_target_cpu}
	rm filter-*.sh

	# Run depmod on the resulting module tree and make sure it isn't broken
	depmod -b . -aeF ./System.map $KernelVer &> depmod.out
	if [ -s depmod.out ]; then
	    echo "Depmod failure"
	    cat depmod.out
	    exit 1
	else
	    rm depmod.out
	fi
    else
	# Ensure important files/directories exist to let the packaging succeed
	echo '%%defattr(-,-,-)' > modules.list
	echo '%%defattr(-,-,-)' > k-d.list
	# This overwrites anything created by %{SOURCE19}
	echo '%%defattr(-,-,-)' > modules-extra.list
	mkdir -p lib/modules/$KernelVer/kernel
	# Add files usually created by make modules, needed to prevent errors
	# thrown by depmod during package installation
	touch lib/modules/$KernelVer/modules.order
	touch lib/modules/$KernelVer/modules.builtin
    fi

    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    # Go back and find all of the various directories in the tree.  We use this
    # for the dir lists in kernel-core
    find lib/modules/$KernelVer/kernel -mindepth 1 -type d | sort -n > module-dirs.list

    # Cleanup
    rm System.map
    cp -r restore/* lib/modules/$KernelVer/.
    rm -rf restore
    popd

    # Make sure the files lists start with absolute paths or rpmbuild fails.
    # Also add in the dir entries
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../kernel${Flavour:+-${Flavour}}-modules.list
    sed -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../kernel${Flavour:+-${Flavour}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../kernel${Flavour:+-${Flavour}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules-extra.list >> ../kernel${Flavour:+-${Flavour}}-modules-extra.list

    # Cleanup
    rm -f $RPM_BUILD_ROOT/k-d.list
    rm -f $RPM_BUILD_ROOT/modules.list
    rm -f $RPM_BUILD_ROOT/module-dirs.list
    # Cleanup file created by %{SOURCE17}
    rm -f $RPM_BUILD_ROOT/modules-extra.list

%if %{signmodules}
    if [ $DoModules -eq 1 ]; then
	# Save the signing keys so we can sign the modules in __modsign_install_post
	cp certs/signing_key.pem certs/signing_key.pem.sign${Flav}
	cp certs/signing_key.x509 certs/signing_key.x509.sign${Flav}
    fi
%endif

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir

    # This is going to create a broken link during the build, but we don't use
    # it after this point.  We need the link to actually point to something
    # when kernel-devel is installed, and a relative link doesn't work across
    # the F17 UsrMove feature.
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;

    # build a BLS config for this kernel
    %{SOURCE43} "$KernelVer" "$RPM_BUILD_ROOT" "%{?variant}"

    # Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer
    install -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/$KernelVer/kernel-signing-ca.cer

}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVERREL}


%if %{with_debug}
BuildKernel %make_target %kernel_image %{with_vdso_install} debug
%endif

%if %{with_zfcpdump}
BuildKernel %make_target %kernel_image %{with_vdso_install} zfcpdump
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image %{with_vdso_install}
%endif

%global perf_make \
  make EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?cross_opts} -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 prefix=%{_prefix} PYTHON=%{__python3}
%if %{with_perf}
# perf
# make sure check-headers.sh is executable
chmod +x tools/perf/check-headers.sh
%{perf_make} DESTDIR=$RPM_BUILD_ROOT all
%endif

%global tools_make \
  %{make} CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" V=1

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%{tools_make} -C tools/power/cpupower CPUFREQ_BENCH=false DEBUG=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{tools_make} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   %{make}
   popd
   pushd tools/power/x86/turbostat
   %{make}
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools/thermal/tmon/
%{make}
popd
pushd tools/iio/
%{make}
popd
pushd tools/gpio/
%{make}
popd
%endif

%global bpftool_make \
  make EXTRA_CFLAGS="${RPM_OPT_FLAGS}" EXTRA_LDFLAGS="%{__global_ldflags}" DESTDIR=$RPM_BUILD_ROOT V=1
%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make}
popd
%endif

%if %{with_bpf_samples}
# Unfortunately, samples/bpf/Makefile expects that the headers are installed
# in the source tree. We installed them previously to $RPM_BUILD_ROOT/usr
# but there's no way to tell the Makefile to take them from there.
make headers_install
%{make} -s ARCH=$Arch V=1 samples/bpf/
pushd tools/testing/selftests
# We need to install here because we need to call make with ARCH set which
# doesn't seem possible to do in the install section.
%{make} -s ARCH=$Arch V=1 TARGETS=bpf INSTALL_PATH=%{buildroot}%{_libexecdir}/bpf-samples/selftests install
popd
%endif

%if %{with_doc}
# Make the HTML pages.
make htmldocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Don't sign modules for the zfcpdump flavour as it is monolithic.

%define __modsign_install_post \
  if [ "%{signmodules}" -eq "1" ]; then \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+debug certs/signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign certs/signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
    fi \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs xz; \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif

%endif

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}

# copy the source over
mkdir -p $docdir
tar -h -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_cross_headers}
mkdir -p $RPM_BUILD_ROOT/usr/tmp-headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr/tmp-headers headers_install

find $RPM_BUILD_ROOT/usr/tmp-headers/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

# Copy all the architectures we care about to their respective asm directories
# for arch in arm64 powerpc s390 x86 ; do
# mkdir -p $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include
# mv $RPM_BUILD_ROOT/usr/tmp-headers/include/arch-${arch}/asm $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/
# cp -a $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-generic $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/.
# done

# Remove the rest of the architectures
# rm -rf $RPM_BUILD_ROOT/usr/tmp-headers/include/arch*
# rm -rf $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-*

mkdir -p $RPM_BUILD_ROOT/usr/arm64-linux-gnu/include
cp -a $RPM_BUILD_ROOT/usr/tmp-headers/include/* $RPM_BUILD_ROOT/usr/arm64-linux-gnu/include/.

rm -rf $RPM_BUILD_ROOT/usr/tmp-headers
%endif

%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE300} -C $INSTALL_KABI_PATH
%endif  # with_kernel_abi_whitelists

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-bin install-traceevent-plugins
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace
# remove the perf-tips
rm -rf %{buildroot}%{_docdir}/perf-tip

# For both of the below, yes, this should be using a macro but right now
# it's hard coded and we don't actually want it anyway right now.
# Whoever wants examples can fix it up!

# remove examples
rm -rf %{buildroot}/usr/lib/examples/perf
# remove the stray header file that somehow got packaged in examples
rm -rf %{buildroot}/usr/lib/include/perf/bpf/bpf.h

# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
mkdir -p %{buildroot}/%{_mandir}/man1
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
%{make} -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif
%ifarch x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   %{tools_make} DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   %{tools_make} DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
%{tools_make} INSTALL_ROOT=%{buildroot} install
popd
pushd tools/iio
%{tools_make} DESTDIR=%{buildroot} install
popd
pushd tools/gpio
%{tools_make} DESTDIR=%{buildroot} install
popd
pushd tools/kvm/kvm_stat
make INSTALL_ROOT=%{buildroot} install-tools
make INSTALL_ROOT=%{buildroot} install-man
popd
%endif

%if %{with_bpftool}
pushd tools/bpf/bpftool
%{bpftool_make} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install doc-install
popd
%endif

%if %{with_bpf_samples}
pushd samples/bpf
install -d %{buildroot}%{_libexecdir}/bpf-samples
find -type f -executable -exec install -m755 {} %{buildroot}%{_libexecdir}/bpf-samples \;
install -m755 *.sh %{buildroot}%{_libexecdir}/bpf-samples
# test_lwt_bpf.sh compiles test_lwt_bpf.c when run; this works only from the
# kernel tree. Just remove it.
rm %{buildroot}%{_libexecdir}/bpf-samples/test_lwt_bpf.sh
install -m644 *_kern.o %{buildroot}%{_libexecdir}/bpf-samples
install -m644 tcp_bpf.readme %{buildroot}%{_libexecdir}/bpf-samples
popd
%endif

# We have to do the headers checksum calculation after the tools install because
# these might end up installing their own set of headers on top of kernel's
%if %{with_headers}
# compute a content hash to export as Provides: kernel-headers-checksum
HEADERS_CHKSUM=$(export LC_ALL=C; find $RPM_BUILD_ROOT/usr/include -type f -name "*.h" \
			! -path $RPM_BUILD_ROOT/usr/include/linux/version.h | \
		 sort | xargs cat | sha1sum - | cut -f 1 -d ' ');
# export the checksum via usr/include/linux/version.h, so the dynamic
# find-provides can grab the hash to update it accordingly
echo "#define KERNEL_HEADERS_CHECKSUM \"$HEADERS_CHKSUM\"" >> $RPM_BUILD_ROOT/usr/include/linux/version.h
%endif

###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n kernel-tools-libs
/sbin/ldconfig

%postun -n kernel-tools-libs
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f\
     done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_post [<subpackage>]
#
%define kernel_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%kernel_variant_preun debug
%kernel_variant_post -v debug

%if %{with_zfcpdump}
%kernel_variant_preun zfcpdump
%kernel_variant_post -v zfcpdump
%endif

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_cross_headers}
%files cross-headers
%defattr(-,root,root)
/usr/*-linux-gnu/include/*
%endif

%if %{with_kernel_abi_whitelists}
%files -n kernel-abi-whitelists
%defattr(-,root,root,-)
/lib/modules/kabi-*
%endif

%if %{with_kabidw_base}
%ifarch x86_64 s390x ppc64 ppc64le aarch64
%files kabidw-base
%defattr(-,root,root)
/kabidw-base/%{_target_cpu}/*
%endif
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_datadir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt

%files -n python3-perf
%defattr(-,root,root)
%{python3_sitearch}/*

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)

%files -f python3-perf-debuginfo.list -n python3-perf-debuginfo
%defattr(-,root,root)
%endif
%endif # with_perf

%if %{with_tools}
%ifarch %{cpupowerarchs}
%defattr(-,root,root)
%files -n kernel-tools -f cpupower.lang
%{_bindir}/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%else # !cpupowerarchs
%files -n kernel-tools
%defattr(-,root,root)
%endif # cpupowerarchs
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_mandir}/man1/kvm_stat*
%{_bindir}/kvm_stat

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n kernel-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
%endif # with_tools

%if %{with_bpftool}
%files -n bpftool
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man7/bpf-helpers.7.gz
%{_mandir}/man8/bpftool-cgroup.8.gz
%{_mandir}/man8/bpftool-map.8.gz
%{_mandir}/man8/bpftool-prog.8.gz
%{_mandir}/man8/bpftool-perf.8.gz
%{_mandir}/man8/bpftool.8.gz
%{_mandir}/man8/bpftool-btf.8.gz
%{_mandir}/man8/bpftool-feature.8.gz
%{_mandir}/man8/bpftool-net.8.gz

%if %{with_debuginfo}
%files -f bpftool-debuginfo.list -n bpftool-debuginfo
%defattr(-,root,root)
%endif
%endif

%if %{with_bpf_samples}
%files -n bpf-samples
%{_libexecdir}/bpf-samples
%endif

# empty meta-package
%ifnarch %nobuildarches noarch
%files
%defattr(-,root,root)
%endif

%if %{with_gcov}
%ifarch x86_64 s390x ppc64le aarch64
%files gcov
%defattr(-,root,root)
%{_builddir}
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{2}\
%{expand:%%files -f kernel-%{?3:%{3}-}core.list %{?3:%{3}-}core}\
%defattr(-,root,root)\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING-%{version}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/%{?-k:%{-k*}}%{!?-k:vmlinuz}\
%ghost /%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/.vmlinuz.hmac \
%ghost /%{image_install_path}/.vmlinuz-%{KVERREL}%{?3:+%{3}}.hmac \
%ifarch aarch64\
/lib/modules/%{KVERREL}%{?3:+%{3}}/dtb \
%ghost /%{image_install_path}/dtb-%{KVERREL}%{?3:+%{3}} \
%endif\
%attr(600,root,root) /lib/modules/%{KVERREL}%{?3:+%{3}}/System.map\
%ghost /boot/System.map-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/symvers.gz\
/lib/modules/%{KVERREL}%{?3:+%{3}}/config\
%ghost /boot/symvers-%{KVERREL}%{?3:+%{3}}.gz\
%ghost /boot/config-%{KVERREL}%{?3:+%{3}}\
%ghost /boot/initramfs-%{KVERREL}%{?3:+%{3}}.img\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}/kernel\
/lib/modules/%{KVERREL}%{?3:+%{3}}/build\
/lib/modules/%{KVERREL}%{?3:+%{3}}/source\
/lib/modules/%{KVERREL}%{?3:+%{3}}/updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/weak-updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/bls.conf\
%{_datadir}/doc/kernel-keys/%{KVERREL}%{?3:+%{3}}/kernel-signing-ca.cer\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?3:+%{3}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f kernel-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%defattr(-,root,root)\
%{expand:%%files %{?3:%{3}-}devel}\
%defattr(-,root,root)\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files -f kernel-%{?3:%{3}-}modules-extra.list %{?3:%{3}-}modules-extra}\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?3}.list %{?3:%{3}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%if %{?3:1} %{!?3:0}\
%{expand:%%files %{3}}\
%defattr(-,root,root)\
%endif\
%endif\
%{nil}

%kernel_variant_files  %{with_vdso_install} %{with_up}
%kernel_variant_files  %{with_vdso_install} %{with_debug} debug
%kernel_variant_files  %{with_vdso_install} %{with_zfcpdump} zfcpdump

# plz don't put in a version string unless you're going to tag
# and build.
#
#
%changelog
* Fri Sep 20 2019 CentOS Sources <bugs@centos.org> - 4.18.0-80.11.2.el8.centos
- Apply debranding changes

* Sun Sep 15 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.11.2.el8_0]
- [vhost] vhost: make sure log_num < in_num (Eugenio Perez) [1750881 1750882] {CVE-2019-14835}

* Tue Sep 03 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.11.1.el8_0]
- [wireless] mwifiex: Don't abort on small, spec-compliant vendor IEs (Jarod Wilson) [1714475 1728992]
- [wireless] mwifiex: fix 802.11n/WPA detection (Jarod Wilson) [1714475 1714476] {CVE-2019-3846}

* Tue Aug 06 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.10.1.el8_0]
- [x86] x86/entry/64: Use JMP instead of JMPQ (Josh Poimboeuf) [1724500 1724501] {CVE-2019-1125}
- [x86] x86/speculation: Enable Spectre v1 swapgs mitigations (Josh Poimboeuf) [1724500 1724501] {CVE-2019-1125}
- [x86] x86/speculation: Prepare entry code for Spectre v1 swapgs mitigations (Josh Poimboeuf) [1724500 1724501] {CVE-2019-1125}
- [x86] x86/cpufeatures: Combine word 11 and 12 into a new scattered features word (Josh Poimboeuf) [1724500 1724501] {CVE-2019-1125}
- [x86] x86/cpufeatures: Carve out CQM features retrieval (Josh Poimboeuf) [1724500 1724501] {CVE-2019-1125}

* Mon Aug 05 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.9.1.el8_0]
- [netdrv] thunderx: eliminate extra calls to put_page() for pages held for recycling (Dean Nelson) [1726354 1644011]
- [netdrv] thunderx: enable page recycling for non-XDP case (Dean Nelson) [1726354 1644011]
- [arm64] arm64: kaslr: ensure randomized quantities are clean also when kaslr is off (Mark Salter) [1726357 1673068]
- [arm64] arm64: kaslr: ensure randomized quantities are clean to the PoC (Mark Salter) [1726357 1673068]
- [mm] powerpc/mm/64s/hash: Reallocate context ids on fork (Gustavo Duarte) [1734689 1723808] {CVE-2019-12817}
- [powerpc] powerpc/pseries/mobility: rebuild cacheinfo hierarchy post-migration (Steve Best) [1733282 1720929]
- [powerpc] powerpc/pseries/mobility: prevent cpu hotplug during DT update (Steve Best) [1733282 1720929]
- [powerpc] powerpc/cacheinfo: add cacheinfo_teardown, cacheinfo_rebuild (Steve Best) [1733282 1720929]
- [powerpc] powerpc/watchpoint: Restore NV GPRs while returning from exception (Steve Best) [1733281 1728557]
- [hid] HID: i2c-hid: Don't reset device upon system resume (Perry Yuan) [1727098 1715385]
- [netdrv] net/mlx5e: RX, Verify MPWQE stride size is in range (Alaa Hleihel) [1726372 1683589]
- [sound] ALSA: usb-audio: Fix UAF decrement if card has no live interfaces in card.c (Jaroslav Kysela) [1726371 1658924] {CVE-2018-19824}
- [sound] ALSA: hda - Enable runtime PM only for discrete GPU (Jaroslav Kysela) [1726361 1714817]
- [cpufreq] cpufreq: intel_pstate: Ignore turbo active ratio in HWP (David Arcari) [1726360 1711970]
- [infiniband] usnic_verbs: fix deadlock (Govindarajulu Varadarajan) [1726358 1688505]
- [infiniband] IB/usnic: Fix locking when unregistering (Govindarajulu Varadarajan) [1726358 1688505]
- [infiniband] IB/usnic: Fix potential deadlock (Govindarajulu Varadarajan) [1726358 1688505]
- [netdrv] igb: shorten maximum PHC timecounter update interval (Corinna Vinschen) [1726352 1637098]
- [netdrv] igb: shorten maximum PHC timecounter update interval (Corinna Vinschen) [1726352 1637098]
- [x86] x86/platform/UV: Use efi_runtime_lock to serialise BIOS calls (Frank Ramsay) [1724534 1677695]
- [security] selinux: overhaul sidtab to fix bug and improve performance (Ondrej Mosnacek) [1717780 1656787]
- [security] selinux: use separate table for initial SID lookup (Ondrej Mosnacek) [1717780 1656787]
- [security] selinux: refactor sidtab conversion (Ondrej Mosnacek) [1717780 1656787]
- [security] selinux: Cleanup printk logging in sidtab (Ondrej Mosnacek) [1717780 1656787]
- [security] selinux: Cleanup printk logging in services (Ondrej Mosnacek) [1717780 1656787]
- [security] selinux: Cleanup printk logging in policydb (Ondrej Mosnacek) [1717780 1656787]
- [crypto] crypto: authenc - fix parsing key with misaligned rta_len (Herbert Xu) [1715335 1707546]
- [mm] mm, page_alloc: fix has_unmovable_pages for HugePages (David Gibson) [1714758 1688114]
- [wireless] mwifiex: Abort at too short BSS descriptor element (Jarod Wilson) [1714475 1714476] {CVE-2019-3846}
- [wireless] mwifiex: Fix possible buffer overflows at parsing bss descriptor (Jarod Wilson) [1714475 1714476] {CVE-2019-3846}
- [nvme] nvme-pci: add missing unlock for reset error (Gopal Tiwari) [1712261 1703201]
- [nvme] nvme-pci: fix rapid add remove sequence (Gopal Tiwari) [1712261 1703201]
- [wireless] brcmfmac: add subtype check for event handling in data path (Stanislaw Gruszka) [1733895 1704684] {CVE-2019-9503}
- [wireless] brcmfmac: assure SSID length from firmware is limited (Stanislaw Gruszka) [1705385 1705386] {CVE-2019-9500}
- [include] fs: fix kABI for struct pipe_buf_operations (Miklos Szeredi) [1705006 1705007] {CVE-2019-11487}
- [fs] fs: prevent page refcount overflow in pipe_buf_get (Miklos Szeredi) [1705006 1705007] {CVE-2019-11487}
- [mm] mm: prevent get_user_pages() from overflowing page refcount (Miklos Szeredi) [1705006 1705007] {CVE-2019-11487}
- [include] mm: add 'try_get_page()' helper function (Miklos Szeredi) [1705006 1705007] {CVE-2019-11487}
- [include] mm: make page ref count overflow check tighter and more explicit (Miklos Szeredi) [1705006 1705007] {CVE-2019-11487}
- [fs] fuse: call pipe_buf_release() under pipe lock (Miklos Szeredi) [1705006 1705007] {CVE-2019-11487}
- [kvm] KVM: x86: nVMX: fix x2APIC VTPR read intercept (Vitaly Kuznetsov) [1697198 1697199]
- [kvm] KVM: x86: nVMX: close leak of L0's x2APIC MSRs (CVE-2019-3887) (Vitaly Kuznetsov) [1697198 1697199]

* Thu Aug 01 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.8.1.el8_0]
- [documentation] Documentation: Add ARM64 to kernel-parameters.rst (Jeremy Linton) [1726353 1640855]
- [arm64] arm64/speculation: Support 'mitigations=' cmdline option (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: ssbs: Don't treat CPUs with SSBS as unaffected by SSB (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: enable generic CPU vulnerabilites support (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: add sysfs vulnerability show for speculative store bypass (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Always enable ssb vulnerability detection (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: add sysfs vulnerability show for spectre-v2 (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Always enable spectre-v2 vulnerability detection (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Use firmware to detect CPUs that are not affected by Spectre-v2 (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Advertise mitigation of Spectre-v2, or lack thereof (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: add sysfs vulnerability show for meltdown (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Add sysfs vulnerability show for spectre-v1 (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Provide a command line to disable spectre_v2 mitigation (Jeremy Linton) [1726353 1640855]
- [documentation] powerpc/fsl: Add FSL_PPC_BOOK3E as supported arch for nospectre_v2 boot arg (Jeremy Linton) [1726353 1640855]
- [documentation] Documentation: Document arm64 kpti control (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: kpti: Whitelist HiSilicon Taishan v110 CPUs (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Add MIDR encoding for HiSilicon Taishan CPUs (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: kpti: Whitelist Cortex-A CPUs that don't implement the CSV3 field (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: kpti: Update arm64_kernel_use_ng_mappings() when forced on (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: kpti: Avoid rewriting early page tables when KASLR is enabled (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: capabilities: Merge duplicate Cavium erratum entries (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: capabilities: Merge entries for ARM64_WORKAROUND_CLEAN_CACHE (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: Use a raw spinlock in __install_bp_hardening_cb() (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: KVM: Guests can skip __install_bp_hardening_cb()s HYP work (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: fix SSBS sanitization (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: don't zero DIT on signal return (Jeremy Linton) [1726353 1640855]
- [kvm] KVM: arm64: Set SCTLR_EL2.DSSBS if SSBD is forcefully disabled and !vhe (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: ssbd: Add support for PSTATE.SSBS rather than trapping to EL3 (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: ssbd: Drop #ifdefs for PR_SPEC_STORE_BYPASS (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: cpufeature: Detect SSBS and advertise to userspace (Jeremy Linton) [1726353 1640855]
- [arm64] arm64: move SCTLR_EL{1,2} assertions to <asm/sysreg.h> (Jeremy Linton) [1726353 1640855]
- Revert: [arm64] arm64/speculation: Support 'mitigations=' cmdline option (Josh Poimboeuf) [1726353 1640855] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [kernel] ptrace: Fix ->ptracer_cred handling for PTRACE_TRACEME (Aristeu Rozanski) [1730958 1730959] {CVE-2019-13272}

* Mon Jun 24 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.7.1.el8_0]
- [x86] Update stepping values for Whiskey Lake U/Y (David Arcari) [1722372 1704801]
- [x86] x86/perf/amd: Resolve NMI latency issues for active PMCs (David Arcari) [1722367 1640238]
- [x86] x86/perf/amd: Resolve race condition when disabling PMC (David Arcari) [1722367 1640238]
- [edac] EDAC/amd64: Set maximum channel layer size depending on family (Gary Hook) [1722365 1690984]
- [edac] EDAC/amd64: Adjust printed chip select sizes when interleaved (Gary Hook) [1722365 1690984]
- [edac] EDAC/amd64: Recognize x16 symbol size (Gary Hook) [1722365 1690984]
- [edac] EDAC/amd64: Support more than two Unified Memory Controllers (Gary Hook) [1722365 1690984]
- [edac] EDAC/amd64: Use a macro for iterating over Unified Memory Controllers (Gary Hook) [1722365 1690984]
- [edac] EDAC, amd64: Add Family 17h, models 10h-2fh support (Gary Hook) [1722365 1690984]
- [edac] EDAC/amd64: Add Family 17h Model 30h PCI IDs (Aristeu Rozanski) [1722365 1696603]
- [x86] mark AMD Rome processors supported (David Arcari) [1721972 1520002]
- [x86] x86/mce: Handle varying MCA bank counts (David Arcari) [1721233 1668779]
- [iommu] iommu/vt-d: Disable ATS support on untrusted devices (Jerry Snitselaar) [1700376 1692246]
- [documentation] thunderbolt: Export IOMMU based DMA protection support to userspace (Jerry Snitselaar) [1700376 1692246]
- [iommu] iommu/vt-d: Do not enable ATS for untrusted devices (Jerry Snitselaar) [1700376 1692246]
- [iommu] iommu/vt-d: Force IOMMU on for platform opt in hint (Jerry Snitselaar) [1700376 1692246]
- [pci] PCI / ACPI: Identify untrusted PCI devices (Myron Stowe) [1700376 1704979]
- [acpi] ACPI / property: Allow multiple property compatible _DSD entries (Myron Stowe) [1700376 1537397]
- [net] tcp: enforce tcp_min_snd_mss in tcp_mtu_probing() (Florian Westphal) [1719922 1719923] {CVE-2019-11479}
- [net] tcp: add tcp_min_snd_mss sysctl (Florian Westphal) [1719922 1719923] {CVE-2019-11479}
- [net] tcp: tcp_fragment() should apply sane memory limits (Florian Westphal) [1719857 1719858] {CVE-2019-11478}
- [net] tcp: limit payload size of sacked skbs (Florian Westphal) [1719602 1719603] {CVE-2019-11477}

* Tue Jun 18 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.6.1.el8_0]
- [mm] mm: defer ZONE_DEVICE page initialization to the point where we init pgmap (Waiman Long) [1719635 1666538]
- [mm] mm: create non-atomic version of SetPageReserved for init use (Waiman Long) [1719635 1666538]
- [mm] mm: provide kernel parameter to allow disabling page init poisoning (Waiman Long) [1719635 1666538]
- [mm] mm, slub: restore the original intention of prefetch_freepointer() (Rafael Aquini) [1718237 1714671]
- [security] selinux: do not report error on connect(AF_UNSPEC) (Ondrej Mosnacek) [1717870 1707828]
- [security] selinux: Check address length before reading address family (Ondrej Mosnacek) [1717870 1707828]
- [powerpc] powerpc/tm: Fix stack pointer corruption (Desnes Augusto Nunes do Rosario) [1717869 1707635]
- [md] dm cache metadata: Fix loading discard bitset (Mike Snitzer) [1717868 1701618]
- [md] dm mpath: fix missing call of path selector type->end_io (Mike Snitzer) [1717804 1686227]
- [mm] mm/memory.c: do_fault: avoid usage of stale vm_area_struct ("Herton R. Krzesinski") [1717801 1684734]
- [net] sunrpc: fix 4 more call sites that were using stack memory with a scatterlist (Scott Mayhew) [1717800 1679183]
- [net] sunrpc: Don't use stack buffer with scatterlist (Scott Mayhew) [1717800 1679183]
- [scsi] scsi: mpt3sas: Fix kernel panic during expander reset (Tomas Henzl) [1717791 1677693]
- [security] selinux: always allow mounting submounts (Ondrej Mosnacek) [1717777 1647723]
- [drm] drm/bufs: Fix Spectre v1 vulnerability (Rob Clark) [1717382 1663467]
- [drm] drm/ioctl: Fix Spectre v1 vulnerabilities (Rob Clark) [1717382 1663467]
- [tools] perf annotate: Fix getting source line failure (Michael Petlan) [1716887 1614435]
- [iommu] iommu/amd: Set exclusion range correctly (Jerry Snitselaar) [1715336 1702766]
- [iommu] iommu/amd: Reserve exclusion range in iova-domain (Jerry Snitselaar) [1717344 1694835]
- [kvm] KVM: PPC: Book3S: Add count cache flush parameters to kvmppc_get_cpu_char() (Vitaly Kuznetsov) [1715018 1694456]
- [s390] kvm: s390: Fix potential spectre warnings (Thomas Huth) [1714754 1702344]
- [drm] drm/i915/gvt: Fix mmap range check (Alex Williamson) [1713572 1713573] {CVE-2019-11085}
- [scsi] scsi: megaraid_sas: return error when create DMA pool failed (Tomas Henzl) [1712862 1712863] {CVE-2019-11810}

* Wed Jun 05 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.5.1.el8_0]
- [kernel] sched/fair: Limit sched_cfs_period_timer() loop to avoid hard lockup (Joel Savitz) [1715345 1695651]
- [kernel] sched/fair: Fix O(nr_cgroups) in the load balancing path (Phil Auld) [1715343 1685636] {CVE-2018-20784}
- [kernel] sched/fair: Fix insertion in rq->leaf_cfs_rq_list (Phil Auld) [1715343 1685636] {CVE-2018-20784}
- [kernel] sched/fair: Add tmp_alone_branch assertion (Phil Auld) [1715343 1685636] {CVE-2018-20784}
- [kernel] sched/fair: Fix infinite loop in update_blocked_averages() by reverting a9e7f6544b9c (Phil Auld) [1715343 1685636] {CVE-2018-20784}
- [rpmspec] apply linux-kernel-test.patch when building ("Herton R. Krzesinski") [1715340 1690534]
- [rpmspec] Fix cross builds (Jiri Olsa) [1715339 1694956]
- [kernel] sched/fair: Do not re-read ->h_load_next during hierarchical load calculation (Phil Auld) [1715337 1701762]
- [kvm] KVM: PPC: Book3S HV: Save/restore vrsave register in kvmhv_p9_guest_entry() (Suraj Jitindar Singh) [1714753 1700272]
- [powerpc] KVM: PPC: Book3S HV: Perserve PSSCR FAKE_SUSPEND bit on guest exit (Suraj Jitindar Singh) [1714751 1689768]
- [powerpc] powerpc/powernv/ioda: Fix locked_vm counting for memory used by IOMMU tables (David Gibson) [1714746 1674410]
- [char] ipmi_si: fix use-after-free of resource->name (Tony Camuso) [1714409 1714410] {CVE-2019-11811}
- [x86] Update stepping values for coffee lake desktop (David Arcari) [1711048 1704800]

* Thu May 16 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.4.1.el8_0]
- [netdrv] ice: Do autoneg based on VSI state (Jonathan Toppins) [1709433 1687903]
- [arm64] arm64: apply workaround on A64FX v1r0 (Mark Langsdorf) [1700901 1692306]
- [arm64] arm64/speculation: Support 'mitigations=' cmdline option (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [s390] s390/speculation: Support 'mitigations=' cmdline option (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [powerpc] powerpc/speculation: Support 'mitigations=' cmdline option (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [powerpc] powerpc/64: Disable the speculation barrier from the command line (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add 'mitigations=' support for MDS (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation: Support 'mitigations=' cmdline option (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [kernel] cpu/speculation: Add 'mitigations=' cmdline option (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Print SMT vulnerable on MSBDS with mitigations off (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Fix comment (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add SMT warning message (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation: Move arch_smt_update() call to after mitigation decisions (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add mds=full, nosmt cmdline option (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [documentation] Documentation: Add MDS vulnerability documentation (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [documentation] Documentation: Move L1TF to separate directory (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add mitigation mode VMWERV (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add sysfs reporting for MDS (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add mitigation control for MDS (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Conditionally clear CPU buffers on idle entry (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/kvm/vmx: Add MDS protection when L1D Flush is not active (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Clear CPU buffers on exit to user (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add mds_clear_cpu_buffers() (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [kvm] x86/kvm: Expose X86_FEATURE_MD_CLEAR to guests (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add BUG_MSBDS_ONLY (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation/mds: Add basic bug infrastructure for MDS (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation: Consolidate CPU whitelists (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/msr-index: Cleanup bit defines (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/speculation: Cast ~SPEC_CTRL_STIBP atomic value to int (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [x86] x86/cpu: Sanitize FAM6_ATOM naming (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [include] locking/atomics, asm-generic: Move some macros from <linux/bitops.h> to a new <linux/bits.h> file (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}
- [tools] tools include: Adopt linux/bits.h (Josh Poimboeuf) [1698809 1698896 1699001 1705836 1690338 1690360 1690351 1705312] {CVE-2018-12130 CVE-2018-12127 CVE-2018-12126 CVE-2019-11091}

* Tue May 14 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.3.1.el8_0]
- [mm] mm: enforce min addr even if capable() in expand_downwards() (Rafael Aquini) [1708829 1687667] {CVE-2019-9213}
- [powerpc] powerpc/radix: Fix kernel crash with mremap() (Steve Best) [1708617 1674186]
- [powerpc] powerpc/security: Fix spectre_v2 reporting (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/powernv: Query firmware for count cache flush settings (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/pseries: Query hypervisor for count cache flush settings (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/64s: Add support for software count cache flush (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/64s: Add new security feature flags for count cache flush (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/asm: Add a patch_site macro & helpers for patching instructions (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/64: Call setup_barrier_nospec() from setup_arch() (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc/64: Add CONFIG_PPC_BARRIER_NOSPEC (Gustavo Duarte) [1708112 1694456]
- [powerpc] powerpc64s: Show ori31 availability in spectre_v1 sysfs file not v2 (Gustavo Duarte) [1708112 1694456]
- [of] of: __of_detach_node() - remove node from phandle cache (Steve Best) [1708102 1669198]
- [of] of: of_node_get()/of_node_put() nodes held in phandle cache (Steve Best) [1708102 1669198]
- [fs] debugfs: Fix EPERM regression from kernel lockdown check (Lenny Szubowicz) [1708100 1686755]
- [block] nvme: lock NS list changes while handling command effects (David Milburn) [1701140 1672759]

* Fri May 10 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.2.1.el8_0]
- [netdrv] qed: Fix qed_mcp_halt|resume() (Manish Chopra) [1704184 1697310]
- [cpufreq] cpufreq: intel_pstate: Also use CPPC nominal_perf for base_frequency (Prarit Bhargava) [1706739 1696131]
- [acpi] ACPI / CPPC: Fix guaranteed performance handling (Prarit Bhargava) [1706739 1696131]
- [arm64] arm64: Add workaround for Fujitsu A64FX erratum 010001 (Mark Langsdorf) [1700902 1666951]
- [s390] vfio_ap: link the vfio_ap devices to the vfio_ap bus subsystem (Cornelia Huck) [1700290 1686044]
- [netdrv] net/mlx4_en: Force CHECKSUM_NONE for short ethernet frames (Alaa Hleihel) [1700289 1651509]
- [netdrv] net/mlx5e: Force CHECKSUM_UNNECESSARY for short ethernet frames (Alaa Hleihel) [1700289 1651509]
- [pci] PCI: pciehp: Fix re-enabling the slot marked for safe removal (Myron Stowe) [1700288 1695922]

* Sat Apr 27 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.1.1.el8_0]
- [zstream] switch to zstream (Frantisek Hrbata)

* Wed Mar 13 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-80.el8]
- [arm64] revert "arm64: tlb: Avoid synchronous TLBIs when freeing page tables" (Christoph von Recklinghausen) [1685697]

* Mon Mar 11 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-79.el8]
- [firmware] drivers/firmware: psci_checker: stash and use topology_core_cpumask for hotplug tests (Josh Poimboeuf) [1687101]
- [arm64] arm64: topology: re-introduce numa mask check for scheduler MC selection (Josh Poimboeuf) [1687101]
- [arm64] arm64: topology: rename llc_siblings to align with other struct members (Josh Poimboeuf) [1687101]
- [arm64] arm64: smp: remove cpu and numa topology information when hotplugging out CPU (Josh Poimboeuf) [1687101]
- [arm64] arm64: topology: restrict updating siblings_masks to online cpus only (Josh Poimboeuf) [1687101]
- [arm64] arm64: topology: add support to remove cpu topology sibling masks (Josh Poimboeuf) [1687101]
- [arm64] arm64: numa: separate out updates to percpu nodeid and NUMA node cpumap (Josh Poimboeuf) [1687101]
- [arm64] arm64: topology: refactor reset_cpu_topology to add support for removing topology (Josh Poimboeuf) [1687101]

* Sun Mar 10 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-78.el8]
- [fs] gfs2: Fix missed wakeups in find_insert_glock (Andreas Grunbacher) [1678907]

* Thu Mar 07 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-77.el8]
- [firmware] efi: Reduce the amount of memblock reservations for persistent allocations (Bhupesh Sharma) [1682988]
- [firmware] efi: Permit multiple entries in persistent memreserve data structure (Bhupesh Sharma) [1682988]
- [kernel] cpu/hotplug: Create SMT sysfs interface for all arches (Josh Poimboeuf) [1686068]
- [net] netfilter: nft_set_hash: bogus element self comparison from deactivation path (Florian Westphal) [1678574]
- [net] netfilter: nft_set_hash: fix lookups with fixed size hash on big endian (Florian Westphal) [1678574]

* Tue Mar 05 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-76.el8]
- [security] revert "Add a SysRq option to lift kernel lockdown" (Lenny Szubowicz) [1684348]
- [s390] s390/setup: fix boot crash for machine without EDAT-1 (Philipp Rudo) [1677357]
- [s390] s390/setup: fix early warning messages (Philipp Rudo) [1677357]

* Fri Mar 01 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-75.el8]
- [netdrv] net: hns3: add 8 BD limit for tx flow (Xiaojun Tan) [1676771]
- [netdrv] net: hns3: fix a SSU buffer checking bug (Xiaojun Tan) [1676771]
- [netdrv] net: hns3: aligning buffer size in SSU to 256 bytes (Xiaojun Tan) [1676771]
- [netdrv] net: hns3: getting tx and dv buffer size through firmware (Xiaojun Tan) [1676771]
- [net] netfilter: nf_nat_snmp_basic: add missing length checks in ASN.1 cbs (Florian Westphal) [1676602]
- [char] ipmi: fix use-after-free of user->release_barrier.rda (Xiaojun Tan) [1677550]
- [char] ipmi: Prevent use-after-free in deliver_response (Xiaojun Tan) [1677550]

* Wed Feb 27 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-74.el8]
- [x86] revert "cpu/hotplug: Add SMT policy options" (Josh Poimboeuf) [1683690]
- [crypto] net: crypto set sk to NULL when af_alg_release (Neil Horman) [1679450] {CVE-2019-8912}
- [drm] drm/i915/gvt: update force-to-nonpriv register whitelist (Paul Lai) [1643972]
- [kernel] MODSIGN: Also check platform keyring in mod_verify_sig() (Lenny Szubowicz) [1568532]
- [kernel] Fix for module sig verification (Lenny Szubowicz) [1568532]
- [security] efi: Lock down the kernel if booted in secure boot mode (Lenny Szubowicz) [1568532]
- [firmware] efi: Add an EFI_SECURE_BOOT flag to indicate secure boot mode (Lenny Szubowicz) [1568532]
- [x86] Copy secure_boot flag in boot params across kexec reboot (Lenny Szubowicz) [1568532]
- [fs] debugfs: Restrict debugfs when the kernel is locked down (Lenny Szubowicz) [1568532]
- [mm] x86/mmiotrace: Lock down the testmmiotrace module (Lenny Szubowicz) [1568532]
- [kernel] Lock down module params that specify hardware parameters (eg. ioport) (Lenny Szubowicz) [1568532]
- [tty] Lock down TIOCSSERIAL (Lenny Szubowicz) [1568532]
- [pcmcia] Prohibit PCMCIA CIS storage when the kernel is locked down (Lenny Szubowicz) [1568532]
- [acpi] acpi: Disable ACPI table override if the kernel is locked down (Lenny Szubowicz) [1568532]
- [acpi] acpi: Ignore acpi_rsdp kernel param when the kernel has been locked down (Lenny Szubowicz) [1568532]
- [acpi] ACPI: Limit access to custom_method when the kernel is locked down (Lenny Szubowicz) [1568532]
- [x86] x86/msr: Restrict MSR access when the kernel is locked down (Lenny Szubowicz) [1568532]
- [x86] x86: Lock down IO port access when the kernel is locked down (Lenny Szubowicz) [1568532]
- [pci] PCI: Lock down BAR access when the kernel is locked down (Lenny Szubowicz) [1568532]
- [kernel] uswsusp: Disable when the kernel is locked down (Lenny Szubowicz) [1568532]
- [kernel] hibernate: Disable when the kernel is locked down (Lenny Szubowicz) [1568532]
- [kernel] kexec_load: Disable at runtime if the kernel is locked down (Lenny Szubowicz) [1568532]
- [char] Restrict /dev/{mem, kmem, port} when the kernel is locked down (Lenny Szubowicz) [1568532]
- [kernel] MODSIGN: Enforce module signatures if the kernel is locked down (Lenny Szubowicz) [1568532]
- [security] Add a SysRq option to lift kernel lockdown (Lenny Szubowicz) [1568532]
- [security] Add the ability to lock down access to the running kernel image (Lenny Szubowicz) [1568532]

* Tue Feb 26 2019 Frantisek Hrbata <fhrbata@redhat.com> [4.18.0-73.el8]
- [net] tun: forbid iface creation with rtnl ops (Sabrina Dubroca) [1680969]
- [net] revert "bridge: do not add port to router list when receives query with source 0.0.0.0" (Hangbin Liu) [1679896]
- [net] sctp: walk the list of asoc safely (Marcelo Leitner) [1679920] {CVE-2019-8956}
- [net] netfilter: nf_nat: skip nat clash resolution for same-origin entries (Florian Westphal) [1677647]
- [net] netfilter: nf_conntrack: resolve clash for matching conntracks (Florian Westphal) [1677647]
- [net] netfilter: nf_tables: fix flush after rule deletion in the same batch (Phil Sutter) [1677672]
- [net] gro_cell: add napi_disable in gro_cells_destroy (Stefano Brivio) [1674408]
- [net] sctp: call gso_reset_checksum when computing checksum in sctp_gso_segment (Xin Long) [1669386]
- [net] ipvs: fix dependency on nf_defrag_ipv6 (Andrea Claudi) [1660808]
- [net] sctp: check and update stream->out_curr when allocating stream_out (Xin Long) [1651877]

* Mon Feb 25 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-72.el8]
- [x86] cpu/hotplug: Add SMT policy options (Josh Poimboeuf) [1677405]

* Fri Feb 22 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-71.el8]
- [pci] pci/quirks: Add quirk to reset nvgpu at boot for the Lenovo ThinkPad P50 (Lyude Paul) [1677022]
- [arm64] arm64, vmcoreinfo : Append 'MAX_USER_VA_BITS' to vmcoreinfo (Bhupesh Sharma) [1672962]
- [md] dm thin: fix bug where bio that overwrites thin block ignores FUA (Mike Snitzer) [1679211]
- [pci] PCI: Fix "try" semantics of bus and slot reset (Myron Stowe) [1662901]
- [acpi] acpi/nfit: Fix bus command validation (Jeff Moyer) [1673958]
- [pci] PCI/MSI: Return -ENOSPC from pci_alloc_irq_vectors_affinity() (Myron Stowe) [1667773]
- [fs] NFS: Don't use page_file_mapping after removing the page (Benjamin Coddington) [1664190]
- [fs] NFS: Fix up return value on fatal errors in nfs_page_async_flush() (Benjamin Coddington) [1664190]
- [md] md: fix raid10 hang issue caused by barrier (Xiao Ni) [1630921]
- [md] md/raid1: don't clear bitmap bits on interrupted recovery. (Xiao Ni) [1677360]
- [virt] kvm: fix kvm_ioctl_create_device() reference counting (CVE-2019-6974) (Paolo Bonzini) [1673843] {CVE-2019-6974}
- [block] blk-mq: fix a hung issue when fsync (Ming Lei) [1674399]
- [block] Revert "block: cover another queue enter recursion via BIO_QUEUE_ENTERED" (Ming Lei) [1673966]
- [tools] perf tools: Check for null when copying nsinfo. (Jiri Olsa) [1676451]
- [iommu] iommu/amd: Fix IOMMU page flush when detach device from a domain (Suravee Suthikulpanit) [1672476]

* Tue Feb 19 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-70.el8]
- [kernel] namespace: Add padding fix to user_table[] (Prarit Bhargava) [1677103]
- [x86] KVM: nVMX: unconditionally cancel preemption timer in free_nested (CVE-2019-7221) (Paolo Bonzini) [1673841] {CVE-2019-7221}
- [scsi] scsi: sd: fix entropy gathering for most rotational disks (Ewan Milne) [1676735]
- [scsi] scsi: sd: Contribute to randomness when running rotational device (Ewan Milne) [1676735]
- [rpmspec] Revert "Drop -doc subpackage" (Prarit Bhargava) [1657609]
- [net] svcrdma: Remove max_sge check at connect time (Don Dutile) [1638869]
- [net] svcrdma: Reduce max_send_sges (Don Dutile) [1638869]
- [arm64] arm64: mm: Introduce MAX_USER_VA_BITS definition (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlb: Rewrite stale comment in asm/tlbflush.h (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlb: Avoid synchronous TLBIs when freeing page tables (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlb: Remove redundant !CONFIG_HAVE_RCU_TABLE_FREE code (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlbflush: Allow stride to be specified for __flush_tlb_range() (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlb: Justify non-leaf invalidation in flush_tlb_range() (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlb: Add DSB ISHST prior to TLBI in __flush_tlb_[kernel_]pgtable() (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlb: Use last-level invalidation in flush_tlb_kernel_range() (Christoph von Recklinghausen) [1672997]
- [mm] arm64: mm: EXPORT vabits_user to modules (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: fix ARM64_USER_VA_BITS_52 builds (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: Kconfig: Re-jig CONFIG options for 52-bit VA (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: mm: Allow forcing all userspace addresses to 52-bit (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: mm: introduce 52-bit userspace support (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: mm: Prevent mismatched 52-bit VA support (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: mm: Offset TTBR1 to allow 52-bit PTRS_PER_PGD (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: mm: Define arch_get_mmap_end, arch_get_mmap_base (Christoph von Recklinghausen) [1672997]
- [firmware] arm64: mm: Introduce DEFAULT_MAP_WINDOW (Christoph von Recklinghausen) [1672997]
- [mm] mm: mmap: Allow for "high" userspace addresses (Christoph von Recklinghausen) [1672997]
- [mm] arm64: mm: apply r/o permissions of VM areas to its linear alias as well (Christoph von Recklinghausen) [1672997]
- [mm] arm64: mm: purge lazily unmapped vm regions before changing permissions (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: mm: Don't wait for completion of TLB invalidation when page aging (Christoph von Recklinghausen) [1672997]
- [mm] arm64: mm: Use __pa_symbol() for set_swapper_pgd() (Christoph von Recklinghausen) [1672997]
- [mm] arm64: mm: Drop the unused cpu parameter (Christoph von Recklinghausen) [1672997]
- [arm64] arm64/mm: move runtime pgds to rodata (Christoph von Recklinghausen) [1672997]
- [mm] arm64/mm: use fixmap to modify swapper_pg_dir (Christoph von Recklinghausen) [1672997]
- [arm64] arm64/mm: Separate boot-time page tables from swapper_pg_dir (Christoph von Recklinghausen) [1672997]
- [arm64] arm64/mm: Pass ttbr1 as a parameter to __enable_mmu() (Christoph von Recklinghausen) [1672997]
- [mm] arm64: fix erroneous warnings in page freeing functions (Christoph von Recklinghausen) [1672997]
- [mm] arm64: Implement page table free interfaces (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: tlbflush: Introduce __flush_tlb_kernel_pgtable (Christoph von Recklinghausen) [1672997]
- [lib] ioremap: Update pgtable free interfaces with addr (Christoph von Recklinghausen) [1672997]
- [mm] x86/mm: Disable ioremap free page handling on x86-PAE (Christoph von Recklinghausen) [1672997]
- [arm64] arm64: KVM: Enable Common Not Private translations (Christoph von Recklinghausen) [1504991]
- [arm64] arm64: mm: Support Common Not Private translations (Christoph von Recklinghausen) [1504991]
- [kernel] cpu/hotplug: Fix "SMT disabled by BIOS" detection for KVM (Igor Mammedov) [1668147]
- [tools] perf tools: Compile perf with -g instead of -ggdb3 to workaround gdb crash (Jiri Olsa) [1667109]

* Thu Feb 14 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-69.el8]
- [fs] Revert "gfs2: Fix loop in gfs2_rbm_find" (Andreas Grunbacher) [1658528]
- [net] bpf: fix sanitation of alu op with pointer / scalar type from different paths (Jiri Olsa) [1673631] {CVE-2019-7308}
- [net] bpf: prevent out of bounds speculation on pointer arithmetic (Jiri Olsa) [1673631] {CVE-2019-7308}
- [net] bpf: move {prev_,}insn_idx into verifier env (Jiri Olsa) [1673631] {CVE-2019-7308}
- [net] bpf/verifier: per-register parent pointers (Jiri Olsa) [1673631] {CVE-2019-7308}
- [net] bpf: restrict unknown scalars of mixed signed bounds for unprivileged (Jiri Olsa) [1673631] {CVE-2019-7308}
- [net] bpf: Simplify ptr_min_max_vals adjustment (Jiri Olsa) [1673631] {CVE-2019-7308}
- [net] bpf: fix inner map masking to prevent oob under speculation (Jiri Olsa) [1673631] {CVE-2019-7308}
- [include] KABI: struct class padding (Prarit Bhargava) [1670035]
- [include] KABI: struct timer_list padding (Prarit Bhargava) [1670035]
- [include] KABI: struct irq_domain padding (Prarit Bhargava) [1670035]
- [nvdimm] libnvdimm, pmem: Fix badblocks population for 'raw' namespaces (Jeff Moyer) [1672315]
- [netdrv] net/mlx5e: FPGA, fix Innova IPsec TX offload data path performance (Alaa Hleihel) [1648230]
- [kernel] exec: increase BINPRM_BUF_SIZE to 256 (Oleg Nesterov) [1447445]

* Wed Feb 13 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-68.el8]
- [include] KABI: struct kset padding (Prarit Bhargava) [1669796]
- [include] KABI: struct kobject and kobj_type padding (Prarit Bhargava) [1669796]
- [include] KABI: struct delayed_work padding (Prarit Bhargava) [1669796]
- [include] KABI: struct work_struct padding (Prarit Bhargava) [1669796]
- [include] KABI: struct hrtimer padding (Prarit Bhargava) [1669796]
- [include] KABI: struct user_namespace padding (Prarit Bhargava) [1669796]
- [include] KABI: struct resource padding (Prarit Bhargava) [1669796]
- [include] KABI: Protect device_driver struct (Prarit Bhargava) [1666316]
- [include] KABI: Protect radix functions (Prarit Bhargava) [1669079]
- [char] ipmi: msghandler: Fix potential Spectre v1 vulnerabilities (Tony Camuso) [1672582]
- [vhost] vhost: fix OOB in get_rx_bufs() (Jason Wang) [1668665] {CVE-2018-16880}

* Sat Feb 09 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-67.el8]
- [md] dm: don't use bio_trim() afterall (Mike Snitzer) [1673657]
- [md] dm: add memory barrier before waitqueue_active (Mike Snitzer) [1673110]
- [x86] x86: uaccess: Inhibit speculation past access_ok() in user_access_begin() (Joe Lawrence) [1670113] {CVE-2018-20669}
- [kernel] make 'user_access_begin()' do 'access_ok()' (Joe Lawrence) [1670113] {CVE-2018-20669}
- [drm] i915: fix missing user_access_end() in page fault exception case (Joe Lawrence) [1670113] {CVE-2018-20669}
- [drm] drm/i915: Force the slow path after a user-write error (Joe Lawrence) [1670113] {CVE-2018-20669}
- [x86] x86/microcode/amd: Don't falsely trick the late loading mechanism (David Arcari) [1654904]
- [fs] iomap: get/put the page in iomap_page_create/release() (Artem Savkov) [1664298]
- [scsi] scsi: qla2xxx: Add new FC-NVMe enable BIT to enable FC-NVMe feature (Himanshu Madhani) [1671569]
- [message] mptsas: pci-id table changes (Tomas Henzl) [1666730]
- [message] mptsas: Taint kernel if mptsas is loaded (Tomas Henzl) [1666730]
- [kernel] genirq/matrix: Improve target CPU selection for managed interrupts. (Gary Hook) [1669557]
- [kernel] irq/matrix: Spread managed interrupts on allocation (Gary Hook) [1669557]
- [kernel] irq/matrix: Split out the CPU selection code into a helper (Gary Hook) [1669557]
- [net] sit: check if IPv6 enabled before calling ip6_err_gen_icmpv6_unreach() (Stefano Brivio) [1671680]
- [net] geneve: should not call rt6_lookup() when ipv6 was disabled (Stefano Brivio) [1671680]
- [net] netfilter: physdev: relax br_netfilter dependency (Phil Sutter) [1650382]
- [net] netfilter: nf_tables: add NFTA_RULE_POSITION_ID to nla_policy (Phil Sutter) [1670563]
- [net] netfilter: nf_tables: Support RULE_ID reference in new rule (Phil Sutter) [1670563]
- [net] rtnetlink: fix incorrect handling of device stats passed to userspace (Ivan Vecera) [1668298]
- [net] netfilter: nf_tables: handle nft_object lookups via rhltable (Phil Sutter) [1659725]
- [net] netfilter: nf_tables: prepare nft_object for lookups via hashtable (Phil Sutter) [1659725]
- [net] netfilter: nf_tables: selective rule dump needs table to be specified (Phil Sutter) [1659725]
- [net] netfilter: nf_tables: Fix for endless loop when dumping ruleset (Phil Sutter) [1659725]
- [net] netfilter: nf_tables: Speed up selective rule dumps (Phil Sutter) [1659725]
- [net] exclude sock_reuseport from kABI protection (Paolo Abeni) [1665984]
- [include] KABI: struct device padding (Don Dutile) [1664445]
- [include] KABI: struct dma_map_ops padding (Don Dutile) [1664482]
- [kernel] swiotlb: clear io_tlb_start and io_tlb_end in swiotlb_exit (Don Dutile) [1664484]
- [kernel] dma-mapping: remove a few unused exports (Don Dutile) [1664484]
- [include] dma-mapping: properly stub out the DMA API for !CONFIG_HAS_DMA (Don Dutile) [1664484]
- [kernel] dma-mapping: remove dmam_{declare,release}_coherent_memory (Don Dutile) [1664484]
- [kernel] dma-mapping: implement dmam_alloc_coherent using dmam_alloc_attrs (Don Dutile) [1664484]
- [include] dma-mapping: implement dma_map_single_attrs using dma_map_page_attrs (Don Dutile) [1664484]
- [include] dma-mapping: fix flags in dma_alloc_wc (Don Dutile) [1664484]
- [include] dma-mapping: deprecate dma_zalloc_coherent (Don Dutile) [1664484]
- [arm64] arm64: default to the direct mapping in get_arch_dma_ops (Don Dutile) [1664484]
- [kernel] dma-mapping: fix inverted logic in dma_supported (Don Dutile) [1664484]
- [include] dma-mapping: bypass indirect calls for dma-direct (Don Dutile) [1664484]
- [kernel] dma-direct: merge swiotlb_dma_ops into the dma_direct code (Don Dutile) [1664484]
- [kernel] dma-direct: do not include SME mask in the DMA supported check (Don Dutile) [1664484]
- [kernel] dma-direct: use dma_direct_map_page to implement dma_direct_map_sg (Don Dutile) [1664484]
- [kernel] dma-direct: improve addressability error reporting (Don Dutile) [1664484]
- [kernel] dma-direct: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [xen] swiotlb: remove dma_mark_clean (Don Dutile) [1664484]
- [xen] swiotlb: remove SWIOTLB_MAP_ERROR (Don Dutile) [1664484]
- [xen] xen-swiotlb: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [kernel] swiotlb: Skip cache maintenance on map error (Don Dutile) [1664484]
- [kernel] swiotlb: add support for non-coherent DMA (Don Dutile) [1664484]
- [kernel] swiotlb: mark is_swiotlb_buffer static (Don Dutile) [1664484]
- [kernel] swiotlb: remove a pointless comment (Don Dutile) [1664484]
- [kernel] swiotlb: clean up reporting (Don Dutile) [1664484]
- [kernel] dma-direct: reject highmem pages from dma_alloc_from_contiguous (Don Dutile) [1664484]
- [kernel] dma-direct: provide page based alloc/free helpers (Don Dutile) [1664484]
- [include] dma-direct: Make DIRECT_MAPPING_ERROR viable for SWIOTLB (Don Dutile) [1664484]
- [kernel] dma-direct: respect DMA_ATTR_NO_WARN (Don Dutile) [1664484]
- [kernel] dma-direct: document the zone selection logic (Don Dutile) [1664484]
- [kernel] dma-direct: fix return value of dma_direct_supported (Don Dutile) [1664484]
- [kernel] dma-direct: always allow dma mask <= physiscal memory size (Don Dutile) [1664484]
- [kernel] dma-direct: implement complete bus_dma_mask handling (Don Dutile) [1664484]
- [kernel] dma-direct: refine dma_direct_alloc zone selection (Don Dutile) [1664484]
- [kernel] dma-direct: add an explicit dma_direct_get_required_mask (Don Dutile) [1664484]
- [kernel] kernel/dma/direct: take DMA offset into account in dma_direct_supported (Don Dutile) [1664484]
- [kernel] dma-mapping: factor out dummy DMA ops (Don Dutile) [1664484]
- [mm] arm64: dma-mapping: Fix FORCE_CONTIGUOUS buffer clearing (Don Dutile) [1664484]
- [iommu] iommu/dma-iommu: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [iommu] iommu/vt-d: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [iommu] iommu/intel: small map_page cleanup (Don Dutile) [1664484]
- [iommu] intel-iommu: mark intel_dma_ops static (Don Dutile) [1664484]
- [iommu] ia64: remove iommu_dma_supported (Don Dutile) [1664484]
- [iommu] iommu: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [iommu] iommu/dma: Use fast DMA domain lookup (Don Dutile) [1664484]
- [x86] x86/amd_gart: fix unmapping of non-GART mappings (Don Dutile) [1664484]
- [x86] x86/amd_gart: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [mm] arm64: remove the dummy_dma_ops mapping_error method (Don Dutile) [1664484]
- [powerpc] powerpc: Do not redefine NEED_DMA_MAP_STATE (Don Dutile) [1664484]
- [powerpc] powerpc/iommu: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [s390] s390: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [kernel] dma-mapping: always build the direct mapping code (Don Dutile) [1664484]
- [kernel] dma-mapping: move dma_cache_sync out of line (Don Dutile) [1664484]
- [kernel] dma-mapping: move various slow path functions out of line (Don Dutile) [1664484]
- [base] dma-mapping: move dma_get_required_mask to kernel/dma (Don Dutile) [1664484]
- [base] dma-mapping: move dma_default_get_required_mask under ifdef (Don Dutile) [1664484]
- [include] dma-mapping: merge dma_unmap_page_attrs and dma_unmap_single_attrs (Don Dutile) [1664484]
- [include] dma-mapping: simplify the dma_sync_single_range_for_{cpu,device} implementation (Don Dutile) [1664484]
- [include] dma-mapping: return an error code from dma_mapping_error (Don Dutile) [1664484]
- [pci] dma-mapping: remove the mapping_error dma_map_ops method (Don Dutile) [1664484]
- [include] dma-mapping: provide a generic DMA_MAPPING_ERROR (Don Dutile) [1664484]
- [kernel] dma-mapping: move the arm64 noncoherent alloc/free support to common code (Don Dutile) [1664484]
- [mm] arm64: fix warnings without CONFIG_IOMMU_DMA (Don Dutile) [1664484]
- [arm64] arm64: use the generic swiotlb_dma_ops (Don Dutile) [1664484]
- [kernel] swiotlb: don't dip into swiotlb pool for coherent allocations (Don Dutile) [1664484]
- [kernel] swiotlb: refactor swiotlb_map_page (Don Dutile) [1664484]
- [kernel] swiotlb: use swiotlb_map_page in swiotlb_map_sg_attrs (Don Dutile) [1664484]
- [kernel] swiotlb: merge swiotlb_unmap_page and unmap_single (Don Dutile) [1664484]
- [kernel] swiotlb: remove the overflow buffer (Don Dutile) [1664484]
- [kernel] swiotlb: do not panic on mapping failures (Don Dutile) [1664484]
- [mm] arm64/dma-mapping: Mildly optimise non-coherent IOMMU ops (Don Dutile) [1664484]
- [iommu] iommu: Add fast hook for getting DMA domains (Don Dutile) [1664484]
- [iommu] iommu: Remove the ->map_sg indirection (Don Dutile) [1664484]
- [iommu] kernel/dma: remove unsupported gfp_mask parameter from dma_alloc_from_contiguous() (Don Dutile) [1664484]
- [mm] mm/cma: remove unsupported gfp_mask parameter from cma_alloc() (Don Dutile) [1664484]
- [kernel] dma-mapping: move the remap helpers to a separate file (Don Dutile) [1664484]
- [include] dma-mapping: fix return type of dma_set_max_seg_size() (Don Dutile) [1664484]
- [include] dma-mapping: translate __GFP_NOFAIL to DMA_ATTR_NO_WARN (Don Dutile) [1664484]
- [include] dma-debug: Check for drivers mapping invalid addresses in dma_map_single() (Don Dutile) [1664484]
- [base] dma-mapping: make the get_required_mask method available unconditionally (Don Dutile) [1664484]
- [xen] dma-mapping: support non-coherent devices in dma_common_get_sgtable (Don Dutile) [1664484]
- [kernel] dma-mapping: consolidate the dma mmap implementations (Don Dutile) [1664484]
- [kernel] dma-mapping: merge direct and noncoherent ops (Don Dutile) [1664484]
- [include] dma-mapping: move the dma_coherent flag to struct device (Don Dutile) [1664484]
- [include] dma-mapping: remove dma_deconfigure (Don Dutile) [1664484]
- [base] dma-mapping: remove dma_configure (Don Dutile) [1664484]
- [include] dma-mapping: relax warning for per-device areas (Don Dutile) [1664484]
- [kernel] dma-mapping: add the missing ARCH_HAS_SYNC_DMA_FOR_CPU_ALL declaration (Don Dutile) [1664484]
- [kernel] dma-noncoherent: add a arch_sync_dma_for_cpu_all hook (Don Dutile) [1664484]
- [block] deprecate elevator= kernel parameter (Jeff Moyer) [1665295]
- [rpmspec] kernel.spec: disable kabi checks until RC (=?UTF-8?q?=C4=8Cestm=C3=ADr=20Kalina?=) [1671007]
- [iommu] iommu/amd: Unmap all mapped pages in error path of map_sg (Jerry Snitselaar) [1668448]
- [iommu] iommu/amd: Call free_iova_fast with pfn in map_sg (Jerry Snitselaar) [1668448]

* Thu Feb 07 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-66.el8]
- [arm64] arm64, vmcoreinfo : Append 'MAX_PHYSMEM_BITS' to vmcoreinfo (Bhupesh Sharma) [1666679]
- [kernel] sched/debug: Initialize sd_sysctl_cpus if !CONFIG_CPUMASK_OFFSTACK (Joe Lawrence) [1667840]
- [init] Small change to the message about certified hardware (Steve Best) [1671765]
- [x86] x86/kdump: make the behavior of crashkernel=X consistent with kaslr (Pingfan Liu) [1640799]
- [x86] Add back support for Intel processors (Steve Best) [1670529]
- [net] SUNRPC: Clean up initialisation of the struct rpc_rqst (Benjamin Coddington) [1650494]
- [x86] KABI, x86/paravirt: Protect paravirt ops structures (Waiman Long) [1669957]
- [include] KABI: struct module padding (Prarit Bhargava) [1669480]
- [include] KABI: struct stack_trace_struct padding (Prarit Bhargava) [1669480]
- [documentation] iommu: Fix passthrough option documentation (Gary Hook) [1658391]
- [iommu] iommu: Add config option to set passthrough as default (Gary Hook) [1658391]
- [kernel] redhat: kernel: clean up taint flags (Jiri Benc) [1654313]

* Wed Feb 06 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-65.el8]
- [scsi] scsi: qedi: Add the CRC size within iSCSI NVM image (Charles Rose) [1670186]
- [fs] iomap: don't search past page end in iomap_is_partially_uptodate (Eric Sandeen) [1657588]
- [netdrv] cxgb4: update supported DCB version (Arjun Vynipadath) [1668571]
- [x86] kexec, KEYS: Make use of platform keyring for signature verify (Kairui Song) [1640486]
- [security] integrity, KEYS: add a reference to platform keyring (Kairui Song) [1640486]
- [security] efi: Allow the "db" UEFI variable to be suppressed (Kairui Song) [1640486]
- [security] efi: Import certificates from UEFI Secure Boot (Kairui Song) [1640486]
- [security] efi: Add an EFI signature blob parser (Kairui Song) [1640486]
- [include] efi: Add EFI signature data types (Kairui Song) [1640486]
- [security] integrity: Load certs to the platform keyring (Kairui Song) [1640486]
- [security] integrity: Define a trusted platform keyring (Kairui Song) [1640486]
- [security] security/integrity: remove unnecessary 'init_keyring' variable (Kairui Song) [1640486]
- [x86] Fix kexec forbidding kernels signed with keys in the secondary keyring to boot (Kairui Song) [1640486]
- [crypto] Replace magic for trusting the secondary keyring with #define (Kairui Song) [1640486]
- [acpi] acpi/nfit: Fix command-supported detection (Jeff Moyer) [1665812]
- [acpi] acpi/nfit: Block function zero DSMs (Jeff Moyer) [1665812]
- [md] dm: add missing trace_block_split() to __split_and_process_bio() (Mike Snitzer) [1645283]
- [md] dm: fix dm_wq_work() to only use __split_and_process_bio() if appropriate (Mike Snitzer) [1645283]
- [md] dm: fix redundant IO accounting for bios that need splitting (Mike Snitzer) [1645283]
- [md] dm: fix clone_bio() to trigger blk_recount_segments() (Mike Snitzer) [1645283]
- [block] block: cover another queue enter recursion via BIO_QUEUE_ENTERED (Mike Snitzer) [1645283]
- [md] dm thin: fix passdown_double_checking_shared_status() (Mike Snitzer) [1668039]
- [tools] bpftool: Fix prog dump by tag (Jiri Olsa) [1667305]
- [arm64] arm64: ftrace: Fix to enable syscall events on arm64 (Don Dutile) [1668035]
- [arm64] arm64: implement syscall wrappers (Don Dutile) [1668035]
- [arm64] arm64: convert compat wrappers to C (Don Dutile) [1668035]
- [arm64] arm64: use SYSCALL_DEFINE6() for mmap (Don Dutile) [1668035]
- [arm64] arm64: use {COMPAT,}SYSCALL_DEFINE0 for sigreturn (Don Dutile) [1668035]
- [arm64] arm64: remove in-kernel call to sys_personality() (Don Dutile) [1668035]
- [include] kernel: add ksys_personality() (Don Dutile) [1668035]
- [arm64] arm64: drop alignment from syscall tables (Don Dutile) [1668035]
- [arm64] arm64: entry: remove unused register aliases (Don Dutile) [1668035]
- [arm64] arm64: convert native/compat syscall entry to C (Don Dutile) [1668035]
- [arm64] arm64: svc: Ensure hardirq tracing is updated before return (Don Dutile) [1668035]
- [arm64] arm64: convert syscall trace logic to C (Don Dutile) [1668035]
- [arm64] arm64: move sve_user_{enable,disable} to <asm/fpsimd.h> (Don Dutile) [1668035]
- [arm64] arm64: kill change_cpacr() (Don Dutile) [1668035]
- [arm64] arm64: convert raw syscall invocation to C (Don Dutile) [1668035]
- [arm64] arm64: introduce syscall_fn_t (Don Dutile) [1668035]
- [arm64] arm64: remove sigreturn wrappers (Don Dutile) [1668035]
- [arm64] arm64: rseq: Implement backend rseq calls and select HAVE_RSEQ (Don Dutile) [1668035]
- [sound] ALSA: usb-audio: Add vendor and product name for Dell WD19 Dock (Jaroslav Kysela) [1664249]
- [infiniband] IB/hfi1: Fix an out-of-bounds access in get_hw_stats (Alex Estrin) [1667104]
- [infiniband] IB/hfi1: Incorrect sizing of sge for PIO will OOPs (Alex Estrin) [1667095]
- [drm] drm/nouveau: register backlight on pascal and newer (Ben Skeggs) [1664899]
- [drm] drm/nouveau/disp/gm200-: enforce identity-mapped SOR assignment for LVDS/eDP panels (Ben Skeggs) [1664899]
- [drm] drm/nouveau/disp: move eDP panel power handling (Ben Skeggs) [1664899]
- [drm] drm/nouveau/devinit: don't fail when PMU/PRE_OS is missing from VBIOS (Ben Skeggs) [1664899]
- [kernel] locking/rwsem: Fix (possible) missed wakeup (Waiman Long) [1668014]
- [kernel] futex: Fix (possible) missed wakeup (Waiman Long) [1668014]
- [kernel] sched/wake_q: Fix wakeup ordering for wake_q (Waiman Long) [1668014]
- [kernel] sched/wake_q: Document wake_q_add() (Waiman Long) [1668014]
- [kernel] sched/wait: Fix rcuwait_wake_up() ordering (Waiman Long) [1668014]
- [kernel] sched/Documentation: Update wake_up() & co. memory-barrier guarantees (Waiman Long) [1668014]
- [kvm] KVM: PPC: Book3S HV: Flush guest mappings when turning dirty tracking on/off (Laurent Vivier) [1650386]
- [kvm] KVM: PPC: Book3S HV: Cleanups - constify memslots, fix comments (Laurent Vivier) [1650386]
- [kvm] KVM: PPC: Book3S HV: Map single pages when doing dirty page logging (Laurent Vivier) [1650386]
- [kvm] KVM: PPC: Pass change type down to memslot commit function (Laurent Vivier) [1650386]
- [vhost] vhost: log dirty page correctly (Jason Wang) [1657578]
- [netdrv] netxen: taint as unsupported in RHEL8 (Tony Camuso) [1654825]
- [hid] HID: hiddev: fix potential Spectre v1 (Benjamin Tissoires) [1664611]
- [net] resort to custom code for sk_buff padding (Paolo Abeni) [1665984]
- [net] add padding to cipher_context (Paolo Abeni) [1665984]
- [net] add padding to tls_crypto_context (Paolo Abeni) [1665984]
- [net] add padding to ipv4_devconf (Paolo Abeni) [1665984]
- [net] ip6mr: Fix potential Spectre v1 vulnerability (Stefano Brivio) [1663472]
- [net] ipv4: Fix potential Spectre v1 vulnerability (Stefano Brivio) [1663472]
- [include] add KABI padding to file_system_type (Eric Sandeen) [1665320 1650565]
- [include] add KABI padding to multiple fs ops vectors (Eric Sandeen) [1665320]
- [fs] add KABI padding to dentry structure (Eric Sandeen) [1665320]
- [fs] add KABI padding to inode structure (Eric Sandeen) [1665320]
- [include] add KABI padding to file_lock structure (Eric Sandeen) [1665320]
- [include] KABI: add an iopoll method to struct file_operations (Eric Sandeen) [1665320]
- [sound] ALSA: emux: Fix potential Spectre v1 vulnerabilities (Jaroslav Kysela) [1663477]
- [sound] ALSA: pcm: Fix potential Spectre v1 vulnerability (Jaroslav Kysela) [1663477]
- [sound] ALSA: rme9652: Fix potential Spectre v1 vulnerability (Jaroslav Kysela) [1663477]
- [sound] ALSA: emu10k1: Fix potential Spectre v1 vulnerabilities (Jaroslav Kysela) [1663477]
- [powerpc] powerpc/tm: Unset MSR[TS] if not recheckpointing (Gustavo Duarte) [1663853]
- [netdrv] r8152: Add support for MAC address pass through on RTL8153-BND (Perry Yuan) [1658433]
- [hid] HID: debug: fix the ring buffer implementation (Tony Camuso) [1669469] {CVE-2019-3819}

* Wed Jan 23 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-64.el8]
- [netdrv] net: hns: Fix WARNING when hns modules installed (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Fix ping failed when use net bridge and send multicast (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Add mac pcs config when enable|disable mac (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Fix ntuple-filters status error. (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Free irq when exit from abnormal branch (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Clean rx fbd when ae stopped. (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Some registers use wrong address according to the datasheet. (Xiaojun Tan) [1662120]
- [netdrv] net: hns: All ports can not work when insmod hns ko after rmmod. (Xiaojun Tan) [1662120]
- [netdrv] net: hns: Incorrect offset address used for some registers. (Xiaojun Tan) [1662120]
- [include] ipmi: RH_KABI macros to pad kabi exposed structs (Tony Camuso) [1658175]
- [scsi] reserve space in structures for KABI (Ewan Milne) [1664397]

* Sat Jan 19 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-63.el8]
- [include] PCI: Add reserved fields to 'struct hotplug_slot' (Myron Stowe) [1663534]
- [include] PCI: Add reserved fields to 'struct hotplug_slot_ops' (Myron Stowe) [1663534]
- [pci] PCI: Add reserved fields to 'struct pci_sriov' (Myron Stowe) [1663534]
- [include] PCI: Add reserved fields to 'struct pci_driver' (Myron Stowe) [1663534]
- [include] PCI: Add reserved fields to 'struct pci_bus' (Myron Stowe) [1663534]
- [include] PCI: Add reserved fields, and extension, to 'struct pci_dev' (Myron Stowe) [1663534]
- [pci] PCI: Add missing include to drivers/pci.h (Myron Stowe) [1663534]
- [pci] PCI/IOV: Use VF0 cached config space size for other VFs (Myron Stowe) [1663534]
- [include] PCI: always include 'p2pdma' in 'struct pci_dev' (Myron Stowe) [1663534]
- [ata] PCI: Remove pci_set_dma_max_seg_size() (Myron Stowe) [1663534]
- [pci] PCI: Remove pci_set_dma_seg_boundary() (Myron Stowe) [1663534]
- [include] PCI: Remove pci_unmap_addr() wrappers for DMA API (Myron Stowe) [1663534]
- [pci] PCI/AER: Abstract AER interrupt handling (Myron Stowe) [1663534]
- [pci] PCI: Uninline PCI bus accessors for better ftracing (Myron Stowe) [1663534]
- [pci] PCI/portdrv: Add runtime PM hooks for port service drivers (Myron Stowe) [1663534]
- [pci] PCI: Make link active reporting detection generic (Myron Stowe) [1663534]
- [block] block: don't lose track of REQ_INTEGRITY flag (Ming Lei) [1665684]
- [nvme] nvme-pci: fix nvme_setup_irqs() (Ming Lei) [1661439]
- [lib] sbitmap: Protect swap_lock from hardirq (Ming Lei) [1666192]
- [lib] sbitmap: Protect swap_lock from softirqs (Ming Lei) [1666192]
- [scsi] scsi: isci: initialize shost fully before calling scsi_add_host() (Ming Lei) [1664918]
- [nvme] nvmet-fc: Mark NVMe/FC target mode driver as unsupported (Ewan Milne) [1664838]
- [netdrv] bnx2x: Assign unique DMAE channel number for FW DMAE transactions. (Jonathan Toppins) [1638306]
- [fs] block: don't use un-ordered __set_current_state(TASK_UNINTERRUPTIBLE) (Ming Lei) [1664580]
- [netdrv] qed: Wait for ready indication before rereading the shmem (Chad Dupuis) [1652417]
- [netdrv] qed: Avoid sending mailbox commands when MFW is not responsive (Chad Dupuis) [1652417]
- [netdrv] qed: Wait for MCP halt and resume commands to take place (Chad Dupuis) [1652417]
- [netdrv] qed: Prevent a possible deadlock during driver load and unload (Chad Dupuis) [1652417]
- [fs] gfs2: Fix loop in gfs2_rbm_find (Andreas Grunbacher) [1658528]
- [fs] gfs2: Get rid of potential double-freeing in gfs2_create_inode (Andreas Grunbacher) [1658539]

* Thu Jan 17 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-62.el8]
- [vhost] vhost/vsock: fix vhost vsock cid hashing inconsistent (Stefan Hajnoczi) [1619848] {CVE-2018-14625}
- [vhost] vhost/vsock: fix use-after-free in network stack callers (Stefan Hajnoczi) [1619848] {CVE-2018-14625}
- [netdrv] bnx2x: Add VF spoof-checking configuration (Jonathan Toppins) [1646842]
- [netdrv] net-next: hinic: fix a problem in free_tx_poll() (Xiaojun Tan) [1642016]
- [netdrv] net: hns: fix for unmapping problem when SMMU is on (Xiaojun Tan) [1640526]
- [netdrv] net: hns: add netif_carrier_off before change speed and duplex (Xiaojun Tan) [1640526]
- [netdrv] net: hns: add the code for cleaning pkt in chip (Xiaojun Tan) [1640526]
- [netdrv] net: hns: modify variable type in hns_nic_reuse_page (Xiaojun Tan) [1640526]

* Wed Jan 16 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-61.el8]
- [irqchip] Mark GICv2 deprecated (Wei Huang) [1609391]
- [scsi] qla2xxx: Use correct number of vectors for online CPUs (Himanshu Madhani) [1644058]
- [scsi] megaraid_sas: mark Aero controllers as tech preview (Tomas Henzl) [1659972]
- [scsi] megaraid_sas: add retry logic in megasas_readl (Tomas Henzl) [1659972]
- [scsi] scsi: megaraid_sas: Introduce new Aero adapter type (Tomas Henzl) [1659972]
- [scsi] scsi: megaraid_sas: Fix Ventura series based checks (Tomas Henzl) [1659972]
- [scsi] scsi: libfc: retry PRLI if we cannot analyse the payload (Chris Leech) [1631843]
- [scsi] scsi: libfc: check fc_frame_payload_get() return value for null (Chris Leech) [1631843]
- [scsi] scsi: libfc: hold disc_mutex in fc_disc_stop_rports() (Chris Leech) [1631843]
- [scsi] scsi: libfc: fixup lockdep annotations (Chris Leech) [1631843]
- [scsi] scsi: libfc: fixup 'sleeping function called from invalid context' (Chris Leech) [1631843]
- [scsi] scsi: libfc: Add lockdep annotations (Chris Leech) [1631843]
- [md] dm crypt: fix parsing of extended IV arguments (Mike Snitzer) [1665290]
- [kernel] redhat: kabi: reserved padding for kernel sched data structures (Rafael Aquini) [1664858]
- [kernel] redhat: kabi: reserved padding for MM related data structures (Rafael Aquini) [1664858]
- [vfio] vfio/type1: Fix unmap overflow off-by-one (Alex Williamson) [1662291]
- [message] mptspi: pci-id table changes (Tomas Henzl) [1651803]
- [message] mptspi: Taint kernel if mptspi is loaded (Tomas Henzl) [1651803]
- [block] kabi: reserve space for public data structure (Ming Lei) [1551939]
- [block] kabi: reserve space for blk-mq related structure (Ming Lei) [1551939]
- [block] kabi: reserve space for bsg related structure (Ming Lei) [1551939]
- [block] kabi: reserve space for integrity related structure (Ming Lei) [1551939]
- [block] kabi: reserve space for CONFIG_BLK_DEV_ZONED (Ming Lei) [1551939]
- [ata] ata: Disable AHCI ALPM feature for Ampere Computing eMAG SATA (David Milburn) [1663347]
- [kvm] KVM: x86: Add CPUID support for new instruction WBNOINVD (Andrew Jones) [1659491]
- [x86] KVM: x86: Use jmp to invoke kvm_spurious_fault() from .fixup (Andrew Jones) [1659491]
- [virt] kvm: Change offset in kvm_write_guest_offset_cached to unsigned (Andrew Jones) [1659491]
- [virt] kvm: Disallow wraparound in kvm_gfn_to_hva_cache_init (Andrew Jones) [1659491]
- [kvm] KVM: x86: svm: report MSR_IA32_MCG_EXT_CTL as unsupported (Andrew Jones) [1659491]
- [virt] arm/arm64: KVM: Add ARM_EXCEPTION_IS_TRAP macro (Andrew Jones) [1659491]
- [arm64] arm64: KVM: Avoid setting the upper 32 bits of VTCR_EL2 to 1 (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: Fix unintended stage 2 PMD mappings (Andrew Jones) [1659491]
- [virt] arm/arm64: KVM: vgic: Force VM halt when changing the active state of GICv3 PPIs/SGIs (Andrew Jones) [1659491]
- [arm64] KVM: arm/arm64: Fixup the kvm_exit tracepoint (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: vgic: Consider priority and active state for pending irq (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: vgic: Fix off-by-one bug in vgic_get_irq() (Andrew Jones) [1659491]
- [kvm] KVM: X86: Fix NULL deref in vcpu_scan_ioapic (Andrew Jones) [1659491]
- [kvm] KVM: Fix UAF in nested posted interrupt processing (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: vgic: Cap SPIs to the VM-defined maximum (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: vgic: Do not cond_resched_lock() with IRQs disabled (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: vgic-v2: Set active_source to 0 when restoring state (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: Fix VMID alloc race by reverting to lock-less (Andrew Jones) [1659491]
- [kvm] KVM: nVMX: Free the VMREAD/VMWRITE bitmaps if alloc_kvm_area() fails (Andrew Jones) [1659491]
- [kvm] arm64: KVM: Install stage-2 translation before enabling traps (Andrew Jones) [1659491]
- [kvm] arm64: KVM: Make VHE Stage-2 TLB invalidation operations non-interruptible (Andrew Jones) [1659491]
- [arm64] arm64: entry: Remove confusing comment (Andrew Jones) [1659491]
- [kvm] arm64: entry: Place an SB sequence following an ERET instruction (Andrew Jones) [1659491]
- [arm64] arm64: Add support for SB barrier and patch in over DSB; ISB sequences (Andrew Jones) [1659491]
- [kvm] kvm: nVMX: Set VM instruction error for VMPTRLD of unbacked page (Andrew Jones) [1659491]
- [kvm] kvm: svm: Ensure an IBPB on all affected CPUs when freeing a vmcb (Andrew Jones) [1659491]
- [kvm] kvm: mmu: Fix race in emulated page table writes (Andrew Jones) [1659491]
- [kvm] KVM: nVMX/nSVM: Fix bug which sets vcpu->arch.tsc_offset to L1 tsc_offset (Andrew Jones) [1659491]
- [kvm] KVM: VMX: Update shared MSRs to be saved/restored on MSR_EFER.LMA changes (Andrew Jones) [1659491]
- [kvm] KVM: x86: Fix kernel info-leak in KVM_HC_CLOCK_PAIRING hypercall (Andrew Jones) [1659491]
- [kvm] svm: Add mutex_lock to protect apic_access_page_done on AMD systems (Andrew Jones) [1659491]
- [kvm] KVM/nVMX: Do not validate that posted_intr_desc_addr is page aligned (Andrew Jones) [1659491]
- [kvm] KVM: arm64: Safety check PSTATE when entering guest and handle IL (Andrew Jones) [1659491]
- [virt] KVM: arm64: Fix caching of host MDCR_EL2 value (Andrew Jones) [1659491]
- [kvm] x86/kvm/nVMX: allow bare VMXON state migration (Andrew Jones) [1659491]
- [kvm] x86/kvm/lapic: preserve gfn_to_hva_cache len on cache reinit (Andrew Jones) [1659491]
- [kvm] KVM: hyperv: define VP assist page helpers (Andrew Jones) [1659491]
- [kvm] KVM: nVMX: move check_vmentry_postreqs() call to nested_vmx_enter_non_root_mode() (Andrew Jones) [1659491]
- [kvm] KVM: nVMX: Always reflect #NM VM-exits to L1 (Andrew Jones) [1659491]
- [kvm] KVM: x86: hyperv: consistently use 'hv_vcpu' for 'struct kvm_vcpu_hv' variables (Andrew Jones) [1659491]
- [kvm] KVM: x86: hyperv: enforce vp_index < KVM_MAX_VCPUS (Andrew Jones) [1659491]
- [kvm] KVM: nVMX: restore host state in nested_vmx_vmexit for VMFail (Andrew Jones) [1659491]
- [kvm] KVM: nVMX: Clear reserved bits of #DB exit qualification (Andrew Jones) [1659491]
- [virt] KVM: arm/arm64: Ensure only THP is candidate for adjustment (Andrew Jones) [1659491]
- [kvm] x86: kvm: avoid unused variable warning (Andrew Jones) [1659491]
- [kvm] powerpc64/ftrace: Include ftrace.h needed for enable/disable calls (Andrew Jones) [1659491]
- [kvm] x86/kvm/vmx: Remove duplicate l1d flush definitions (Andrew Jones) [1659491]
- [tools] perf kvm: Fix subcommands on s390 (Andrew Jones) [1659491]
- [arm64] arm64: add PSR_AA32_* definitions (Andrew Jones) [1659491]
- [pci] PCI: hotplug: Document TODOs (Myron Stowe) [1664454]
- [pci] PCI: hotplug: Embed hotplug_slot (Myron Stowe) [1664454]
- [pci] PCI: hotplug: Drop hotplug_slot_info (Myron Stowe) [1664454]
- [pci] PCI: hotplug: Constify hotplug_slot_ops (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Reshuffle controller struct for clarity (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Rename controller struct members for clarity (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Unify controller and slot structs (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Tolerate Presence Detect hardwired to zero (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Drop hotplug_slot_ops wrappers (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Drop unnecessary includes (Myron Stowe) [1664454]
- [pci] PCI: pciehp: Differentiate between surprise and safe removal (Myron Stowe) [1664454]
- [pci] PCI: Simplify disconnected marking (Myron Stowe) [1664454]
- [tools] perf vendor events arm64: Revise core JSON events for eMAG (Jiri Olsa) [1663353]
- [tools] perf vendor events arm64: Enable JSON events for eMAG (Jiri Olsa) [1663353]
- [perf] drivers/perf: xgene: Add CPU hotplug support (Jiri Olsa) [1663349]
- [scsi] mpt3sas: mark Aero controllers as tech preview (Tomas Henzl) [1663281]
- [powerpc] KVM: PPC: Book3S HV: Keep rc bits in shadow pgtable in sync with host (Suraj Jitindar Singh) [1662029]
- [powerpc] KVM: PPC: Book3S HV: Introduce kvmhv_update_nest_rmap_rc_list() (Suraj Jitindar Singh) [1662029]
- [powerpc] KVM: PPC: Book3S HV: Apply combination of host and l1 pte rc for nested guest (Suraj Jitindar Singh) [1662029]
- [powerpc] KVM: PPC: Book3S HV: Align gfn to L1 page size when inserting nest-rmap entry (Suraj Jitindar Singh) [1662029]
- [powerpc] KVM: PPC: Book3S HV: Hold kvm->mmu_lock across updating nested pte rc bits (Suraj Jitindar Singh) [1662029]
- [tools] perf python: Do not force closing original perf descriptor in evlist.get_pollfd (Jiri Olsa) [1659445]
- [mm] mm: thp: relax __GFP_THISNODE for MADV_HUGEPAGE mappings (Andrea Arcangeli) [1613993]
- [rpmspec] spec: Add libperf-jvmti.so into perf debuginfo rpm (Jiri Olsa) [1653570]
- [scsi] scsi: hisi_sas: Fix spin lock management in slot_index_alloc_quirk_v2_hw() (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: Update v3 hw AIP_LIMIT and CFG_AGING_TIME register values (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: Use block layer tag instead for IPTT (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: unmask interrupts ent72 and ent74 (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: Free slot later in slot_complete_vx_hw() (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: Fix the race between IO completion and timeout for SMP/internal IO (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: Move evaluation of hisi_hba in hisi_sas_task_prep() (Xiaojun Tan) [1642819]
- [scsi] scsi: hisi_sas: Feed back linkrate(max/min) when re-attached (Xiaojun Tan) [1642819]
- [hwtracing] intel_th: pci: Add Ice Lake PCH support (Jiri Olsa) [1485529]

* Fri Jan 11 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-60.el8]
- [kernel] userns: also map extents in the reverse map to kernel IDs (Chris von Recklinghausen) [1652679] {CVE-2018-18955}
- [net] ipv6: route: Fix return value of ip6_neigh_lookup() on neigh_create() error (Stefano Brivio) [1662789]
- [net] ipv6: frags: Fix bogus skb->sk in reassembled packets (Herbert Xu) [1645839]
- [net] redhat: blacklist auto-loadable net modules in modules-extra (Marcelo Leitner) [1642795]
- [net] redhat: move sctp modules to kernel-modules-extra (Marcelo Leitner) [1642795]
- [net] add reserved fields to neighbour (Paolo Abeni) [1655084]
- [net] add reserved fields to rtnl_link_stats* (Paolo Abeni) [1655084]
- [net] reserve bits in netdev_features_t for future features (Paolo Abeni) [1655084]
- [net] add reserved fields to sk_buff (Paolo Abeni) [1655084]
- [net] add reserved fields to ipv6_devconf (Paolo Abeni) [1655084]
- [net] add reserved fields to fib_rule (Paolo Abeni) [1655084]
- [net] add reserved fields to sock (Paolo Abeni) [1655084]
- [net] add reserved fields to genl_family (Paolo Abeni) [1655084]
- [net] add reserved fields to proto_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to proto (Paolo Abeni) [1655084]
- [net] add reserved fields to genl_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to dst_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to dst_entry (Paolo Abeni) [1655084]
- [net] add reserved fields to lwtunnel_state (Paolo Abeni) [1655084]
- [net] add reserved fields to packet_type (Paolo Abeni) [1655084]
- [net] add reserved fields to napi_struct (Paolo Abeni) [1655084]
- [net] add reserved fields to net_device (Paolo Abeni) [1655084]
- [net] exclude wireless_dev from KABI protection (Paolo Abeni) [1655084]
- [net] add reserved fields to dcbnl_rtnl_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to xfrm_* (Paolo Abeni) [1655084]
- [net] add reserved fields to switchdev_obj (Paolo Abeni) [1655084]
- [net] add reserved fields to switchdev_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to l3mdev_ops (Paolo Abeni) [1655084]
- [net] exclude ndisc_ops from kABI protection (Paolo Abeni) [1655084]
- [net] add reserved fields to xfrmdev_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to tlsdev_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to netdev_rx_queue (Paolo Abeni) [1655084]
- [net] add reserved fields to netdev_queue (Paolo Abeni) [1655084]
- [net] add reserved fields to rtnl_link_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to ethtool_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to header_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to net_device_ops (Paolo Abeni) [1655084]
- [net] add reserved fields to flowi* structs (Paolo Abeni) [1655084]
- [arm64] KVM: arm64: Clarify explanation of STAGE2_PGTABLE_LEVELS (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] KVM: arm/arm64: Rename kvm_arm_config_vm to kvm_arm_setup_stage2 (Christoph von Recklinghausen) [1643586 1643522]
- [virt] KVM: arm64: Drop __cpu_init_stage2 on the VHE path (Christoph von Recklinghausen) [1643586 1643522]
- [kvm] kvm: arm64: Allow tuning the physical address size for VM (Christoph von Recklinghausen) [1643586 1643522]
- [kvm] kvm: arm64: Limit the minimum number of page table levels (Christoph von Recklinghausen) [1643586 1643522]
- [virt] kvm: arm64: Set a limit on the IPA size (Christoph von Recklinghausen) [1643586 1643522]
- [kvm] kvm: arm64: Add 52bit support for PAR to HPFAR conversoin (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] kvm: arm64: Switch to per VM IPA limit (Christoph von Recklinghausen) [1643586 1643522]
- [kvm] kvm: arm64: Configure VTCR_EL2.SL0 per VM (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] kvm: arm64: Dynamic configuration of VTTBR mask (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] kvm: arm64: Make stage2 page table layout dynamic (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] kvm: arm64: Prepare for dynamic stage2 page table layout (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] kvm: arm/arm64: Prepare for VM specific stage2 translations (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] kvm: arm64: Configure VTCR_EL2 per VM (Christoph von Recklinghausen) [1643586 1643522]
- [virt] kvm: arm/arm64: Allow arch specific configurations for VM (Christoph von Recklinghausen) [1643586 1643522]
- [kvm] kvm: arm64: Clean up VTCR_EL2 initialisation (Christoph von Recklinghausen) [1643586 1643522]
- [arm64] arm64: Add a helper for PARange to physical shift conversion (Christoph von Recklinghausen) [1643586 1643522]
- [kvm] kvm: arm64: Add helper for loading the stage2 setting for a VM (Christoph von Recklinghausen) [1643586 1643522]
- [virt] kvm: arm/arm64: Remove spurious WARN_ON (Christoph von Recklinghausen) [1643586 1643522]
- [virt] kvm: arm/arm64: Fix stage2_flush_memslot for 4 level page table (Christoph von Recklinghausen) [1643586 1643522]
- [hv] hv_balloon: avoid touching uninitialized struct page during tail onlining (Vitaly Kuznetsov) [1662277]
- [x86] Mark AMD EPYC guests as supported (David Arcari) [1663356]
- [netdrv] be2net: Disable queue dump in be_tx_timeout handler (Petr Oros) [1646838]
- [vhost] vhost: Fix Spectre V1 vulnerability (Jason Wang) [1663469]
- [mm] mm/hugetlb.c: teach follow_hugetlb_page() to handle FOLL_NOWAIT (Andrea Arcangeli) [1575028]
- [tools] cpupower: Fix AMD Family 0x17 msr_pstate size (Prarit Bhargava) [1659883]
- [tools] cpupower: Fix coredump on VMWare (Prarit Bhargava) [1659883]
- [scsi] scsi: csiostor: remove flush_scheduled_work() (Arjun Vynipadath) [1663973]
- [powerpc] KVM: PPC: Book3S HV: Fix race between kvm_unmap_hva_range and MMU mode switch (David Gibson) [1663225]
- [fs] userfaultfd: check VM_MAYWRITE was set after verifying the uffd is registered (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [mm] userfaultfd: shmem: UFFDIO_COPY: set the page dirty if VM_WRITE is not set (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [mm] userfaultfd: shmem: add i_size checks (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [mm] userfaultfd: shmem/hugetlbfs: only allow to register VM_MAYWRITE vmas (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [mm] userfaultfd: shmem: allocate anonymous memory for MAP_PRIVATE shmem (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [mm] userfaultfd: use ENOENT instead of EFAULT if the atomic copy user fails (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [mm] userfaultfd: allow get_mempolicy(MPOL_F_NODE|MPOL_F_ADDR) to trigger userfaults (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [fs] userfaultfd: clear flag if remap event not enabled (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [fs] userfaultfd: disable irqs when taking the waitqueue lock (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [fs] fs/userfaultfd.c: remove redundant pointer uwq (Andrea Arcangeli) [1657615] {CVE-2018-18397}
- [fs] NFS: nfs_compare_mount_options always compare auth flavors. (Steve Dickson) [1661619]
- [infiniband] RDMA/hns: Bugfix for RoCE loopback test (Xiaojun Tan) [1663359]
- [infiniband] RDMA/hns: Update posting & querying mailbox (Xiaojun Tan) [1663359]
- [infiniband] RDMA/hns: Fix the bug while use multi-hop of pbl (Xiaojun Tan) [1663359]
- [infiniband] RDMA/hns: Init qp context when modify qp from reset to init (Xiaojun Tan) [1663359]
- [infiniband] RDMA/hns: Bugfix pbl configuration for rereg mr (Xiaojun Tan) [1663359]
- [security] selinux: add support for RTM_NEWCHAIN, RTM_DELCHAIN, and RTM_GETCHAIN (Ondrej Mosnacek) [1660564]
- [scsi] scsi: megaraid_sas: driver version update (Tomas Henzl) [1656261]
- [scsi] scsi: megaraid_sas: Use 63-bit DMA addressing (Tomas Henzl) [1656261]
- [x86] x86/kvm: mark as TechPreview when running as a nested hypervisor (Vitaly Kuznetsov) [1519039]
- [rpmspec] kernel.spec: Fix kernel-tools files section logic (Prarit Bhargava) [1661247]
- [crypto] crypto: ccp - Make function sev_get_firmware() static (Gary Hook) [1632894]
- [crypto] crypto: ccp - Allow SEV firmware to be chosen based on Family and Model (Gary Hook) [1632894]
- [crypto] crypto: ccp - Fix static checker warning (Gary Hook) [1632894]
- [crypto] crypto: ccp - add timeout support in the SEV command (Gary Hook) [1632894]
- [nvdimm] nvdimm: Use namespace index data to reduce number of label reads needed (Jeff Moyer) [1634345]
- [nvdimm] nvdimm: Split label init out from the logic for getting config data (Jeff Moyer) [1634345]
- [nvdimm] nvdimm: Remove empty if statement (Jeff Moyer) [1634345]
- [nvdimm] nvdimm: Clarify comment in sizeof_namespace_index (Jeff Moyer) [1634345]
- [nvdimm] nvdimm: Sanity check labeloff (Jeff Moyer) [1634345]
- [nvdimm] libnvdimm, dimm: Maximize label transfer size (Jeff Moyer) [1634345]
- [mm] mm/page-writeback.c: fix range_cyclic writeback vs writepages deadlock (Brian Foster) [1659528]
- [input] Input: elantech - disable elan-i2c for P52 and P72 (Benjamin Tissoires) [1658602]
- [fs] cachefiles: avoid deprecated get_seconds() (David Howells) [1655613]
- [fs] fscache, cachefiles: remove redundant variable 'cache' (David Howells) [1655613]
- [fs] cachefiles: Explicitly cast enumerated type in put_object (David Howells) [1655613]
- [fs] fscache: fix race between enablement and dropping of object (David Howells) [1655613]
- [fs] cachefiles: Fix page leak in cachefiles_read_backing_file while vmscan is active (David Howells) [1655613]
- [fs] fscache: Fix race in fscache_op_complete() due to split atomic_sub & read (David Howells) [1655613]
- [fs] cachefiles: Fix an assertion failure when trying to update a failed object (David Howells) [1655613]
- [fs] fscache: Fix out of bound read in long cookie keys (David Howells) [1655613]
- [fs] fscache: Fix incomplete initialisation of inline key space (David Howells) [1655613]
- [fs] cachefiles: fix the race between cachefiles_bury_object() and rmdir(2) (David Howells) [1655613]
- [kernel] ebpf: record usage of eBPF (Jiri Benc) [1654279]
- [kernel] add rh_features to /proc (Jiri Benc) [1654279]
- [kernel] add support for rh_features (Jiri Benc) [1654279]
- [fs] fs/lock: show locks taken by processes from another pidns (Miklos Szeredi) [1616125]
- [iommu] iommu/arm-smmu: Support non-strict mode (Xiaojun Tan) [1643114]
- [iommu] iommu/io-pgtable-arm-v7s: Add support for non-strict mode (Xiaojun Tan) [1643114]
- [iommu] iommu/arm-smmu-v3: Add support for non-strict mode (Xiaojun Tan) [1643114]
- [iommu] iommu/io-pgtable-arm: Add support for non-strict mode (Xiaojun Tan) [1643114]
- [iommu] iommu: Add "iommu.strict" command line option (Xiaojun Tan) [1643114]
- [iommu] iommu/dma: Add support for non-strict mode (Xiaojun Tan) [1643114]
- [iommu] iommu/arm-smmu: Ensure that page-table updates are visible before TLBI (Xiaojun Tan) [1643114]
- [iommu] iommu/arm-smmu-v3: Implement flush_iotlb_all hook (Xiaojun Tan) [1643114]
- [iommu] iommu/arm-smmu-v3: Avoid back-to-back CMD_SYNC operations (Xiaojun Tan) [1643114]
- [iommu] iommu/arm-smmu-v3: Fix unexpected CMD_SYNC timeout (Xiaojun Tan) [1643114]
- [iommu] iommu/io-pgtable-arm: Fix race handling in split_blk_unmap() (Xiaojun Tan) [1643114]
- [infiniband] RDMA/hns: Update some attributes of the RoCE device (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Limit the size of extend sge of sq (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Bugfix for CM test (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Submit bad wr when post send wr exception (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Bugfix for reserved qp number (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Refactor the codes for setting transport opode (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Move all prints out of irq handle (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Fix an error code in hns_roce_v2_init_eq_table() (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Fix usage of bitmap allocation functions return values (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Support flush cqe for hip08 in kernel space (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Program the tclass and flow label into the hardware (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Use macro instead of magic number (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Modify qp will return errno when qp type is illegal (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Assign the value for vlan field of qp context (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Only assgin the fields of the av if IB_QP_AV bit is set (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Enable modify_cq for uverbs. (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Update the data type of immediate data (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Use delay instead of usleep (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Add illegal hop_num judgement (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Add 50GE type of hnae3 device match (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Do not overwrite the error code during error unwind in hns_roce_init (Xiaojun Tan) [1639578]
- [infiniband] hns: Remove a set-but-not-used variable (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Update the implementation of set_mac (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Update the implementation of set_gid (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Add TPQ link table support (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Add TSQ link table support (Xiaojun Tan) [1639578]
- [infiniband] RDMA/hns: Fix endian conversions and annotations (Xiaojun Tan) [1639578]
- [scsi] scsi: hisi_sas: Add SATA FIS check for v3 hw (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: add memory barrier in task delivery function (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Tidy hisi_sas_task_prep() (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Implement handlers of PCIe FLR for v3 hw (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: relocate some common code for v3 hw (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: tidy host controller reset function a bit (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Fix the failure of recovering PHY from STP link timeout (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: tidy channel interrupt handler for v3 hw (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Drop hisi_sas_slot_abort() (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Update a couple of register settings for v3 hw (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Add missing PHY spinlock init (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Pre-allocate slot DMA buffers (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Release all remaining resources in clear nexus ha (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Add a flag to filter PHY events during reset (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Adjust task reject period during host reset (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Fix the conflict between dev gone and host reset (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Only process broadcast change in phy_bcast_v3_hw() (Zhou Wang) [1639541]
- [scsi] scsi: hisi_sas: Use dmam_alloc_coherent() (Zhou Wang) [1639541]
- [netdrv] xen/netfront: fix waiting for xenbus state change (Petr Oros) [1638456]

* Thu Jan 10 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-59.el8]
- [x86] expand cpu feature/bug bits (David Arcari) [1662434]
- [x86] add kabi support for cpuinfo_x86 (David Arcari) [1662434]
- [init] Display a message about certified hardware (Steve Best) [1660523]
- [scsi] scsi: t10-pi: Return correct ref tag when queue has no integrity profile (Ming Lei) [1660719]
- [scsi] scsi: storvsc: Fix a race in sub-channel creation that can cause panic (Mohammed Gamal) [1650149]
- [uio] uio_hv_generic: set callbacks on open (Mohammed Gamal) [1650149]
- [hv] vmbus: fix subchannel removal (Mohammed Gamal) [1650149]
- [uio] uio_hv_generic: defer opening vmbus until first use (Mohammed Gamal) [1650149]
- [hv] vmbus: split ring buffer allocation from open (Mohammed Gamal) [1650149]
- [hv] vmbus: pass channel to hv_process_channel_removal (Mohammed Gamal) [1650149]
- [hv] Drivers: hv: vmbus: Reset the channel callback in vmbus_onoffer_rescind() (Mohammed Gamal) [1650149]
- [uio] hv_uio_generic: map ringbuffer phys addr (Mohammed Gamal) [1650149]
- [uio] uio: introduce UIO_MEM_IOVA (Mohammed Gamal) [1650149]
- [hv] vmbus: add driver_override support (Mohammed Gamal) [1650149]
- [hv] vmbus: keep pointer to ring buffer page (Mohammed Gamal) [1650149]
- [uio] uio_hv_generic: increase size of receive and send buffers (Mohammed Gamal) [1650149]
- [uio] uio: add SPDX license tags (Mohammed Gamal) [1650149]
- [fs] gfs2: take jdata unstuff into account in do_grow (Robert S Peterson) [1660519]
- [drm] drm/dp_mst: Check if primary mstb is null (Lyude Paul) [1658711]
- [tools] perf tests: Use shebangs in the shell scripts (Michael Petlan) [1613523]

* Mon Jan 07 2019 Herton R. Krzesinski <herton@redhat.com> [4.18.0-58.el8]
- [mm] mm: put_and_wait_on_page_locked() while page is migrated (Baoquan He) [1649214]
- [netdrv] i40e: define proper net_device::neigh_priv_len (Stefan Assmann) [1658743]
- [netdrv] i40e: fix VLAN.TCI == 0 RX HW offload (Stefan Assmann) [1658743]
- [netdrv] i40e: fix mac filter delete when setting mac address (Stefan Assmann) [1658743]
- [netdrv] i40e: prevent overlapping tx_timeout recover (Stefan Assmann) [1658743]
- [netdrv] i40e: Use correct shift for VLAN priority (Stefan Assmann) [1658743]
- [netdrv] i40e: always set ks->base.speed in i40e_get_settings_link_up (Stefan Assmann) [1658743]
- [netdrv] i40e: don't restart nway if autoneg not supported (Stefan Assmann) [1658743]
- [netdrv] i40e: enable NETIF_F_NTUPLE and NETIF_F_HW_TC at driver load (Stefan Assmann) [1658743]
- [netdrv] i40e: restore NETIF_F_GSO_IPXIP[46] to netdev features (Stefan Assmann) [1658743]
- [acpi] ACPI/APEI: Clear GHES block_status before panic() (David Arcari) [1662442]
- [misc] VMCI: Resource wildcard match fixed (Vitaly Kuznetsov) [1652868]
- [mm] mm/page_alloc.c: don't call kasan_free_pages() at deferred mem init (Waiman Long) [1655964]
- [block] block/bio: Do not zero user pages (Ming Lei) [1662502]
- [vhost] disable zerocopy by default (Jason Wang) [1582756]
- [block] kyber: use sbitmap add_wait_queue/list_del wait helpers (Ming Lei) [1661426]
- [lib] sbitmap: add helpers for add/del wait queue handling (Ming Lei) [1661426]
- [net] Revert "sunrpc: Ensure we always close the socket after a connection shuts down" (Dave Wysochanski) [1657449]
- [vhost] vhost/vsock: fix reset orphans race with close timeout (Stefan Hajnoczi) [1660445]
- [misc] genwqe: Fix size check (Steve Best) [1660126]
- [fs] aio: fix spectre gadget in lookup_ioctx (Jeff Moyer) [1660963]
- [block] block: save irq state in blkg_lookup_create() (Ming Lei) [1660299]
- [md] dm: don't reuse bio for flushes (Ming Lei) [1660401]
- [wireless] mac80211_hwsim: Fix possible Spectre-v1 for hwsim_world_regdom_custom (Stanislaw Gruszka) [1637113]
- [wireless] nl80211: Fix possible Spectre-v1 for NL80211_TXRATE_HT (Stanislaw Gruszka) [1637113]
- [wireless] nl80211: Fix possible Spectre-v1 for CQM RSSI thresholds (Stanislaw Gruszka) [1637113]
- [block] blk-mq: enable IO poll if .nr_queues of type poll > 0 (Ming Lei) [1660826]
- [powerpc] powerpc/rtas: Fix a potential race between CPU-Offline & Migration (Desnes Augusto Nunes do Rosario) [1639266]
- [x86] kvm: x86: Add AMD's EX_CFG to the list of ignored MSRs (Eduardo Habkost) [1625111]
- [scsi] scsi_sysfs: make unpriv_sgio queue attribute accessible for non-block devices (Paolo Bonzini) [1584504]
- [block] scsi_ioctl: introduce unpriv_sgio queue flag (Paolo Bonzini) [1584504]
- [block] scsi_ioctl: pass request_queue to blk_verify_command (Paolo Bonzini) [1584504]
- [fs] ext4: missing !bh check in ext4_xattr_inode_write() (Lukas Czerner) [1659481]
- [fs] ext4: fix buffer leak in __ext4_read_dirblock() on error path (Lukas Czerner) [1659481]
- [fs] ext4: fix buffer leak in ext4_expand_extra_isize_ea() on error path (Lukas Czerner) [1659481]
- [fs] ext4: fix buffer leak in ext4_xattr_move_to_block() on error path (Lukas Czerner) [1659481]
- [fs] ext4: release bs.bh before re-using in ext4_xattr_block_find() (Lukas Czerner) [1659481]
- [fs] ext4: fix buffer leak in ext4_xattr_get_block() on error path (Lukas Czerner) [1659481]
- [fs] ext4: fix possible leak of s_journal_flag_rwsem in error path (Lukas Czerner) [1659481]
- [fs] ext4: fix possible leak of sbi->s_group_desc_leak in error path (Lukas Czerner) [1659481]
- [fs] ext4: avoid possible double brelse() in add_new_gdb() on error path (Lukas Czerner) [1659481]
- [fs] ext4: avoid buffer leak in ext4_orphan_add() after prior errors (Lukas Czerner) [1659481]
- [fs] ext4: avoid buffer leak on shutdown in ext4_mark_iloc_dirty() (Lukas Czerner) [1659481]
- [fs] ext4: fix possible inode leak in the retry loop of ext4_resize_fs() (Lukas Czerner) [1659481]
- [fs] ext4: fix missing cleanup if ext4_alloc_flex_bg_array() fails while resizing (Lukas Czerner) [1659481]
- [fs] ext4: add missing brelse() update_backups()'s error path (Lukas Czerner) [1659481]
- [fs] ext4: add missing brelse() add_new_gdb_meta_bg()'s error path (Lukas Czerner) [1659481]
- [fs] ext4: add missing brelse() in set_flexbg_block_bitmap()'s error path (Lukas Czerner) [1659481]
- [fs] ext4: avoid potential extra brelse in setup_new_flex_group_blocks() (Lukas Czerner) [1659481]
- [scsi] scsi: lpfc: Enable Management features for IF_TYPE=6 (Dick Kennedy) [1658755]
- [scsi] scsi: mpt3sas: Update driver version to 27.101.00.00 (Tomas Henzl) [1659035]
- [scsi] scsi: mpt3sas: Replace readl with ioc->base_readl (Tomas Henzl) [1659035]
- [scsi] scsi: mpt3sas: Add separate function for aero doorbell reads (Tomas Henzl) [1659035]
- [scsi] scsi: mpt3sas: Introduce flag for aero based controllers (Tomas Henzl) [1659035]
- [md] dm: do not allow readahead to limit IO size (Mike Snitzer) [1658757]
- [md] dm raid: fix false -EBUSY when handling check/repair message (Mike Snitzer) [1658757]
- [block] blk-mq: change blk_mq_queue_busy() to blk_mq_queue_inflight() (Mike Snitzer) [1658757]
- [md] dm rq: cleanup leftover code from recently removed q->mq_ops branching (Mike Snitzer) [1658757]
- [md] dm verity: log the hash algorithm implementation (Mike Snitzer) [1658757]
- [md] dm crypt: log the encryption algorithm implementation (Mike Snitzer) [1658757]
- [md] dm integrity: fix spelling mistake in workqueue name (Mike Snitzer) [1658757]
- [md] dm flakey: Properly corrupt multi-page bios. (Mike Snitzer) [1658757]
- [md] dm: Check for device sector overflow if CONFIG_LBDAF is not set (Mike Snitzer) [1658757]
- [md] dm crypt: use u64 instead of sector_t to store iv_offset (Mike Snitzer) [1658757]
- [md] dm kcopyd: Fix bug causing workqueue stalls (Mike Snitzer) [1658757]
- [md] dm snapshot: Fix excessive memory usage and workqueue stalls (Mike Snitzer) [1658757]
- [md] dm bufio: update comment in dm-bufio.c (Mike Snitzer) [1658757]
- [md] dm writecache: fix typo in error msg for creating writecache_flush_thread (Mike Snitzer) [1658757]
- [md] dm: remove indirect calls from __send_changing_extent_only() (Mike Snitzer) [1658757]
- [md] dm mpath: only flush workqueue when needed (Mike Snitzer) [1658757]
- [md] dm: avoid indirect call in __dm_make_request (Mike Snitzer) [1658757]
- [md] dm thin: bump target version (Mike Snitzer) [1658757]
- [md] dm thin: send event about thin-pool state change _after_ making it (Mike Snitzer) [1658757]
- [md] dm cache metadata: verify cache has blocks in blocks_are_clean_separate_dirty() (Mike Snitzer) [1658757]
- [md] dm writecache: remove disabled code in memory_entry() (Mike Snitzer) [1658757]
- [md] dm raid: avoid bitmap with raid4/5/6 journal device (Mike Snitzer) [1658757]
- [md] dm crypt: make workqueue names device-specific (Mike Snitzer) [1658757]
- [md] dm: add dm_table_device_name() (Mike Snitzer) [1658757]
- [md] dm ioctl: harden copy_params()'s copy_from_user() from malicious users (Mike Snitzer) [1658757]
- [md] dm: remove unnecessary unlikely() around WARN_ON_ONCE() (Mike Snitzer) [1658757]
- [md] dm thin: use refcount_t for thin_c reference counting (Mike Snitzer) [1658757]
- [netdrv] nfp: provide a better warning when ring allocation fails (Pablo Cascon) [1645456]
- [netdrv] nfp: use kvcalloc() to allocate SW buffer descriptor arrays (Pablo Cascon) [1645456]
- [scsi] scsi: lpfc: rport port swap discovery issue. (Dick Kennedy) [1656635]
- [scsi] scsi: lpfc: Fix discovery failures during port failovers with lots of vports (Dick Kennedy) [1656635]
- [scsi] scsi: lpfc: refactor mailbox structure context fields (Dick Kennedy) [1656635]
- [scsi] scsi: lpfc: Correct loss of fc4 type on remote port address change (Dick Kennedy) [1656635]
- [hid] HID: multitouch: Add pointstick support for Cirque Touchpad (Perry Yuan) [1656673]
- [powerpc] KVM: PPC: Book3S HV: Fix handling for interrupted H_ENTER_NESTED (Suraj Jitindar Singh) [1649980]
- [powerpc] powerpc: Select CONFIG_SWIOTLB (Gustavo Duarte) [1648466]
- [fs] nfs: Fix a missed page unlock after pg_doio() (Benjamin Coddington) [1651287]
- [arm64] arm64: fix possible spectre-v1 write in ptrace_hbp_set_event() (Mark Salter) [1637585]
- [fs] fsnotify: Fix busy inodes during unmount (Lukas Czerner) [1650462]
- [tools] perf vendor events arm64: Update ThunderX2 implementation defined pmu core events (Robert Richter) [1501638]
- [tools] perf tools: Fix undefined symbol scnprintf in libperf-jvmti.so (Jiri Olsa) [1579484]

* Tue Dec 18 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-57.el8]
- [block] blk-mq: export hctx->type in debugfs instead of sysfs (Ming Lei) [1660040]
- [block] blk-mq: fix dispatch from sw queue (Ming Lei) [1660040]
- [block] blk-mq: skip zero-queue maps in blk_mq_map_swqueue (Ming Lei) [1660040]
- [nvme] nvme-pci: don't share queue maps (Ming Lei) [1660040]
- [block] blk-mq: only dispatch to non-defauly queue maps if they have queues (Ming Lei) [1660040]
- [x86] KVM: LAPIC: Fix pv ipis use-before-initialization (Paul Lai) [1657702]
- [fs] autofs: fix directory and symlink access (Ian Kent) [1611967]
- [infiniband] IB/iser: Fix possible NULL deref at iser_inv_desc() (Don Dutile) [1657574]
- [infiniband] RDMA/core: Fix unwinding flow in case of error to register device (Don Dutile) [1657574]
- [infiniband] IB/rxe: fix for duplicate request processing and ack psns (Don Dutile) [1657574]
- [infiniband] IB/ipoib: Clear IPCB before icmp_send (Don Dutile) [1657574]
- [infiniband] RDMA/core: Do not expose unsupported counters (Don Dutile) [1657574]
- [infiniband] IB/ucm: Fix Spectre v1 vulnerability (Don Dutile) [1657574]
- [infiniband] RDMA/ucma: Fix Spectre v1 vulnerability (Don Dutile) [1657574]
- [infiniband] RDMA/uverbs: Don't overwrite NULL pointer with ZERO_SIZE_PTR (Don Dutile) [1657574]
- [infiniband] RDMA/cma: Do not ignore net namespace for unbound cm_id (Don Dutile) [1657574]
- [net] xprtrdma: Reset credit grant properly after a disconnect (Don Dutile) [1657574]
- [input] Input: hyper-v - fix wakeup from suspend-to-idle (Vitaly Kuznetsov) [1588888]
- [kernel] kernel: hung_task.c: disable on suspend (Vitaly Kuznetsov) [1588888]
- [kernel] redhat: add a comment with warning about RH_KABI_EXCLUDE usage (Jiri Benc) [1656933]
- [rpmspec] Sign the aarch64 kernel (Jeremy Linton) [1659158]

* Mon Dec 17 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-56.el8]
- [netdrv] nfp: flower: add geneve option match offload (Pablo Cascon) [1655604]
- [netdrv] nfp: flower: add geneve option push action offload (Pablo Cascon) [1655604]
- [netdrv] nfp: flower: offload tos and tunnel flags for ipv4 udp tunnels (Pablo Cascon) [1655604]
- [netdrv] nfp: flower: set ip tunnel ttl from encap action (Pablo Cascon) [1655604]
- [netdrv] nfp: flower: extract ipv4 udp tunnel ttl from route (Pablo Cascon) [1655604]
- [net] sctp: hold transport before accessing its asoc in sctp_transport_get_next (Marcelo Leitner) [1656271]
- [net] sctp: fix the data size calculation in sctp_data_size (Marcelo Leitner) [1656271]
- [net] sctp: fix race on sctp_id2asoc (Marcelo Leitner) [1656271]
- [net] rtnetlink: ndo_dflt_fdb_dump() only work for ARPHRD_ETHER devices (Hangbin Liu) [1657120]
- [netdrv] mlx5e: fix csum adjustments caused by RXFCS (Hangbin Liu) [1657120]
- [net] drop skb on failure in ip_check_defrag() (Hangbin Liu) [1657120]
- [net] rtnl_configure_link: fix dev flags changes arg to __dev_notify_flags (Hangbin Liu) [1657120]
- [net] socket: fix a missing-check bug (Hangbin Liu) [1657120]
- [net] rtnetlink: Disallow FDB configuration for non-Ethernet device (Hangbin Liu) [1657120]
- [net] rtnetlink: Fail dump if target netnsid is invalid (Hangbin Liu) [1657120]
- [net] rtnetlink: fix rtnl_fdb_dump() for ndmsg header (Hangbin Liu) [1657120]
- [net] rtnl: limit IFLA_NUM_TX_QUEUES and IFLA_NUM_RX_QUEUES to 4096 (Hangbin Liu) [1657120]
- [net] socket: fix struct ifreq size in compat ioctl (Hangbin Liu) [1657120]
- [net] fix pskb_trim_rcsum_slow() with odd trim offset (Hangbin Liu) [1657120]
- [net] gso_segment: Reset skb->mac_len after modifying network header (Hangbin Liu) [1657120]
- [net] Use __kernel_clockid_t in uapi net_stamp.h (Davide Caratti) [1638022]
- [net] tun: Consistently configure generic netdev params via rtnetlink (Matteo Croce) [1657910]
- [net] tun: napi flags belong to tfile (Matteo Croce) [1657910]
- [net] tun: initialize napi_mutex unconditionally (Matteo Croce) [1657910]
- [net] tun: remove unused parameters (Matteo Croce) [1657910]
- [net] team: Forbid enslaving team device to itself (Matteo Croce) [1658725]
- [net] sched: Remove TCA_OPTIONS from policy (Davide Caratti) [1658516]
- [net] sched: cls_api: add missing validation of netlink attributes (Davide Caratti) [1658516]
- [net] sched: gred: pass the right attribute to gred_change_table_def() (Davide Caratti) [1658516]
- [net] sched: cls_u32: fix hnode refcounting (Davide Caratti) [1658516]
- [net] sched: Add policy validation for tc attributes (Davide Caratti) [1658516]
- [net] bpf: use __GFP_COMP while allocating page (Andrea Claudi) [1658231]
- [net] xsk: do not call synchronize_net() under RCU read lock (Andrea Claudi) [1658231]
- [net] bpf: fix partial copy of map_ptr when dst is scalar (Andrea Claudi) [1658231]
- [net] bpf: Fix bpf_msg_pull_data() (Andrea Claudi) [1658231]
- [net] bpf: fix shift upon scatterlist ring wrap-around in bpf_msg_pull_data (Andrea Claudi) [1658231]
- [net] bpf: fix sg shift repair start offset in bpf_msg_pull_data (Andrea Claudi) [1658231]
- [net] bpf: fix msg->data/data_end after sg shift repair in bpf_msg_pull_data (Andrea Claudi) [1658231]
- [net] bpf: fix several offset tests in bpf_msg_pull_data (Andrea Claudi) [1658231]
- [net] vlan: add support for tunnel offload (Andrea Claudi) [1656804]
- [net] 8021q: move vlan offload registrations into vlan_core (Hangbin Liu) [1657658]
- [net] ipv6/ndisc: Preserve IPv6 control buffer if protocol error handlers are called (Stefano Brivio) [1658010]
- [net] ipv6: Allow onlink routes to have a device mismatch if it is the default route (Stefano Brivio) [1658010]
- [net] ipv6: Fix index counter for unicast addresses in in6_dump_addrs (Stefano Brivio) [1658010]
- [net] ipv6: mcast: fix a use-after-free in inet6_mc_check (Stefano Brivio) [1658010]
- [net] ipv6: rate-limit probes for neighbourless routes (Stefano Brivio) [1658010]
- [net] ipv6: stop leaking percpu memory in fib6 info (Stefano Brivio) [1658010]
- [net] ipv6: Remove extra call to ip6_convert_metrics for multipath case (Stefano Brivio) [1658010]
- [net] ipv6: Display all addresses in output of /proc/net/if_inet6 (Stefano Brivio) [1658010]
- [net] ipv6: do not copy dst flags on rt init (Stefano Brivio) [1658010]
- [net] ipv6: Only update MTU metric if it set (Stefano Brivio) [1658010]
- [net] ipv6: don't get lwtstate twice in ip6_rt_copy_init() (Stefano Brivio) [1658010]
- [net] ipv6: Put lwtstate when destroying fib6_info (Stefano Brivio) [1658010]
- [net] ip6_tunnel: Fix encapsulation layout (Stefano Brivio) [1658008]
- [net] vxlan: fill ttl inherit info (Stefano Brivio) [1658008]
- [net] ip_tunnel: be careful when accessing the inner header (Stefano Brivio) [1658008]
- [net] vti6: remove !skb->ignore_df check from vti6_xmit() (Stefano Brivio) [1658008]
- [net] ip6_vti: fix a null pointer deference when destroy vti6 tunnel (Stefano Brivio) [1658008]
- [net] ip6_vti: fix creating fallback tunnel device for vti6 (Stefano Brivio) [1658008]
- [net] ip_vti: fix a null pointer deferrence when create vti fallback tunnel (Stefano Brivio) [1658008]
- [net] l2tp: use sk_dst_check() to avoid race on sk->sk_dst_cache (Stefano Brivio) [1658008]
- [net] macsec: let the administrator set UP state even if lowerdev is down (Sabrina Dubroca) [1645540]
- [net] macsec: update operstate when lower device changes (Sabrina Dubroca) [1645540]
- [net] tcp: do not restart timewait timer on rst reception (Paolo Abeni) [1657988]
- [net] tcp: really ignore MSG_ZEROCOPY if no SO_ZEROCOPY (Paolo Abeni) [1657988]
- [net] tcp, ulp: add alias for all ulp modules (Paolo Abeni) [1657988]
- [net] tcp, ulp: fix leftover icsk_ulp_ops preventing sock from reattach (Paolo Abeni) [1657988]
- [net] ipv4: tcp: send zero IPID for RST and ACK sent in SYN-RECV and TIME-WAIT state (Paolo Abeni) [1657988]
- [net] neighbour: Avoid writing before skb->head in neigh_hh_output() (Stefano Brivio) [1643336]
- [net] ipv6: Check available headroom in ip6_xmit() even without options (Stefano Brivio) [1643336]
- [net] ipv6: fix possible use-after-free in ip6_xmit() (Stefano Brivio) [1643336]
- [net] openvswitch: Fix push/pop ethernet validation (Hangbin Liu) [1657226]
- [net] cgroup, netclassid: add a preemption point to write_classid (Hangbin Liu) [1657226]
- [net] ethtool: fix a privilege escalation bug (Hangbin Liu) [1657226]
- [net] llc: set SOCK_RCU_FREE in llc_sap_add_socket() (Hangbin Liu) [1657226]
- [net] dcb: For wild-card lookups, use priority -1, not 0 (Hangbin Liu) [1657226]
- [net] packet: fix packet drop as of virtio gso (Hangbin Liu) [1657226]
- [net] netlabel: check for IPV4MASK in addrinfo_get (Hangbin Liu) [1657226]
- [net] netfilter: seqadj: re-load tcp header pointer after possible head reallocation (Florian Westphal) [1654259]
- [net] netfilter: nf_tables: avoid BUG_ON usage (Florian Westphal) [1654259]
- [net] netfilter: nf_tables: deactivate expressions in rule replecement routine (Florian Westphal) [1654259]
- [net] netfilter: nat: fix double register in masquerade modules (Florian Westphal) [1654259]
- [net] netfilter: add missing error handling code for register functions (Florian Westphal) [1654259]
- [net] netfilter: nf_tables: fix use-after-free when deleting compat expressions (Florian Westphal) [1654259]
- [net] netfilter: xt_RATEEST: remove netns exit routine (Florian Westphal) [1654259]
- [net] netfilter: nf_tables: don't use position attribute on rule replacement (Florian Westphal) [1654259]
- [net] revert "netfilter: nft_numgen: add map lookups for numgen random operations" (Florian Westphal) [1654259]
- [net] netfilter: xt_IDLETIMER: add sysfs filename checking routine (Florian Westphal) [1654259]
- [net] netfilter: conntrack: fix calculation of next bucket number in early_drop (Florian Westphal) [1654259]
- [net] netfilter: conntrack: get rid of double sizeof (Florian Westphal) [1654259]
- [net] netfilter: nft_set_rbtree: add missing rb_erase() in GC routine (Florian Westphal) [1654259]
- [net] netfilter: nfnetlink_queue: Solve the NFQUEUE/conntrack clash for NF_REPEAT (Florian Westphal) [1654259]
- [net] netfilter: nf_tables: release chain in flushing set (Florian Westphal) [1654259]
- [net] netfilter: xt_checksum: ignore gso skbs (Florian Westphal) [1654259]
- [net] netfilter: xt_cluster: add dependency on conntrack module (Florian Westphal) [1654259]
- [net] netfilter: fix memory leaks on netlink_dump_start error (Florian Westphal) [1654259]
- [net] netfilter: x_tables: do not fail xt_alloc_table_info too easilly (Florian Westphal) [1654259]
- [net] ipvs: fix race between ip_vs_conn_new() and ip_vs_del_dest() (Florian Westphal) [1654259]
- [net] netfilter: ip6t_rpfilter: set F_IFACE for linklocal addresses (Florian Westphal) [1654259]
- [net] xfrm: policy: use hlist rcu variants on insert (Sabrina Dubroca) [1657272]
- [net] xfrm: validate template mode (Sabrina Dubroca) [1657272]
- [net] xfrm: Fix NULL pointer dereference when skb_dst_force clears the dst_entry. (Sabrina Dubroca) [1657272]
- [net] xfrm: reset transport header back to network header after all input transforms ahave been applied (Sabrina Dubroca) [1657272]
- [net] xfrm: reset crypto_done when iterating over multiple input xfrms (Sabrina Dubroca) [1657272]
- [net] xfrm: Validate address prefix lengths in the xfrm selector. (Sabrina Dubroca) [1657272]
- [net] tls: fix currently broken MSG_PEEK behavior (Sabrina Dubroca) [1657225]
- [net] tls: zero the crypto information from tls_context before freeing (Sabrina Dubroca) [1657225]
- [net] tls: clear key material from kernel memory when do_tls_setsockopt_conf fails (Sabrina Dubroca) [1657225]
- [net] tls: don't copy the key out of tls12_crypto_info_aes_gcm_128 (Sabrina Dubroca) [1657225]
- [net] tls: Set count of SG entries if sk_alloc_sg returns -ENOSPC (Sabrina Dubroca) [1657225]
- [net] tls: possible hang when do_tcp_sendpages hits sndbuf is full case (Sabrina Dubroca) [1657225]
- [net] tls: Fix improper revert in zerocopy_from_iter (Sabrina Dubroca) [1657225]
- [net] tls: Fix zerocopy_from_iter iov handling (Sabrina Dubroca) [1657225]
- [net] netfilter: conntrack: reset tcp maxwin on re-register (Florian Westphal) [1647310]
- [net] configs: Enable CONFIG_IP_SET_HASH_IPMAC as a module (Stefano Brivio) [1655301]
- [net] udp: fix handling of CHECKSUM_COMPLETE packets (Paolo Abeni) [1655656]
- [net] udp: Unbreak modules that rely on external __skb_recv_udp() availability (Paolo Abeni) [1655656]
- [net] udp6: fix encap return code for resubmitting (Paolo Abeni) [1655656]
- [net] team: no need to do team_notify_peers or team_mcast_rejoin when disabling port (Hangbin Liu) [1653197]
- [net] sctp: not increase stream's incnt before sending addstrm_in request (Xin Long) [1651428]
- [net] sctp: not allow to set asoc prsctp_enable by sockopt (Xin Long) [1647272]
- [net] revert "sctp: remove sctp_transport_pmtu_check" (Xin Long) [1643330]
- [net] fix XPS static_key accounting (Ivan Vecera) [1651781]
- [net] restore call to netdev_queue_numa_node_write when resetting XPS (Ivan Vecera) [1651781]
- [net] allow fallback function to pass netdev (Ivan Vecera) [1651781]
- [net] allow ndo_select_queue to pass netdev (Ivan Vecera) [1651781]
- [net] Add generic ndo_select_queue functions (Ivan Vecera) [1651781]
- [net] Add support for subordinate traffic classes to netdev_pick_tx (Ivan Vecera) [1651781]
- [net] ixgbe: Add code to populate and use macvlan TC to Tx queue map (Ivan Vecera) [1651781]
- [net] Add support for subordinate device traffic classes (Ivan Vecera) [1651781]
- [net] net-sysfs: Drop support for XPS and traffic_class on single queue device (Ivan Vecera) [1651781]
- [net] Provide stub for __netif_set_xps_queue if there is no CONFIG_XPS (Ivan Vecera) [1651781]
- [net] allow to call netif_reset_xps_queues() under cpus_read_lock (Ivan Vecera) [1651781]
- [net] documentation: Add explanation for XPS using Rx-queue(s) map (Ivan Vecera) [1651781]
- [net] net-sysfs: Add interface for Rx queue(s) map per Tx queue (Ivan Vecera) [1651781]
- [net] Enable Tx queue selection based on Rx queues (Ivan Vecera) [1651781]
- [net] Record receive queue number for a connection (Ivan Vecera) [1651781]
- [net] sock: Change tx_queue_mapping in sock_common to unsigned short (Ivan Vecera) [1651781]
- [net] Use static_key for XPS maps (Ivan Vecera) [1651781]
- [net] Refactor XPS for CPUs and Rx queues (Ivan Vecera) [1651781]
- [net] devlink: Add helper function for safely copy string param (Ivan Vecera) [1647914]
- [net] devlink: Fix param cmode driverinit for string type (Ivan Vecera) [1647914]
- [net] devlink: Fix param set handling for string type (Ivan Vecera) [1647914]
- [net] devlink: Add Documentation/networking/devlink-params-bnxt.txt (Ivan Vecera) [1647914]
- [net] devlink: Add Documentation/networking/devlink-params.txt (Ivan Vecera) [1647914]
- [net] devlink: Add generic parameter msix_vec_per_pf_min (Ivan Vecera) [1647914]
- [net] devlink: Add generic parameter msix_vec_per_pf_max (Ivan Vecera) [1647914]
- [net] devlink: Add generic parameter ignore_ari (Ivan Vecera) [1647914]
- [net] devlink: double free in devlink_resource_fill() (Ivan Vecera) [1647914]
- [net] devlink: Add extack for eswitch operations (Ivan Vecera) [1647914]
- [net] devlink: Add generic parameters region_snapshot (Ivan Vecera) [1647914]
- [net] devlink: Add support for region snapshot read command (Ivan Vecera) [1647914]
- [net] devlink: Add support for region snapshot delete command (Ivan Vecera) [1647914]
- [net] devlink: Extend the support querying for region snapshot IDs (Ivan Vecera) [1647914]
- [net] devlink: Add support for region get command (Ivan Vecera) [1647914]
- [net] devlink: Add support for creating region snapshots (Ivan Vecera) [1647914]
- [net] devlink: Add callback to query for snapshot id before snapshot create (Ivan Vecera) [1647914]
- [net] devlink: Add support for creating and destroying regions (Ivan Vecera) [1647914]
- [net] devlink: fix incorrect return statement (Ivan Vecera) [1647914]
- [net] devlink: Add enable_sriov boolean generic parameter (Ivan Vecera) [1647914]
- [net] devlink: Add generic parameters internal_err_reset and max_macs (Ivan Vecera) [1647914]
- [net] devlink: Add devlink notifications support for params (Ivan Vecera) [1647914]
- [net] devlink: Add support for get/set driverinit value (Ivan Vecera) [1647914]
- [net] devlink: Add param set command (Ivan Vecera) [1647914]
- [net] devlink: Add param get command (Ivan Vecera) [1647914]
- [net] devlink: Add devlink_param register and unregister (Ivan Vecera) [1647914]
- [net] ipvs: call ip_vs_dst_notifier earlier than ipv6_dev_notf (Xin Long) [1645064]
- [net] ipv6: fix a dst leak when removing its exception (Xin Long) [1645064]
- [net] netfilter: ipset: list:set: Decrease refcount synchronously on deletion and replace (Stefano Brivio) [1649089]
- [net] bridge: remove ipv6 zero address check in mcast queries (Hangbin Liu) [1639666]
- [net] bridge: do not add port to router list when receives query with source 0.0.0.0 (Hangbin Liu) [1639666]
- [net] netfilter: ipv6: fix oops when defragmenting locally generated fragments (Florian Westphal) [1642341]
- [net] xfrm6: call kfree_skb when skb is toobig (Sabrina Dubroca) [1628851]
- [net] sched: act_police: fix memory leak in case of invalid control action (Ivan Vecera) [1638022]
- [net] sched: act_police: add missing spinlock initialization (Ivan Vecera) [1638022]
- [net] netfilter: xt_socket: check sk before checking for netns. (Ivan Vecera) [1638022]
- [net] sched: act_police: fix race condition on state variables (Ivan Vecera) [1638022]
- [net] sched: cls_flower: validate nested enc_opts_policy to avoid warning (Ivan Vecera) [1638022]
- [net] sched: act_pedit: fix memory leak when IDR allocation fails (Ivan Vecera) [1638022]
- [net] configs: disable CAKE, ETF & SKBPRIO qdisc in config (Ivan Vecera) [1638022]
- [net] tc-tests: test denial of 'goto chain' for exceed traffic in police.json (Ivan Vecera) [1638022]
- [net] tc-tests: test denial of 'goto chain' on 'random' traffic in gact.json (Ivan Vecera) [1638022]
- [net] sched: act_police: disallow 'goto chain' on fallback control action (Ivan Vecera) [1638022]
- [net] sched: act_gact: disallow 'goto chain' on fallback control action (Ivan Vecera) [1638022]
- [net] net_sched: fix a crash in tc_new_tfilter() (Ivan Vecera) [1638022]
- [net] core: make function ___gnet_stats_copy_basic() static (Ivan Vecera) [1638022]
- [net] net_sched: convert idrinfo->lock from spinlock to a mutex (Ivan Vecera) [1638022]
- [net] loopback: clear skb->tstamp before netif_rx() (Ivan Vecera) [1638022]
- [net] skbuff: preserve sock reference when scrubbing the skb. (Ivan Vecera) [1638022]
- [net] netfilter: check if the socket netns is correct. (Ivan Vecera) [1638022]
- [net] sched: make function qdisc_free_cb() static (Ivan Vecera) [1638022]
- [net] sched: use reference counting for tcf blocks on rules update (Ivan Vecera) [1638022]
- [net] sched: implement tcf_block_refcnt_{get|put}() (Ivan Vecera) [1638022]
- [net] sched: protect block idr with spinlock (Ivan Vecera) [1638022]
- [net] sched: implement functions to put and flush all chains (Ivan Vecera) [1638022]
- [net] sched: change tcf block reference counter type to refcount_t (Ivan Vecera) [1638022]
- [net] sched: use Qdisc rcu API instead of relying on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: add helper function to take reference to Qdisc (Ivan Vecera) [1638022]
- [net] sched: extend Qdisc with rcu (Ivan Vecera) [1638022]
- [net] sched: rename qdisc_destroy() to qdisc_put() (Ivan Vecera) [1638022]
- [net] core: netlink: add helper refcount dec and lock function (Ivan Vecera) [1638022]
- [net] sched: act_ipt: check for underflow in __tcf_ipt_init() (Ivan Vecera) [1638022]
- [net] sched: Add hardware specific counters to TC actions (Ivan Vecera) [1638022]
- [net] core: Add new basic hardware counter (Ivan Vecera) [1638022]
- [net] net_sched: change tcf_del_walker() to take idrinfo->lock (Ivan Vecera) [1638022]
- [net] sched: Use FIELD_SIZEOF directly instead of reimplementing its function (Ivan Vecera) [1638022]
- [net] sched: act_sample: fix NULL dereference in the data path (Ivan Vecera) [1638022]
- [net] sched: act_police: don't use spinlock in the data path (Ivan Vecera) [1638022]
- [net] sched: act_police: use per-cpu counters (Ivan Vecera) [1638022]
- [net] net_sched: notify filter deletion when deleting a chain (Ivan Vecera) [1638022]
- [net] htb: use anonymous union for simplicity (Ivan Vecera) [1638022]
- [net] net_sched: remove redundant qdisc lock classes (Ivan Vecera) [1638022]
- [net] sched: cls_flower: dump offload count value (Ivan Vecera) [1638022]
- [net] net_sched: properly cancel netlink dump on failure (Ivan Vecera) [1638022]
- [net] sched: fix memory leak in act_tunnel_key_init() (Ivan Vecera) [1638022]
- [net] sched: action_ife: take reference to meta module (Ivan Vecera) [1638022]
- [net] act_ife: fix a potential use-after-free (Ivan Vecera) [1638022]
- [net] sched: act_nat: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_skbedit: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: null actions array pointer before releasing action (Ivan Vecera) [1638022]
- [net] sched: fix type of htb statistics (Ivan Vecera) [1638022]
- [net] net_sched: add missing tcf_lock for act_connmark (Ivan Vecera) [1638022]
- [net] revert "net: sched: act: add extack for lookup callback" (Ivan Vecera) [1638022]
- [net] tc-testing: add test-cases for numeric and invalid control action (Ivan Vecera) [1638022]
- [net] net_sched: reject unknown tcfa_action values (Ivan Vecera) [1638022]
- [net] sched: act_pedit: fix dump of extended layered op (Ivan Vecera) [1638022]
- [net] sched: return -ENOENT when trying to remove filter from non-existent chain (Ivan Vecera) [1638022]
- [net] sched: fix extack error message when chain is failed to be created (Ivan Vecera) [1638022]
- [net] sched: Fix memory exposure from short TCA_U32_SEL (Ivan Vecera) [1638022]
- [net] net_sched: fix unused variable warning in stmmac (Ivan Vecera) [1638022]
- [net] sch_cake: Fix TC filter flow override and expand it to hosts as well (Ivan Vecera) [1638022]
- [net] sch_cake: Remove unused including <linux/version.h> (Ivan Vecera) [1638022]
- [net] act_ife: fix a potential deadlock (Ivan Vecera) [1638022]
- [net] act_ife: move tcfa_lock down to where necessary (Ivan Vecera) [1638022]
- [net] revert "net: sched: act_ife: disable bh when taking ife_mod_lock" (Ivan Vecera) [1638022]
- [net] net_sched: remove unused tcfa_capab (Ivan Vecera) [1638022]
- [net] net_sched: remove list_head from tc_action (Ivan Vecera) [1638022]
- [net] net_sched: remove unused tcf_idr_check() (Ivan Vecera) [1638022]
- [net] net_sched: remove unused parameter for tcf_action_delete() (Ivan Vecera) [1638022]
- [net] net_sched: remove unnecessary ops->delete() (Ivan Vecera) [1638022]
- [net] net_sched: improve and refactor tcf_action_put_many() (Ivan Vecera) [1638022]
- [net] sched: always disable bh when taking tcf_lock (Ivan Vecera) [1638022]
- [net] sched: act_ife: always release ife action on init error (Ivan Vecera) [1638022]
- [net] cls_matchall: fix tcf_unbind_filter missing (Ivan Vecera) [1638022]
- [net] sched: act_ife: disable bh when taking ife_mod_lock (Ivan Vecera) [1638022]
- [net] sched: act_mirred method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_vlan method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_skbmod method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_skbedit method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_simple method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_police method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_pedit method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_nat method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_ipt method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_gact method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_sum method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_bpf method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_connmark method rename for grep-ability and consistency (Ivan Vecera) [1638022]
- [net] sched: act_police: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] core: protect rate estimator statistics pointer with lock (Ivan Vecera) [1638022]
- [net] sched: act_mirred: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: extend action ops with put_dev callback (Ivan Vecera) [1638022]
- [net] sched: act_vlan: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_tunnel_key: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_skbmod: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_simple: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_sample: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_pedit: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_ipt: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_ife: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_gact: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_csum: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] sched: act_bpf: remove dependency on rtnl lock (Ivan Vecera) [1638022]
- [net] tc: Update README and add config (Ivan Vecera) [1638022]
- [net] sched: fix block->refcnt decrement (Ivan Vecera) [1638022]
- [net] tc-tests: initial version of nat action unit tests (Ivan Vecera) [1638022]
- [net] sched: allow flower to match tunnel options (Ivan Vecera) [1638022]
- [net] flow_dissector: allow dissection of tunnel options from metadata (Ivan Vecera) [1638022]
- [net] tc-testing: remove duplicate spaces in skbedit match patterns (Ivan Vecera) [1638022]
- [net] tc-testing: remove duplicate spaces in connmark match patterns (Ivan Vecera) [1638022]
- [net] tc-testing: flush gact actions on test teardown (Ivan Vecera) [1638022]
- [net] tc-testing: fix ip address in u32 test (Ivan Vecera) [1638022]
- [net] sched: cls_flower: Fix an error code in fl_tmplt_create() (Ivan Vecera) [1638022]
- [net] sched: fix flush on non-existing chain (Ivan Vecera) [1638022]
- [net] sched: make tcf_chain_{get, put}() static (Ivan Vecera) [1638022]
- [net] sched: fix notifications for action-held chains (Ivan Vecera) [1638022]
- [net] sched: change name of zombie chain to "held_by_acts_only" (Ivan Vecera) [1638022]
- [net] act_mirred: use TC_ACT_REINSERT when possible (Ivan Vecera) [1638022]
- [net] tc: introduce TC_ACT_REINSERT. (Ivan Vecera) [1638022]
- [net] tc/act: remove unneeded RCU lock in action callback (Ivan Vecera) [1638022]
- [net] sched: user-space can't set unknown tcfa_action values (Ivan Vecera) [1638022]
- [net] Add and use skb_mark_not_on_list(). (Ivan Vecera) [1638022]
- [net] sch_netem: Move private queue handler to generic location. (Ivan Vecera) [1638022]
- [net] sch_htb: Remove local SKB queue handling code. (Ivan Vecera) [1638022]
- [net] act_bpf: Use kmemdup instead of duplicating it in tcf_bpf_init_from_ops (Ivan Vecera) [1638022]
- [net] cls_bpf: Use kmemdup instead of duplicating it in cls_bpf_prog_from_ops (Ivan Vecera) [1638022]
- [net] act_pedit: remove unnecessary semicolon (Ivan Vecera) [1638022]
- [net] sched: don't dump chains only held by actions (Ivan Vecera) [1638022]
- [net] sch_cake: Make gso-splitting configurable from userspace (Ivan Vecera) [1638022]
- [net] sched: unmark chain as explicitly created on delete (Ivan Vecera) [1638022]
- [net] sched: cls_api: fix dead code in switch (Ivan Vecera) [1638022]
- [net] sched: cls_flower: Use correct inline function for assignment of vlan tpid (Ivan Vecera) [1638022]
- [net] sched: fix trailing whitespace (Ivan Vecera) [1638022]
- [net] cbs: Add support for the graft function (Ivan Vecera) [1638022]
- [net] sched: add skbprio scheduler (Ivan Vecera) [1638022]
- [net] selftests: forwarding: add tests for TC chain templates (Ivan Vecera) [1638022]
- [net] selftests: forwarding: add tests for TC chains creation adn destruction (Ivan Vecera) [1638022]
- [net] selftests: forwarding: move shblock tc support check to a separate helper (Ivan Vecera) [1638022]
- [net] sched: cls_flower: propagate chain teplate creation and destruction to drivers (Ivan Vecera) [1638022]
- [net] sched: cls_flower: implement chain templates (Ivan Vecera) [1638022]
- [net] sched: cls_flower: change fl_init_dissector to accept mask and dissector (Ivan Vecera) [1638022]
- [net] sched: cls_flower: move key/mask dumping into a separate function (Ivan Vecera) [1638022]
- [net] sched: introduce chain templates (Ivan Vecera) [1638022]
- [net] sched: introduce chain object to uapi (Ivan Vecera) [1638022]
- [net] sched: Avoid implicit chain 0 creation (Ivan Vecera) [1638022]
- [net] sched: push ops lookup bits into tcf_proto_lookup_ops() (Ivan Vecera) [1638022]
- [net] nfp: bring back support for offloading shared blocks (Ivan Vecera) [1638022]
- [net] sched: use PTR_ERR_OR_ZERO macro in tcf_block_cb_register (Ivan Vecera) [1638022]
- [net] tc-tests: initial version of fw filter unit tests (Ivan Vecera) [1638022]
- [net] sch_cake: Fix tin order when set through skb->priority (Ivan Vecera) [1638022]
- [net] sched: act_skbedit: don't use spinlock in the data path (Ivan Vecera) [1638022]
- [net] sched: skbedit: use per-cpu counters (Ivan Vecera) [1638022]
- [net] tc-testing: add geneve options in tunnel_key unit tests (Ivan Vecera) [1638022]
- [net] sched: fix unprotected access to rcu cookie pointer (Ivan Vecera) [1638022]
- [net] sched: act_ife: fix memory leak in ife init (Ivan Vecera) [1638022]
- [net] sched: refactor flower walk to iterate over idr (Ivan Vecera) [1638022]
- [net] sched: flower: Fix null pointer dereference when run tc vlan command (Ivan Vecera) [1638022]
- [net] sched: Fix warnings from xchg() on RCU'd cookie pointer. (Ivan Vecera) [1638022]
- [net] cls_flower: fix error values for commands not supported by drivers (Ivan Vecera) [1638022]
- [net] nfp: handle cls_flower command default case (Ivan Vecera) [1638022]
- [net] bnxt: simplify cls_flower command switch and handle default case (Ivan Vecera) [1638022]
- [net] sch_cake: Conditionally split GSO segments (Ivan Vecera) [1638022]
- [net] sch_cake: Add overhead compensation support to the rate shaper (Ivan Vecera) [1638022]
- [net] sch_cake: Add DiffServ handling (Ivan Vecera) [1638022]
- [net] sch_cake: Add NAT awareness to packet classifier (Ivan Vecera) [1638022]
- [net] netfilter: Add nf_ct_get_tuple_skb global lookup function (Ivan Vecera) [1638022]
- [net] sch_cake: Add optional ACK filter (Ivan Vecera) [1638022]
- [net] sch_cake: Add ingress mode (Ivan Vecera) [1638022]
- [net] sched: Add Common Applications Kept Enhanced (cake) qdisc (Ivan Vecera) [1638022]
- [net] Use __u32 in uapi net_stamp.h (Ivan Vecera) [1638022]
- [net] sched: flower: Add supprt for matching on QinQ vlan headers (Ivan Vecera) [1638022]
- [net] sched: flower: Dump the ethertype encapsulated in vlan (Ivan Vecera) [1638022]
- [net] flow_dissector: Add support for QinQ dissection (Ivan Vecera) [1638022]
- [net] sched: flower: Add support for matching on vlan ethertype (Ivan Vecera) [1638022]
- [net] flow_dissector: Save vlan ethertype from headers (Ivan Vecera) [1638022]
- [net] sched: change action API to use array of pointers to actions (Ivan Vecera) [1638022]
- [net] sched: atomically check-allocate action (Ivan Vecera) [1638022]
- [net] sched: use reference counting action init (Ivan Vecera) [1638022]
- [net] sched: don't release reference on action overwrite (Ivan Vecera) [1638022]
- [net] sched: implement reference counted action release (Ivan Vecera) [1638022]
- [net] sched: add 'delete' function to action ops (Ivan Vecera) [1638022]
- [net] sched: implement action API that deletes action by index (Ivan Vecera) [1638022]
- [net] sched: always take reference to action (Ivan Vecera) [1638022]
- [net] sched: implement unlocked action init API (Ivan Vecera) [1638022]
- [net] sched: change type of reference and bind counters (Ivan Vecera) [1638022]
- [net] sched: use rcu for action cookie update (Ivan Vecera) [1638022]
- [net] sched: Make etf report drops on error_queue (Ivan Vecera) [1638022]
- [net] sched: Add HW offloading capability to ETF (Ivan Vecera) [1638022]
- [net] sched: Introduce the ETF Qdisc (Ivan Vecera) [1638022]
- [net] sched: Allow creating a Qdisc watchdog with other clocks (Ivan Vecera) [1638022]
- [net] packet: Hook into time based transmission. (Ivan Vecera) [1638022]
- [net] ipv6: Hook into time based transmission (Ivan Vecera) [1638022]
- [net] ipv4: Hook into time based transmission (Ivan Vecera) [1638022]
- [net] Add a new socket option for a future transmit time. (Ivan Vecera) [1638022]
- [net] Clear skb->tstamp only on the forwarding path (Ivan Vecera) [1638022]
- [net] sched: act_pedit: fix possible memory leak in tcf_pedit_init() (Ivan Vecera) [1638022]
- [net] net sched actions: add extack messages in pedit action (Ivan Vecera) [1638022]
- [net] net:sched: add action inheritdsfield to skbedit (Ivan Vecera) [1638022]
- [net] tc-testing: initial version of tunnel_key unit tests (Ivan Vecera) [1638022]
- [net] net sched actions: avoid bitwise operation on signed value in pedit (Ivan Vecera) [1638022]
- [net] net sched actions: fix misleading text strings in pedit action (Ivan Vecera) [1638022]
- [net] net sched actions: use sizeof operator for buffer length (Ivan Vecera) [1638022]
- [net] net sched actions: fix sparse warning (Ivan Vecera) [1638022]
- [net] net sched actions: fix coding style in pedit headers (Ivan Vecera) [1638022]
- [net] net sched actions: fix coding style in pedit action (Ivan Vecera) [1638022]
- [net] netem: slotting with non-uniform distribution (Ivan Vecera) [1638022]
- [net] check tunnel option type in tunnel flags (Ivan Vecera) [1638022]
- [net] sched: act_tunnel_key: add extended ack support (Ivan Vecera) [1638022]
- [net] tc-tests: add an extreme-case csum action test (Ivan Vecera) [1638022]
- [net] net_sched: remove unused htb drop_list (Ivan Vecera) [1638022]

* Sun Dec 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-55.el8]
- [rpmspec] always run make with HOSTCFLAGS/HOSTLDFLAGS set (Jiri Olsa) [1624124]
- [rpmspec] Pass global build flags to tools build (Jiri Olsa) [1624124]
- [rpmspec] Pass global build flags to bpftool build (Jiri Olsa) [1624124]
- [kernel] kbuild: Use HOST*FLAGS options from the command line (Jiri Olsa) [1624124]
- [scripts] kbuild: Rename HOST_LOADLIBES to KBUILD_HOSTLDLIBS (Jiri Olsa) [1624124]
- [tools] kbuild: Rename HOSTLDFLAGS to KBUILD_HOSTLDFLAGS (Jiri Olsa) [1624124]
- [scripts] kbuild: Rename HOSTCXXFLAGS to KBUILD_HOSTCXXFLAGS (Jiri Olsa) [1624124]
- [tools] kbuild: Rename HOSTCFLAGS to KBUILD_HOSTCFLAGS (Jiri Olsa) [1624124]
- [tools] tools cpupower: Override CFLAGS assignments (Jiri Olsa) [1624124]
- [tools] tools cpupower debug: Allow to use outside build flags (Jiri Olsa) [1624124]
- [tools] perf tools: Pass build flags to traceevent build (Jiri Olsa) [1624124]
- [tools] tools lib traceevent: Use LDFLAGS in the build commands (Jiri Olsa) [1624124]
- [tools] perf tools: Link libperf-jvmti.so with LDFLAGS variable (Jiri Olsa) [1624124]
- [tools] bpftool: Allow add linker flags via EXTRA_LDFLAGS variable (Jiri Olsa) [1624124]
- [tools] bpftool: Allow to add compiler flags via EXTRA_CFLAGS variable (Jiri Olsa) [1624124]
- [block] blkcg: handle dying request_queue when associating a blkg (Ming Lei) [1655485]
- [block] block: deactivate blk_stat timer in wbt_disable_default() (Ming Lei) [1655485]
- [lib] sbitmap: flush deferred clears for resize and shallow gets (Ming Lei) [1655485]
- [md] dm: fix request-based dm's use of dm_wait_for_completion (Ming Lei) [1655485]
- [nvme] nvme: fix irq vs io_queue calculations (Ming Lei) [1655485]
- [md] dm: fix inflight IO check (Ming Lei) [1655485]
- [md] dm: remove the pending IO accounting (Ming Lei) [1655485]
- [block] block: return just one value from part_in_flight (Ming Lei) [1655485]
- [block] block: switch to per-cpu in-flight counters (Ming Lei) [1655485]
- [block] block: delete part_round_stats and switch to less precise counting (Ming Lei) [1655485]
- [block] block: stop passing 'cpu' to all percpu stats methods (Ming Lei) [1655485]
- [md] dm rq: leverage blk_mq_queue_busy() to check for outstanding IO (Ming Lei) [1655485]
- [md] dm: dont rewrite dm_disk(md)->part0.in_flight (Ming Lei) [1655485]
- [lib] sbitmap: silence bogus lockdep IRQ warning (Ming Lei) [1655485]
- [scsi] scsi: Fix a harmless double shift bug (Ming Lei) [1655485]
- [block] blk-mq: re-build queue map in case of kdump kernel (Ming Lei) [1655485]
- [block] blkcg: put back rcu lock in blkcg_bio_issue_check() (Ming Lei) [1655485]
- [block] block: convert io-latency to use rq_qos_wait (Ming Lei) [1655485]
- [block] block: convert wbt_wait() to use rq_qos_wait() (Ming Lei) [1655485]
- [block] block: add rq_qos_wait to rq_qos (Ming Lei) [1655485]
- [block] blkcg: rename blkg_try_get() to blkg_tryget() (Ming Lei) [1655485]
- [block] blkcg: change blkg reference counting to use percpu_ref (Ming Lei) [1655485]
- [block] blkcg: remove bio_disassociate_task() (Ming Lei) [1655485]
- [block] blkcg: remove additional reference to the css (Ming Lei) [1655485]
- [block] blkcg: remove bio->bi_css and instead use bio->bi_blkg (Ming Lei) [1655485]
- [block] blkcg: associate writeback bios with a blkg (Ming Lei) [1655485]
- [block] blkcg: associate a blkg for pages being evicted by swap (Ming Lei) [1655485]
- [block] blkcg: consolidate bio_issue_init() to be a part of core (Ming Lei) [1655485]
- [block] blkcg: associate blkg when associating a device (Ming Lei) [1655485]
- [block] dm: set the static flush bio device on demand (Ming Lei) [1655485]
- [block] blkcg: introduce common blkg association logic (Ming Lei) [1655485]
- [block] blkcg: convert blkg_lookup_create() to find closest blkg (Ming Lei) [1655485]
- [block] blkcg: update blkg_lookup_create() to do locking (Ming Lei) [1655485]
- [block] blkcg: fix ref count issue with bio_blkcg() using task_css (Ming Lei) [1655485]
- [block] blk-mq: remove QUEUE_FLAG_POLL from default MQ flags (Ming Lei) [1655485]
- [block] block: enable polling by default if a poll map is initalized (Ming Lei) [1655485]
- [block] block: only allow polling if a poll queue_map exists (Ming Lei) [1655485]
- [block] block: remove ->poll_fn (Ming Lei) [1655485]
- [nvme] nvme-mpath: remove I/O polling support (Ming Lei) [1655485]
- [nvme] nvme-rdma: remove I/O polling support (Ming Lei) [1655485]
- [nvme] nvme-pci: remove the CQ lock for interrupt driven queues (Ming Lei) [1655485]
- [nvme] nvme-pci: don't poll from irq context when deleting queues (Ming Lei) [1655485]
- [nvme] nvme-pci: refactor nvme_disable_io_queues (Ming Lei) [1655485]
- [nvme] nvme-pci: consolidate code for polling non-dedicated queues (Ming Lei) [1655485]
- [nvme] nvme-pci: only allow polling with separate poll queues (Ming Lei) [1655485]
- [nvme] nvme-pci: cleanup SQ allocation a bit (Ming Lei) [1655485]
- [nvme] nvme-pci: use atomic bitops to mark a queue enabled (Ming Lei) [1655485]
- [block] block: move queues types to the block layer (Ming Lei) [1655485]
- [fs] aio: clear IOCB_HIPRI (Ming Lei) [1655485]
- [lib] sbitmap: fix sbitmap_for_each_set() (Ming Lei) [1655485]
- [block] blk-mq: don't call ktime_get_ns() if we don't need it (Ming Lei) [1655485]
- [block] block: add cmd_flags to print_req_error (Ming Lei) [1655485]
- [lib] sbitmap: optimize wakeup check (Ming Lei) [1655485]
- [lib] sbitmap: ammortize cost of clearing bits (Ming Lei) [1655485]
- [block] block: avoid extra bio reference for async O_DIRECT (Ming Lei) [1655485]
- [lib] sbitmap: don't loop for find_next_zero_bit() for !round_robin (Ming Lei) [1655485]
- [block] blk-mq: use plug for devices that implement ->commits_rqs() (Ming Lei) [1655485]
- [block] blk-mq: use bd->last == true for list inserts (Ming Lei) [1655485]
- [block] ataflop: implement mq_ops->commit_rqs() hook (Ming Lei) [1655485]
- [block] virtio_blk: implement mq_ops->commit_rqs() hook (Ming Lei) [1655485]
- [nvme] nvme: implement mq_ops->commit_rqs() hook (Ming Lei) [1655485]
- [block] blk-mq: add mq_ops->commit_rqs() (Ming Lei) [1655485]
- [block] block: improve logic around when to sort a plug list (Ming Lei) [1655485]
- [block] blk-mq: Add a NULL check in blk_mq_free_map_and_requests() (Ming Lei) [1655485]
- [block] ataflop: fix error handling in atari_floppy_init() (Ming Lei) [1655485]
- [block] block: add io timeout to sysfs (Ming Lei) [1655485]
- [block] block: use rcu_work instead of call_rcu to avoid sleep in softirq (Ming Lei) [1655485]
- [block] blk-mq: fix failure to decrement plug count on single rq removal (Ming Lei) [1655485]
- [block] sunvdc: Do not spin in an infinite loop when vio_ldc_send() returns EAGAIN (Ming Lei) [1655485]
- [block] block: sum requests in the plug structure (Ming Lei) [1655485]
- [block] blk-mq: Simplify request completion state (Ming Lei) [1655485]
- [scsi] scsi: Do not rely on blk-mq for double completions (Ming Lei) [1655485]
- [block] blk-mq: Return true if request was completed (Ming Lei) [1655485]
- [block] blk-mq: never redirect polled IO completions (Ming Lei) [1655485]
- [block] blk-mq: ensure mq_ops ->poll() is entered at least once (Ming Lei) [1655485]
- [block] block: make blk_poll() take a parameter on whether to spin or not (Ming Lei) [1655485]
- [nvme] nvme: remove opportunistic polling from bdev target (Ming Lei) [1655485]
- [block] blk-mq: remove 'tag' parameter from mq_ops->poll() (Ming Lei) [1655485]
- [block] blk-mq: when polling for IO, look for any completion (Ming Lei) [1655485]
- [block] block: fix attempt to assign NULL io_context (Ming Lei) [1655485]
- [block] block: Initialize BIO I/O priority early (Ming Lei) [1655485]
- [block] block: prevent merging of requests with different priorities (Ming Lei) [1655485]
- [fs] aio: Fix fallback I/O priority value (Ming Lei) [1655485]
- [block] block: Introduce get_current_ioprio() (Ming Lei) [1655485]
- [block] block: Remove bio->bi_ioc (Ming Lei) [1655485]
- [fs] aio: Comment use of IOCB_FLAG_IOPRIO aio flag (Ming Lei) [1655485]
- [nvme] nvme-fc: remove ->poll implementation (Ming Lei) [1655485]
- [block] block: have ->poll_fn() return number of entries polled (Ming Lei) [1655485]
- [block] block: avoid ordered task state change for polled IO (Ming Lei) [1655485]
- [nvme] nvme: default to 0 poll queues (Ming Lei) [1655485]
- [block] floppy: remove now unused 'flags' variable (Ming Lei) [1655485]
- [mmc] mmc: stop abusing the request queue_lock pointer (Ming Lei) [1655485]
- [block] ide: don't acquire queue_lock in ide_complete_pm_rq (Ming Lei) [1655485]
- [block] ide: don't acquire queue lock in ide_pm_execute_rq (Ming Lei) [1655485]
- [block] pktcdvd: remove queue_lock around blk_queue_max_hw_sectors (Ming Lei) [1655485]
- [block] floppy: remove queue_lock around floppy_end_request (Ming Lei) [1655485]
- [block] block: remove the rq_alloc_data request_queue field (Ming Lei) [1655485]
- [block] block: don't plug for aio/O_DIRECT HIPRI IO (Ming Lei) [1655485]
- [block] block: for async O_DIRECT, mark us as polling if asked to (Ming Lei) [1655485]
- [block] block: add polled wakeup task helper (Ming Lei) [1655485]
- [block] blk-rq-qos: inline check for q->rq_qos functions (Ming Lei) [1655485]
- [block] block: add queue_is_mq() helper (Ming Lei) [1655485]
- [nvme] nvme: provide optimized poll function for separate poll queues (Ming Lei) [1655485]
- [block] ide: clear ide_req()->special for non-passthrough requests (Ming Lei) [1655485]
- [nvme] nvme: fix handling of EINVAL on pci_alloc_irq_vectors_affinity() (Ming Lei) [1655485]
- [block] block: add wbt_disable_default export for BFQ (Ming Lei) [1655485]
- [block] block: remove the queue_lock indirection (Ming Lei) [1655485]
- [block] block: remove the lock argument to blk_alloc_queue_node (Ming Lei) [1655485]
- [mmc] mmc: stop abusing the request queue_lock pointer (Ming Lei) [1655485]
- [mmc] mmc: simplify queue initialization (Ming Lei) [1655485]
- [block] umem: don't override the queue_lock (Ming Lei) [1655485]
- [block] drbd: don't override the queue_lock (Ming Lei) [1655485]
- [block] blk-cgroup: move locking into blkg_destroy_all (Ming Lei) [1655485]
- [block] blk-cgroup: consolidate error handling in blkcg_init_queue (Ming Lei) [1655485]
- [block] block: remove a few unused exports (Ming Lei) [1655485]
- [block] block: update a few comments for the legacy request removal (Ming Lei) [1655485]
- [block] block: remove the unused lock argument to rq_qos_throttle (Ming Lei) [1655485]
- [block] block: remove queue_lockdep_assert_held (Ming Lei) [1655485]
- [block] block: use atomic bitops for ->queue_flags (Ming Lei) [1655485]
- [block] block: don't hold the queue_lock over blk_abort_request (Ming Lei) [1655485]
- [block] block: remove deadline __deadline manipulation helpers (Ming Lei) [1655485]
- [block] block: remove QUEUE_FLAG_BYPASS and ->bypass (Ming Lei) [1655485]
- [nvme] nvmet-rdma: fix response use after free (Ming Lei) [1655485]
- [nvme] nvme: validate controller state before rescheduling keep alive (Ming Lei) [1655485]
- [block] block, bfq: fix decrement of num_active_groups (Ming Lei) [1655485]
- [ata] libata: whitelist all SAMSUNG MZ7KM* solid-state disks (Ming Lei) [1655485]
- [nvme] nvme-rdma: fix double freeing of async event data (Ming Lei) [1655485]
- [nvme] nvme-pci: fix surprise removal (Ming Lei) [1655485]
- [nvme] nvme: Free ctrl device name on init failure (Ming Lei) [1655485]
- [nvme] nvme-fc: resolve io failures during connect (Ming Lei) [1655485]
- [nvme] nvme: make sure ns head inherits underlying device limits (Ming Lei) [1655485]
- [nvme] nvmet: don't try to add ns to p2p map unless it actually uses it (Ming Lei) [1655485]
- [nvme] nvme-pci: fix conflicting p2p resource adds (Ming Lei) [1655485]
- [nvme] nvmet: Optionally use PCI P2P memory (Ming Lei) [1655485]
- [nvme] nvmet: Introduce helper functions to allocate and free request SGLs (Ming Lei) [1655485]
- [nvme] nvme-pci: Add support for P2P memory in requests (Ming Lei) [1655485]
- [nvme] nvme-pci: Use PCI p2pmem subsystem to manage the CMB (Ming Lei) [1655485]
- [infiniband] IB/core: Ensure we map P2P memory correctly in rdma_rw_ctx_[init|destroy]() (Ming Lei) [1655485]
- [block] block: Add PCI P2P flag for request queue (Ming Lei) [1655485]
- [documentation] PCI/P2PDMA: Add P2P DMA driver writer's documentation (Ming Lei) [1655485]
- [documentation] docs-rst: Add a new directory for PCI documentation (Ming Lei) [1655485]
- [pci] PCI/P2PDMA: Introduce configfs/sysfs enable attribute helpers (Ming Lei) [1655485]
- [pci] PCI/P2PDMA: Add PCI p2pmem DMA mappings to adjust the bus offset (Ming Lei) [1655485]
- [pci] PCI/P2PDMA: Add sysfs group to display p2pmem stats (Ming Lei) [1655485]
- [pci] PCI/P2PDMA: Support peer-to-peer memory (Ming Lei) [1655485]
- [nvme] nvmet-rdma: support max(16KB, PAGE_SIZE) inline data (Ming Lei) [1655485]
- [nvme] nvme-rdma: support up to 4 segments of inline data (Ming Lei) [1655485]
- [fs] aio: fix failure to put the file pointer (Ming Lei) [1655485]
- [lib] scsi: Remove percpu_ida (Ming Lei) [1655485]
- [scsi] scsi: target: Convert target drivers to use sbitmap (Ming Lei) [1655485]
- [scsi] scsi: target: Abstract tag freeing (Ming Lei) [1655485]
- [block] mmc: block: Fix unsupported parallel dispatch of requests (Ming Lei) [1655485]
- [scsi] scsi: target: sbitmap: add seq_file forward declaration (Ming Lei) [1655485]
- [mm] mm, memory_hotplug: do not clear numa_node association after hot_remove (Waiman Long) [1657422]
- [fs] iomap: partially revert 4721a601099 (simulated directio short read on EFAULT) (Brian Foster) [1654713]
- [fs] splice: don't read more than available pipe space (Brian Foster) [1654713]
- [fs] vfs: allow some remap flags to be passed to vfs_clone_file_range (Brian Foster) [1654713]
- [fs] xfs: fix inverted return from xfs_btree_sblock_verify_crc (Brian Foster) [1654713]
- [fs] xfs: fix PAGE_MASK usage in xfs_free_file_space (Brian Foster) [1654713]
- [fs] fs/xfs: fix f_ffree value for statfs when project quota is set (Brian Foster) [1654713]
- [fs] iomap: readpages doesn't zero page tail beyond EOF (Brian Foster) [1654713]
- [fs] vfs: vfs_dedupe_file_range() doesn't return EOPNOTSUPP (Brian Foster) [1654713]
- [fs] iomap: dio data corruption and spurious errors when pipes fill (Brian Foster) [1654713]
- [fs] iomap: sub-block dio needs to zeroout beyond EOF (Brian Foster) [1654713]
- [fs] iomap: FUA is wrong for DIO O_DSYNC writes into unwritten extents (Brian Foster) [1654713]
- [fs] xfs: delalloc -> unwritten COW fork allocation can go wrong (Brian Foster) [1654713]
- [fs] xfs: flush removing page cache in xfs_reflink_remap_prep (Brian Foster) [1654713]
- [fs] xfs: extent shifting doesn't fully invalidate page cache (Brian Foster) [1654713]
- [fs] xfs: finobt AG reserves don't consider last AG can be a runt (Brian Foster) [1654713]
- [fs] xfs: fix transient reference count error in xfs_buf_resubmit_failed_buffers (Brian Foster) [1654713]
- [fs] xfs: uncached buffer tracing needs to print bno (Brian Foster) [1654713]
- [fs] xfs: make xfs_file_remap_range() static (Brian Foster) [1654713]
- [fs] xfs: fix shared extent data corruption due to missing cow reservation (Brian Foster) [1654713]
- [fs] xfs: fix overflow in xfs_attr3_leaf_verify (Brian Foster) [1654713]
- [fs] xfs: print buffer offsets when dumping corrupt buffers (Brian Foster) [1654713]
- [fs] xfs: Fix error code in 'xfs_ioc_getbmap()' (Brian Foster) [1654713]
- [fs] xfs: cancel COW blocks before swapext (Brian Foster) [1654713]
- [fs] xfs: clear ail delwri queued bufs on unmount of shutdown fs (Brian Foster) [1654713]
- [fs] xfs: use offsetof() in place of offset macros for __xfsstats (Brian Foster) [1654713]
- [fs] xfs: Fix xqmstats offsets in /proc/fs/xfs/xqmstat (Brian Foster) [1654713]
- [fs] xfs: fix use-after-free race in xfs_buf_rele (Brian Foster) [1654713]
- [fs] xfs: Add attibute remove and helper functions (Brian Foster) [1654713]
- [fs] xfs: Add attibute set and helper functions (Brian Foster) [1654713]
- [fs] xfs: Add helper function xfs_attr_try_sf_addname (Brian Foster) [1654713]
- [fs] xfs: Move fs/xfs/xfs_attr.h to fs/xfs/libxfs/xfs_attr.h (Brian Foster) [1654713]
- [fs] xfs: issue log message on user force shutdown (Brian Foster) [1654713]
- [fs] xfs: fix buffer state management in xrep_findroot_block (Brian Foster) [1654713]
- [fs] xfs: always assign buffer verifiers when one is provided (Brian Foster) [1654713]
- [fs] xfs: xrep_findroot_block should reject root blocks with siblings (Brian Foster) [1654713]
- [fs] xfs: add a define for statfs magic to uapi (Brian Foster) [1654713]
- [fs] xfs: print dangling delalloc extents (Brian Foster) [1654713]
- [fs] xfs: fix fork selection in xfs_find_trim_cow_extent (Brian Foster) [1654713]
- [fs] xfs: remove the unused trimmed argument from xfs_reflink_trim_around_shared (Brian Foster) [1654713]
- [fs] xfs: remove the unused shared argument to xfs_reflink_reserve_cow (Brian Foster) [1654713]
- [fs] xfs: handle zeroing in xfs_file_iomap_begin_delay (Brian Foster) [1654713]
- [fs] xfs: remove suport for filesystems without unwritten extent flag (Brian Foster) [1654713]
- [fs] xfs: remove XFS_IO_INVALID (Brian Foster) [1654713]
- [fs] xfs: remove [cm]time update from reflink calls (Brian Foster) [1654713]
- [fs] xfs: remove xfs_reflink_remap_range (Brian Foster) [1654713]
- [fs] xfs: remove redundant remap partial EOF block checks (Brian Foster) [1654713]
- [fs] xfs: support returning partial reflink results (Brian Foster) [1654713]
- [fs] xfs: clean up xfs_reflink_remap_blocks call site (Brian Foster) [1654713]
- [fs] xfs: fix pagecache truncation prior to reflink (Brian Foster) [1654713]
- [fs] vfs: clean up generic_remap_file_range_prep return value (Brian Foster) [1654713]
- [fs] vfs: hide file range comparison function (Brian Foster) [1654713]
- [fs] vfs: enable remap callers that can handle short operations (Brian Foster) [1654713]
- [fs] vfs: plumb remap flags through the vfs dedupe functions (Brian Foster) [1654713]
- [fs] vfs: plumb remap flags through the vfs clone functions (Brian Foster) [1654713]
- [fs] vfs: make remap_file_range functions take and return bytes completed (Brian Foster) [1654713]
- [fs] vfs: remap helper should update destination inode metadata (Brian Foster) [1654713]
- [fs] vfs: pass remap flags to generic_remap_checks (Brian Foster) [1654713]
- [fs] vfs: pass remap flags to generic_remap_file_range_prep (Brian Foster) [1654713]
- [fs] vfs: combine the clone and dedupe into a single remap_file_range (Brian Foster) [1654713]
- [fs] vfs: rename clone_verify_area to remap_verify_area (Brian Foster) [1654713]
- [fs] vfs: rename vfs_clone_file_prep to be more descriptive (Brian Foster) [1654713]
- [fs] vfs: skip zero-length dedupe requests (Brian Foster) [1654713]
- [fs] vfs: avoid problematic remapping requests into partial EOF block (Brian Foster) [1654713]
- [fs] vfs: strengthen checking of file range inputs to generic_remap_checks (Brian Foster) [1654713]
- [fs] vfs: exit early from zero length remap operations (Brian Foster) [1654713]
- [fs] vfs: check file ranges before cloning files (Brian Foster) [1654713]
- [fs] vfs: vfs_clone_file_prep_inodes should return EINVAL for a clone from beyond EOF (Brian Foster) [1654713]
- [block] blk-mq: not embed .mq_kobj and ctx->kobj into queue instance (Ming Lei) [1653124]
- [fs] fs: fix lost error code in dio_complete (Ming Lei) [1655364]
- [iommu] iommu/iova: Optimise attempts to allocate iova from 32bit address range (Robert Richter) [1639202]

* Fri Dec 14 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-54.el8]
- [drm] drm/nouveau/drm/nouveau: Check rc from drm_dp_mst_topology_mgr_resume() (Lyude Paul) [1658810]
- [x86] Mark Intel Apollo Lake supported (David Arcari) [1653799]
- [infiniband] IB/mlx5: Fix implicit ODP interrupted page fault (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Improve ODP debugging messages (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Use multi threaded workqueue for page fault handling (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Return success for PAGE_FAULT_RESUME in internal error state (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Lock QP during page fault handling (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Enumerate page fault types (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Add interface to hold and release core resources (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Release resource on error flow (Alaa Hleihel) [1658085]
- [netdrv] net/mlx4_core: Correctly set PFC param if global pause is turned off. (Alaa Hleihel) [1658085]
- [netdrv] net/mlx4_en: Change min MTU size to ETH_MIN_MTU (Alaa Hleihel) [1658085]
- [netdrv] mlx5: fix get_ip_proto() (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Fix page fault handling for MW (Alaa Hleihel) [1658085]
- [infiniband] RDMA/mlx5: Initialize return variable in case pagefault was skipped (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Skip non-ODP MR when handling a page fault (Alaa Hleihel) [1658085]
- [net] net/dim: Update DIM start sample after each DIM iteration (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Avoid load failure due to unknown link width (Alaa Hleihel) [1658085]
- [infiniband] RDMA/mlx5: Fix fence type for IB_WR_LOCAL_INV WR (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Removed unnecessary warnings in FEC caps query (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Fix selftest for small MTUs (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: RX, verify received packet size in Linear Striding RQ (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Apply the correct check for supporting TC esw rules split (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Adjust to max number of channles when re-attaching (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Always use the match level enum when parsing TC rule match (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Claim TC hw offloads support only under a proper build config (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Don't match on vlan non-existence if ethertype is wildcarded (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: IPoIB, Reset QP after channels are closed (Alaa Hleihel) [1658085]
- [netdrv] net/mlx4: Fix UBSAN warning of signed integer overflow (Alaa Hleihel) [1658085]
- [netdrv] net/mlx4_core: Fix uninitialized variable compilation warning (Alaa Hleihel) [1658085]
- [netdrv] net/mlx4_core: Zero out lkey field in SW2HW_MPT fw command (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Fix MR cache initialization (Alaa Hleihel) [1658085]
- [infiniband] RDMA/mlx5: Remove extraneous error check (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Take only bit 24-26 of wqe.pftype_wq for page fault type (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Fix memory leak when setting fpga ipsec caps (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Unmap DMA addr from HCA before IOMMU (Alaa Hleihel) [1658085]
- [infiniband] RDMA/mlx5: Remove superfluous version print (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Allow transition of DCI QP to reset (Alaa Hleihel) [1658085]
- [infiniband] IB/mlx5: Don't hold spin lock while checking device state (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Move mlx5e_priv_flags into en_ethtool.c (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5: Fix atomic_mode enum values (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: Delete unneeded function argument (Alaa Hleihel) [1658085]
- [netdrv] net/mlx5e: RX, Prefetch the xdp_frame data area (Alaa Hleihel) [1658085]
- [drm] drm/i915: Synchronize hpd work in i915_hpd_storm_ctl_show() (Lyude Paul) [1658376]
- [drm] drm/i915: Add short HPD IRQ storm detection for non-MST systems (Lyude Paul) [1658376]
- [drm] drm/i915: Clarify flow for disabling IRQs on storms (Lyude Paul) [1658376]
- [drm] drm/i915: Fix threshold check in intel_hpd_irq_storm_detect() (Lyude Paul) [1658376]
- [drm] drm/i915: Fix NULL deref when re-enabling HPD IRQs on systems with MST (Lyude Paul) [1658376]
- [drm] drm/i915: Fix possible race in intel_dp_add_mst_connector() (Lyude Paul) [1658376]
- [x86] kvm: x86: bump KVM_(SOFT_)MAX_VCPUS to 384 (Radim Krcmar) [1635205]
- [block] blk-mq: punt failed direct issue to dispatch list (Ming Lei) [1656653]
- [block] blk-mq: fix corruption with direct issue (Ming Lei) [1656653]
- [pci] PCI: Add support for Immediate Readiness (Myron Stowe) [1483409]
- [x86] x86/PCI: Remove node-local allocation when initialising host controller (Myron Stowe) [1483409]
- [arm64] arm64: PCI: Remove node-local allocations when initialising host controller (Myron Stowe) [1483409]
- [cpufreq] cpufreq: intel_pstate: Add base_frequency attribute (Prarit Bhargava) [1648207]
- [acpi] ACPI / CPPC: Add support for guaranteed performance (Prarit Bhargava) [1648207]
- [block] block: fix single range discard merge (Ming Lei) [1654096]
- [scsi] SCSI: fix queue cleanup race before queue initialization is done (Ming Lei) [1642404]
- [netdrv] net: hinic: fix null pointer dereference on pointer hwdev (Xiaojun Tan) [1654207]
- [netdrv] net-next/hinic: fix a bug in rx data flow (Xiaojun Tan) [1654207]
- [netdrv] net-next/hinic:fix a bug in set mac address (Xiaojun Tan) [1654207]
- [netdrv] net-next/hinic:add rx checksum offload for HiNIC (Xiaojun Tan) [1654207]
- [netdrv] net-next/hinic:replace multiply and division operators (Xiaojun Tan) [1654207]
- [netdrv] hinic: Fix l4_type parameter in hinic_task_set_tunnel_l4 (Xiaojun Tan) [1654207]
- [netdrv] net-next/hinic: add checksum offload and TSO support (Xiaojun Tan) [1654207]
- [netdrv] cxgb4: Remove SGE_HOST_PAGE_SIZE dependency on page size (Arjun Vynipadath) [1651082]

* Thu Dec 13 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-53.el8]
- [x86] kvm: x86: Report STIBP on GET_SUPPORTED_CPUID (Eduardo Habkost) [1644870]
- [kernel] power: remove possible deadlock when unregistering power_supply (Benjamin Tissoires) [1657623]
- [md] dm: call blk_queue_split() to impose device limits on bios (Mike Snitzer) [1657340]
- [pinctrl] Revert "pinctrl: intel: Do pin translation when lock IRQ" (Benjamin Tissoires) [1658075]
- [pinctrl] pinctrl: cannonlake: Fix HOSTSW_OWN register offset of H variant (Benjamin Tissoires) [1658075]
- [pinctrl] pinctrl: intel: Do pin translation in other GPIO operations as well (Benjamin Tissoires) [1658075]
- [pinctrl] pinctrl: cannonlake: Fix gpio base for GPP-E (Benjamin Tissoires) [1658075]
- [pinctrl] pinctrl: intel: Don't shadow error code of gpiochip_lock_as_irq() (Benjamin Tissoires) [1658075]
- [pinctrl] pinctrl: cannonlake: Fix community ordering for H variant (Benjamin Tissoires) [1658075]
- [pinctrl] pinctrl: intel: Do pin translation when lock IRQ (Benjamin Tissoires) [1658075]
- [firmware] efi: Prevent GICv3 WARN() by mapping the memreserve table before first use (Bhupesh Sharma) [1638640]
- [firmware] efi: Permit calling efi_mem_reserve_persistent() from atomic context (Bhupesh Sharma) [1638640]
- [firmware] efi/arm: Defer persistent reservations until after paging_init() (Bhupesh Sharma) [1638640]
- [firmware] efi/arm: Revert deferred unmap of early memmap mapping (Bhupesh Sharma) [1638640]
- [arm64] arm64: memblock: don't permit memblock resizing until linear mapping is up (Bhupesh Sharma) [1638640]
- [arm64] arm64: Fix /proc/iomem for reserved but not memory regions (Bhupesh Sharma) [1638640]
- [tty] tty: wipe buffer. (Christoph von Recklinghausen) [1655051]
- [tty] tty: wipe buffer if not echoing data (Christoph von Recklinghausen) [1655051]

* Wed Dec 12 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-52.el8]
- [powerpc] powerpc/perf: Remove sched_task function defined for thread-imc (Steve Best) [1657153]
- [s390] Add reserved fields to mm_context_t (Philipp Rudo) [1656874]
- [s390] Add reserved fields to thread_struct (Philipp Rudo) [1656874]
- [documentation] kdump: correct crashkernel=auto threshold (Raghavendra Rao) [1656698]
- [fs] NFSv4.x: fix lock recovery during delegation recall (Steve Dickson) [1656410]
- [x86] x86/spec_ctrl: Synchronize RHEL8 percpu SPEC_CTRL MSR states with new STIBP logic (Waiman Long) [1655662]
- [x86] x86/speculation: Provide IBPB always command line options (Waiman Long) [1655662]
- [x86] x86/speculation: Add seccomp Spectre v2 user space protection mode (Waiman Long) [1655662]
- [x86] x86/speculation: Enable prctl mode for spectre_v2_user (Waiman Long) [1655662]
- [x86] x86/speculation: Add prctl() control for indirect branch speculation (Waiman Long) [1655662]
- [x86] x86/speculation: Prepare arch_smt_update() for PRCTL mode (Waiman Long) [1655662]
- [x86] x86/speculation: Prevent stale SPEC_CTRL msr content (Waiman Long) [1655662]
- [x86] x86/speculation: Split out TIF update (Waiman Long) [1655662]
- [x86] ptrace: Remove unused ptrace_may_access_sched() and MODE_IBRS (Waiman Long) [1655662]
- [x86] x86/speculation: Prepare for conditional IBPB in switch_mm() (Waiman Long) [1655662]
- [x86] x86/speculation: Avoid __switch_to_xtra() calls (Waiman Long) [1655662]
- [x86] x86/process: Consolidate and simplify switch_to_xtra() code (Waiman Long) [1655662]
- [x86] x86/speculation: Prepare for per task indirect branch speculation control (Waiman Long) [1655662]
- [x86] x86/speculation: Add command line control for indirect branch speculation (Waiman Long) [1655662]
- [x86] x86/speculation: Unify conditional spectre v2 print functions (Waiman Long) [1655662]
- [x86] x86/speculataion: Mark command line parser data __initdata (Waiman Long) [1655662]
- [x86] x86/speculation: Mark string arrays const correctly (Waiman Long) [1655662]
- [x86] x86/speculation: Reorder the spec_v2 code (Waiman Long) [1655662]
- [x86] x86/l1tf: Show actual SMT state (Waiman Long) [1655662]
- [x86] x86/speculation: Rework SMT state change (Waiman Long) [1655662]
- [x86] sched/smt: Expose sched_smt_present static key (Waiman Long) [1655662]
- [x86] x86/Kconfig: Select SCHED_SMT if SMP enabled (Waiman Long) [1655662]
- [x86] sched/smt: Make sched_smt_present track topology (Waiman Long) [1655662]
- [x86] x86/speculation: Reorganize speculation control MSRs update (Waiman Long) [1655662]
- [x86] x86/speculation: Rename SSBD update functions (Waiman Long) [1655662]
- [x86] x86/speculation: Disable STIBP when enhanced IBRS is in use (Waiman Long) [1655662]
- [x86] x86/speculation: Move STIPB/IBPB string conditionals out of cpu_show_common() (Waiman Long) [1655662]
- [x86] x86/speculation: Remove unnecessary ret variable in cpu_show_common() (Waiman Long) [1655662]
- [x86] x86/speculation: Clean up spectre_v2_parse_cmdline() (Waiman Long) [1655662]
- [x86] x86/speculation: Update the TIF_SSBD comment (Waiman Long) [1655662]
- [x86] x86/retpoline: Remove minimal retpoline support (Waiman Long) [1655662]
- [x86] x86/retpoline: Make CONFIG_RETPOLINE depend on compiler support (Waiman Long) [1655662]
- [x86] x86/spec_ctrl: Temporarily remove the IBRS code from process.c & bugs.c (Waiman Long) [1655662]
- [nvme] nvme: flush namespace scanning work just before removing namespaces (Ewan Milne) [1656028]
- [netdrv] i40e: Fix deletion of MAC filters (Stefan Assmann) [1646847]
- [scsi] mpt3sas: Display message on Configurable secure HBA (Tomas Henzl) [1649314]
- [scsi] scsi: mpt3sas: Add support for Aero controllers (Tomas Henzl) [1649314]
- [scsi] scsi: mpt3sas: Update MPI headers to support Aero controllers (Tomas Henzl) [1649314]
- [scsi] megaraid_sas: Add support for MegaRAID Aero controllers (Tomas Henzl) [1649384]
- [netdrv] nfp: flower: enabled offloading of Team LAG (Pablo Cascon) [1649876]
- [netdrv] net/mlx5: IPSec, Fix the SA context hash key (Alaa Hleihel) [1645857]
- [hwmon] hwmon/k10temp: Add support for AMD family 17h, model 30h CPUs (Gary Hook) [1640681]
- [x86] x86/amd_nb: Add PCI device IDs for family 17h, model 30h (Gary Hook) [1640681]
- [x86] x86/amd_nb: Add support for newer PCI topologies (Gary Hook) [1640681]
- [hwmon] hwmon/k10temp, x86/amd_nb: Consolidate shared device IDs (Gary Hook) [1640681]
- [net] tipc: fix info leak from kernel tipc_event (Jon Maloy) [1643279]
- [net] tipc: eliminate message disordering during binding table update (Jon Maloy) [1643279]
- [net] tipc: fix unsafe rcu locking when accessing publication list (Jon Maloy) [1643279]
- [net] tipc: queue socket protocol error messages into socket receive buffer (Jon Maloy) [1643279]
- [net] tipc: ignore STATE_MSG on wrong link session (Jon Maloy) [1643279]
- [net] tipc: fix failover problem (Jon Maloy) [1643279]
- [net] tipc: eliminate possible recursive locking detected by LOCKDEP (Jon Maloy) [1643279]
- [net] tipc: lock wakeup & inputq at tipc_link_reset() (Jon Maloy) [1643279]
- [net] tipc: reset bearer if device carrier not ok (Jon Maloy) [1643279]
- [net] tipc: fix flow control accounting for implicit connect (Jon Maloy) [1643279]
- [net] tipc: check return value of __tipc_dump_start() (Jon Maloy) [1643279]
- [net] tipc: call start and done ops directly in __tipc_nl_compat_dumpit() (Jon Maloy) [1643279]
- [net] tipc: orphan sock in tipc_release() (Jon Maloy) [1643279]
- [net] tipc: switch to rhashtable iterator (Jon Maloy) [1643279]
- [net] tipc: fix a missing rhashtable_walk_exit() (Jon Maloy) [1643279]
- [net] tipc: add missing dev_put() on error in tipc_enable_l2_media (Jon Maloy) [1643279]
- [net] tipc: initialize broadcast link stale counter correctly (Jon Maloy) [1643279]
- [net] tipc: set link tolerance correctly in broadcast link (Jon Maloy) [1643279]
- [net] tipc: extend link reset criteria for stale packet retransmission (Jon Maloy) [1643279]
- [crypto] crypto: ccp - Add support for new CCP/PSP device ID (Gary Hook) [1634201]
- [crypto] crypto: ccp - Support register differences between PSP devices (Gary Hook) [1634201]
- [crypto] crypto: ccp - Remove unused #defines (Gary Hook) [1634201]
- [crypto] crypto: ccp - Add psp enabled message when initialization succeeds (Gary Hook) [1634201]
- [crypto] crypto: ccp - Fix command completion detection race (Gary Hook) [1634201]
- [crypto] crypto: ccp - Check for NULL PSP pointer at module unload (Gary Hook) [1634201]
- [net] sctp: increase sk_wmem_alloc when head->truesize is increased (Xin Long) [1645419]
- [net] sctp: count sk_wmem_alloc by skb truesize in sctp_packet_transmit (Xin Long) [1645419]
- [net] ipv6: re-do dad when interface has IFF_NOARP flag change (Hangbin Liu) [1644594]
- [net] netfilter: nf_tables: don't skip inactive chains during update (Florian Westphal) [1643746]
- [net] inet: frags: better deal with smp races (Sabrina Dubroca) [1645397]
- [net] geneve, vxlan: Don't set exceptions if skb->len < mtu (Xin Long) [1642842]
- [net] geneve, vxlan: Don't check skb_dst() twice (Xin Long) [1642842]
- [net] sctp: fix strchange_flags name for Stream Change Event (Xin Long) [1641852]
- [net] sctp: update dst pmtu with the correct daddr (Xin Long) [1644478]
- [net] sctp: not free the new asoc when sctp_wait_for_connect returns err (Xin Long) [1644155]
- [net] l2tp: fix a sock refcnt leak in l2tp_tunnel_register (Xin Long) [1642749]
- [net] sctp: check policy more carefully when getting pr status (Xin Long) [1637786]
- [net] sctp: get pr_assoc and pr_stream all status with SCTP_PR_SCTP_ALL instead (Xin Long) [1637786]
- [net] ipv4/igmp: fix v1/v2 switchback timeout based on rfc3376, 8.12 (Hangbin Liu) [1638598]
- [net] netfilter: nft_compat: ebtables 'nat' table is normal chain type (Florian Westphal) [1645377]
- [net] sched: exclude TC from kABI guarantee (Ivan Vecera) [1628454]
- [net] netfilter: nft_set_rbtree: allow loose matching of closing element in interval (Phil Sutter) [1641993]
- [net] netfilter: xt_nat: fix DNAT target for shifted portmap ranges (Paolo Abeni) [1634258]
- [net] sched: Fix for duplicate class dump (Phil Sutter) [1631179]
- [x86] KVM: X86: Fix scan ioapic use-before-initialization (Bandan Das) [1653835] {CVE-2018-19407}

* Fri Dec 07 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-51.el8]
- [scsi] scsi: vmw_pscsi: Rearrange code to avoid multiple calls to free_irq during unload (Cathy Avery) [1590875]
- [netdrv] net/ibmvnic: Fix RTNL deadlock during device reset (Steve Best) [1656076]
- [s390] s390/qeth: fix length check in SNMP processing (Philipp Rudo) [1655612]
- [s390] s390/ism: clear dmbe_mask bit before SMC IRQ handling (Philipp Rudo) [1655611]
- [net] net/smc: use after free fix in smc_wr_tx_put_slot() (Philipp Rudo) [1655611]
- [net] net/smc: atomic SMCD cursor handling (Philipp Rudo) [1655611]
- [net] net/smc: add SMC-D shutdown signal (Philipp Rudo) [1655611]
- [net] net/smc: use queue pair number when matching link group (Philipp Rudo) [1655611]
- [net] net/smc: abort CLC connection in smc_release (Philipp Rudo) [1655611]
- [net] net/smc: unregister rkeys of unused buffer (Philipp Rudo) [1655611]
- [net] net/smc: add infrastructure to send delete rkey messages (Philipp Rudo) [1655611]
- [net] net/smc: avoid a delay by waiting for nothing (Philipp Rudo) [1655611]
- [net] net/smc: cleanup listen worker mutex unlocking (Philipp Rudo) [1655611]
- [net] net/smc: short wait for late smc_clc_wait_msg (Philipp Rudo) [1655611]
- [net] net/smc: no link delete for a never active link (Philipp Rudo) [1655611]
- [net] net/smc: allow fallback after clc timeouts (Philipp Rudo) [1655611]
- [net] net/smc: remove sock_error detour in clc-functions (Philipp Rudo) [1655611]
- [net] net/smc: make smc_lgr_free() static (Philipp Rudo) [1655611]
- [net] net/smc: cleanup tcp_listen_worker initialization (Philipp Rudo) [1655611]
- [net] net/smc: fix smc_buf_unuse to use the lgr pointer (Philipp Rudo) [1655611]
- [net] Revert "net: simplify sock_poll_wait" (Philipp Rudo) [1655611]
- [powerpc] powerpc/pseries: Fix unitialized timer reset on migration (Steve Best) [1655053]
- [powerpc] powerpc/pseries/mobility: Extend start/stop topology update scope (Steve Best) [1655053]
- [x86] Mark Intel Cascade Lake supported (Steve Best) [1641425]

* Wed Dec 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-50.el8]
- [x86] KVM: VMX: re-add ple_gap module parameter (Gary Hook) [1652953]
- [netdrv] tg3: Add PHY reset for 5717/5719/5720 in change ring and flow control paths (Steve Best) [1655515]
- [pci] PCI/ASPM: Do not initialize link state when aspm_disabled is set (Myron Stowe) [1655246]
- [pci] PCI/ACPI: Allow _OSC presence to be optional for PCI (Myron Stowe) [1655246]
- [pci] PCI/ACPI: Correct error message for ASPM disabling (Myron Stowe) [1655246]
- [pci] PCI/ASPM: Fix link_state teardown on device removal (Myron Stowe) [1655246]
- [netdrv] ice: Change req_speeds to be u16 (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix the bytecount sent to netdev_tx_sent_queue (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix tx_timeout in PF driver (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix napi delete calls for remove (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix typo in error message (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix flags for port VLAN (Jonathan Toppins) [1644403]
- [netdrv] ice: Remove duplicate addition of VLANs in replay path (Jonathan Toppins) [1644403]
- [netdrv] ice: Free VSI contexts during for unload (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix dead device link issue with flow control (Jonathan Toppins) [1644403]
- [netdrv] ice: Check for reset in progress during remove (Jonathan Toppins) [1644403]
- [netdrv] ice: Set carrier state and start/stop queues in rebuild (Jonathan Toppins) [1644403]
- [netdrv] virtchnl: Added support to exchange additional speed values (Jonathan Toppins) [1644403]
- [netdrv] ice: Poll for link status change (Jonathan Toppins) [1644403]
- [netdrv] ice: Allocate VF interrupts and set queue map (Jonathan Toppins) [1644403]
- [netdrv] ice: Introduce ice_dev_onetime_setup (Jonathan Toppins) [1644403]
- [netdrv] ice: Use capability count returned by the firmware (Jonathan Toppins) [1644403]
- [netdrv] ice: Update expected FW version (Jonathan Toppins) [1644403]
- [netdrv] ice: Change device ID define names to align with branding string (Jonathan Toppins) [1644403]
- [netdrv] ice: Make ice_msix_clean_rings static (Jonathan Toppins) [1644403]
- [netdrv] ice: Update version string (Jonathan Toppins) [1644403]
- [netdrv] ice: Use the right function to enable/disable VSI (Jonathan Toppins) [1644403]
- [netdrv] ice: Add more flexibility on how we assign an ITR index (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix potential null pointer issues (Jonathan Toppins) [1644403]
- [netdrv] ice: Add code to go from ICE_FWD_TO_VSI_LIST to ICE_FWD_TO_VSI (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix forward to queue group logic (Jonathan Toppins) [1644403]
- [netdrv] ice: Extend malicious operations detection logic (Jonathan Toppins) [1644403]
- [netdrv] ice: Notify VF of link status change (Jonathan Toppins) [1644403]
- [netdrv] ice: Implement virtchnl commands for AVF support (Jonathan Toppins) [1644403]
- [netdrv] ice: Add handlers for VF netdevice operations (Jonathan Toppins) [1644403]
- [netdrv] ice: Add support for VF reset events (Jonathan Toppins) [1644403]
- [netdrv] ice: Update VSI and queue management code to handle VF VSI (Jonathan Toppins) [1644403]
- [netdrv] ice: Add handler to configure SR-IOV (Jonathan Toppins) [1644403]
- [netdrv] ice: Add support to detect SR-IOV capability and mailbox queues (Jonathan Toppins) [1644403]
- [netdrv] ice: Fix error on driver remove (Jonathan Toppins) [1644403]
- [netdrv] ice: Add support for dynamic interrupt moderation (Jonathan Toppins) [1644403]
- [netdrv] ice: Align ice_reset_req enum values to hardware reset values (Jonathan Toppins) [1644403]
- [netdrv] ice: Implement ethtool hook for RSS switch (Jonathan Toppins) [1644403]
- [netdrv] ice: Split irq_tracker into sw_irq_tracker and hw_irq_tracker (Jonathan Toppins) [1644403]
- [netdrv] ice: Check for actual link state of port after reset (Jonathan Toppins) [1644403]
- [netdrv] ice: Implement VSI replay framework (Jonathan Toppins) [1644403]
- [netdrv] ice: Expand use of VSI handles part 2/2 (Jonathan Toppins) [1644403]
- [netdrv] ice: Expand use of VSI handles part 1/2 (Jonathan Toppins) [1644403]
- [netdrv] ice: Change pf state behavior to protect reset path (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 7/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 6/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 5/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 4/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 3/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 2/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: Move common functions out of ice_main.c part 1/7 (Jonathan Toppins) [1644403]
- [netdrv] ice: fix changing of ring descriptor size (ethtool -G) (Jonathan Toppins) [1644403]
- [netdrv] ice: Update to capabilities admin queue command (Jonathan Toppins) [1644403]
- [netdrv] ice: Query the Tx scheduler node before adding it (Jonathan Toppins) [1644403]
- [netdrv] ice: Update comment for ice_fltr_mgmt_list_entry (Jonathan Toppins) [1644403]
- [netdrv] ice: update fw version check logic (Jonathan Toppins) [1644403]
- [netdrv] ice: update branding strings and supported device ids (Jonathan Toppins) [1644403]
- [netdrv] ice: replace unnecessary memcpy with direct assignment (Jonathan Toppins) [1644403]
- [netdrv] ice: use [sr]q.count when checking if queue is initialized (Jonathan Toppins) [1644403]
- [netdrv] ice: remove ndo_poll_controller (Jonathan Toppins) [1644403]
- [fs] fanotify: fix handling of events on child sub-directory (Miklos Szeredi) [1652432]
- [fs] fsnotify: generalize handling of extra event flags (Miklos Szeredi) [1652432]
- [netdrv] net: hns3: add common validation in hclge_dcb (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: fix for multiple unmapping DMA problem (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: rename hns_nic_dma_unmap (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: add handling for big TX fragment (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: move DMA map into hns3_fill_desc (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: remove hns3_fill_desc_tso (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Resume promisc mode and vlan filter status after loopback test (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Resume promisc mode and vlan filter status after reset (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Enable promisc mode when mac vlan table is full (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for rx vlan id handle to support Rev 0x21 hardware (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add egress/ingress vlan filter for revision 0x21 (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Optimize for unicast mac vlan table (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix loss of coal configuration while doing reset (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Modify hns3_get_max_available_channels (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Change return type of hclge_tm_schd_info_update() (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for netdev not up problem when setting mtu (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for packet buffer setting bug (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Set extra mac address of pause param for HW (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix speed/duplex information loss problem when executing ethtool ethx cmd of VF (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add get_media_type ops support for VF (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Remove print messages for error packet (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add nic state check before calling netif_tx_wake_queue (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add handle for default case (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Unify the prefix of vf functions (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix tqp array traversal condition for vf (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix ets validate issue (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix parameter type for q_id in hclge_tm_q_to_qs_map_cfg() (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix client initialize state issue when roce client initialize failed (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Clear client pointer when initialize client failed or unintialize finished (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix cmdq registers initialization issue for vf (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for setting speed for phy failed problem (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Check hdev state when getting link status (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Set STATE_DOWN bit of hdev state when stopping net (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Remove packet statistics of public (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Remove tx budget to clean more TX descriptors in a napi (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Refine hns3_get_link_ksettings() (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Remove redundant codes of query advertised flow control abilitiy (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Change the dst mac addr of loopback packet (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Only update mac configuation when necessary (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Preserve vlan 0 in hardware table (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix ping exited problem when doing lp selftest (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for loopback selftest failed problem (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix error of checking used vlan id (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for multicast failure (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for vf vlan delete failed problem (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: modify variable type in hns3_nic_reuse_page (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add vlan filter setting by ethtool command -K (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Set tx ring' tc info when netdev is up (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix desc num set to default when setting channel (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for information of phydev lost problem when down/up (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add support for serdes loopback selftest (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Refine the MSIX allocation for PF (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix MSIX allocation issue for VF (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: fix return value error while hclge_cmd_csq_clean failed (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Modify inconsistent bit mask macros (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for using wrong mask and shift in hclge_get_ring_chain_from_mbx (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Correct reset event status register (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Prevent to request reset frequently (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Prevent sending command during global or core reset (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Add configure for mac minimal frame size (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for l4 checksum offload bug (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix for waterline not setting correctly (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: Fix tc setup when netdev is first up (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: modify hnae_ to hnae3_ (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: simplify hclge_cmd_csq_clean (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: remove some redundant assignments (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: remove back in struct hclge_hw (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: add unlikely for error check (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: add l4_type check for both ipv4 and ipv6 (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: add vector status check before free vector (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: rename the interface for init_client_instance and uninit_client_instance (Xiaojun Tan) [1640945]
- [netdrv] net: hns3: remove hclge_get_vector_index from hclge_bind_ring_with_vector (Xiaojun Tan) [1640945]
- [kernel] redhat: Enable -Werror for architectures (Laura Abbott) [1582754]
- [drm] drm/atomic_helper: Remove dangling variable (Laura Abbott) [1582754]
- [s390] s390/tools: fix gcc 8 stringop-truncation warnings (Laura Abbott) [1582754]
- [tty] kgdboc: Fix restrict error (Laura Abbott) [1582754]
- [misc] misc: kgdbts: Fix restrict error (Laura Abbott) [1582754]
- [scsi] scsi: ibmvscsis: Fix a stringop-overflow warning (Laura Abbott) [1582754]
- [s390] s390/extmem: fix gcc 8 stringop-overflow warning (Laura Abbott) [1582754]
- [s390] s390/perf: fix gcc 8 array-bounds warning (Laura Abbott) [1582754]
- [kernel] kdb: Use strscpy with destination buffer size (Laura Abbott) [1582754]
- [fs] configfs: replace strncpy with memcpy (Laura Abbott) [1582754]
- [fs] kernfs: Replace strncpy with memcpy (Laura Abbott) [1582754]
- [kernel] disable stringop truncation warnings for now (Laura Abbott) [1582754]
- [sound] ALSA: intel_hdmi: Use strlcpy() instead of strncpy() (Laura Abbott) [1582754]
- [sound] ALSA: trident: Suppress gcc string warning (Laura Abbott) [1582754]
- [lib] kobject: Replace strncpy with memcpy (Laura Abbott) [1582754]
- [tty] TTY: isdn: Replace strncpy with memcpy (Laura Abbott) [1582754]
- [target] scsi: target/iscsi: Make iscsit_ta_authentication() respect the output buffer size (Laura Abbott) [1582754]
- [fs] fuse: don't need GETATTR after every READ (Miklos Szeredi) [1650538]
- [fs] fuse: allow fine grained attr cache invaldation (Miklos Szeredi) [1650538]

* Tue Dec 04 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-49.el8]
- [mm] mm: mremap: properly flush TLB before releasing the page (Rafael Aquini) [1645122] {CVE-2018-18281}
- [x86] x86/spec_ctrl: Change default Skylake Spectre v2 mitigation to retpoline (Waiman Long) [1651806]
- [fs] gfs2: write revokes should traverse sd_ail1_list in reverse (Andreas Grunbacher) [1652763]
- [fs] gfs2: Fix marking bitmaps non-full (Andreas Grunbacher) [1652762]
- [fs] GFS2: Flush the GFS2 delete workqueue before stopping the kernel threads (Andreas Grunbacher) [1652761]
- [fs] gfs2: Don't leave s_fs_info pointing to freed memory in init_sbd (Andreas Grunbacher) [1652759]
- [fs] gfs2: Use fs_* functions instead of pr_* function where we can (Andreas Grunbacher) [1652757]
- [fs] gfs2: slow the deluge of io error messages (Andreas Grunbacher) [1652757]
- [fs] gfs2_meta: ->mount() can get NULL dev_name (Andreas Grunbacher) [1652754]
- [powerpc] powerpc/vdso: Correct call frame information (Steve Best) [1651281]
- [i2c] i2c: i801: Add support for Intel Ice Lake (David Arcari) [1637435]
- [usb] xhci: Add quirk to workaround the errata seen on Cavium Thunder-X2 Soc (Robert Richter) [1649829]
- [x86] x86: numa_emulation: fix uniform-split numa emulation (Rafael Aquini) [1620341]
- [x86] x86: numa_emulation: introduce uniform split capability (Rafael Aquini) [1620341]
- [kernel] perf/hw_breakpoint: Modify breakpoint even if the new attr has disabled set (Mark Salter) [1643174]
- [x86] KVM: vmx: hyper-v: don't pass EPT configuration info to vmx_hv_remote_flush_tlb() (Paolo Bonzini) [1636610]
- [x86] KVM: x86: support CONFIG_KVM_AMD=y with CONFIG_CRYPTO_DEV_CCP_DD=m (Paolo Bonzini) [1636610]
- [x86] kvm: nVMX: fix entry with pending interrupt if APICv is enabled (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: hide flexpriority from guest when disabled at the module level (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: check for existence of secondary exec controls before accessing (Paolo Bonzini) [1636610]
- [x86] KVM: x86: fix L1TF's MMIO GFN calculation (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: cut down decimal places in update interval dialog (Paolo Bonzini) [1636610]
- [x86] KVM: nVMX: Fix emulation of VM_ENTRY_LOAD_BNDCFGS (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Do not use kvm_x86_ops->mpx_supported() directly (Paolo Bonzini) [1636610]
- [x86] KVM: nVMX: Do not expose MPX VMX controls when guest MPX disabled (Paolo Bonzini) [1636610]
- [x86] KVM: x86: never trap MSR_KERNEL_GS_BASE (Paolo Bonzini) [1636610]
- [x86] KVM: LAPIC: Fix pv ipis out-of-bounds access (Paolo Bonzini) [1636610]
- [x86] KVM: nVMX: Fix loss of pending IRQ/NMI before entering L2 (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: re-animate display of dead guests (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: indicate dead guests as such (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: handle guest removals more gracefully (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: don't reset stats when setting PID filter for debugfs (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: fix updates for dead guests (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: fix handling of invalid paths in debugfs provider (Paolo Bonzini) [1636610]
- [tools] tools/kvm_stat: fix python3 issues (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Unexport x86_emulate_instruction() (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Rename emulate_instruction() to kvm_emulate_instruction() (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Do not re-{try, execute} after failed emulation in L2 (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Default to not allowing emulation retry in kvm_mmu_page_fault (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Merge EMULTYPE_RETRY and EMULTYPE_ALLOW_REEXECUTE (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Invert emulation re-execute behavior to make it opt-in (Paolo Bonzini) [1636610]
- [x86] KVM: x86: SVM: Set EMULTYPE_NO_REEXECUTE for RSM emulation (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: Do not allow reexecute_instruction() when skipping MMIO instr (Paolo Bonzini) [1636610]
- [x86] KVM: SVM: remove unused variable dst_vaddr_end (Paolo Bonzini) [1636610]
- [x86] KVM: nVMX: avoid redundant double assignment of nested_run_pending (Paolo Bonzini) [1636610]
- [x86] KVM: nVMX: Fix bad cleanup on error of get/set nested state IOCTLs (Paolo Bonzini) [1636610]
- [tools] kvm: selftests: Add platform_info_test (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Control guest reads of MSR_PLATFORM_INFO (Paolo Bonzini) [1636610]
- [x86] KVM: x86: Turbo bits in MSR_PLATFORM_INFO (Paolo Bonzini) [1636610]
- [x86] nVMX x86: Check VPID value on vmentry of L2 guests (Paolo Bonzini) [1636610]
- [x86] nVMX x86: check posted-interrupt descriptor addresss on vmentry of L2 (Paolo Bonzini) [1636610]
- [x86] KVM: nVMX: Wake blocked vCPU in guest-mode if pending interrupt in virtual APICv (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: check nested state and CR4.VMXE against SMM (Paolo Bonzini) [1636610]
- [x86] kvm: x86: make kvm_{load|put}_guest_fpu() static (Paolo Bonzini) [1636610]
- [x86] x86/hyper-v: rename ipi_arg_{ex, non_ex} structures (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: use preemption timer to force immediate VMExit (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: modify preemption timer bit only when arming timer (Paolo Bonzini) [1636610]
- [x86] KVM: VMX: immediately mark preemption timer expired only for zero value (Paolo Bonzini) [1636610]
- [x86] KVM: SVM: Switch to bitmap_zalloc() (Paolo Bonzini) [1636610]
- [lib] bitmap: Add bitmap_alloc(), bitmap_zalloc() and bitmap_free() (Paolo Bonzini) [1636610]
- [x86] KVM/MMU: Fix comment in walk_shadow_page_lockless_end() (Paolo Bonzini) [1636610]
- [tools] kvm: selftests: use -pthread instead of -lpthread (Paolo Bonzini) [1636610]
- [tools] kvm: selftest: add dirty logging test (Paolo Bonzini) [1636610]
- [tools] kvm: selftest: pass in extra memory when create vm (Paolo Bonzini) [1636610]
- [tools] kvm: selftest: include the tools headers (Paolo Bonzini) [1636610]
- [tools] kvm: selftest: unify the guest port macros (Paolo Bonzini) [1636610]
- [x86] KVM: x86: don't reset root in kvm_mmu_setup() (Paolo Bonzini) [1636610]
- [x86] kvm: mmu: Don't read PDPTEs when paging is not enabled (Paolo Bonzini) [1636610]
- [x86] x86/kvm/lapic: always disable MMIO interface in x2APIC mode (Paolo Bonzini) [1636610]
- [s390] KVM: s390: Make huge pages unavailable in ucontrol VMs (Paolo Bonzini) [1636610]
- [s390] s390/mm: Check for valid vma before zapping in gmap_discard (Paolo Bonzini) [1636610]
- [tools] selftests: add headers_install to lib.mk (Paolo Bonzini) [1636610]
- [tools] selftests: kselftest: Remove outdated comment (Paolo Bonzini) [1636610]
- [tools] selftests: android: move config up a level (Paolo Bonzini) [1636610]
- [md] md: Avoid namespace collision with bitmap API (Paolo Bonzini) [1636610]

* Fri Nov 30 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-48.el8]
- [cpufreq] cpufreq / CPPC: Add cpuinfo_cur_freq support for CPPC (Prarit Bhargava) [1654361]
- [netdrv] nfp: flower: add ipv6 set flow label and hop limit offload (Pablo Cascon) [1651639]
- [netdrv] nfp: flower: add ipv4 set ttl and tos offload (Pablo Cascon) [1651639]
- [netdrv] ibmvnic: Update driver queues after change in ring size support (Steve Best) [1651947]
- [netdrv] ibmvnic: Fix RX queue buffer cleanup (Steve Best) [1651947]
- [netdrv] net/ibmnvic: Fix deadlock problem in reset (Steve Best) [1651947]
- [netdrv] ibmvnic: fix accelerated VLAN handling (Steve Best) [1651947]
- [netdrv] ibmvnic: Add ethtool private flag for driver-defined queue limits (Steve Best) [1651947]
- [netdrv] ibmvnic: Introduce driver limits for ring sizes (Steve Best) [1651947]
- [netdrv] ibmvnic: Increase maximum queue size limit (Steve Best) [1651947]
- [netdrv] ibmvnic: remove ndo_poll_controller (Steve Best) [1651947]
- [powerpc] powerpc/powernv/npu: Remove atsd_threshold debugfs setting (Steve Best) [1653661]
- [powerpc] powerpc/powernv/npu: Use size-based ATSD invalidates (Steve Best) [1653661]
- [powerpc] powerpc/powernv/npu: Reduce eieio usage when issuing ATSD invalidates (Steve Best) [1653661]
- [powerpc] powerpc/powernv/npu: Add a debugfs setting to change ATSD threshold (Steve Best) [1653661]
- [net] libceph: fall back to sendmsg for slab pages (Ilya Dryomov) [1653395]
- [s390] s390/qeth: utilize virtual MAC for Layer2 OSD devices (Philipp Rudo) [1653246]
- [fs] vfs: fix FIGETBSZ ioctl on an overlayfs file (Miklos Szeredi) [1651362]
- [fs] ovl: fix decode of dir file handle with multi lower layers (Miklos Szeredi) [1651362]
- [fs] ovl: fix missing override creds in link of a metacopy upper (Miklos Szeredi) [1651362]
- [fs] ovl: automatically enable redirect_dir on metacopy=on (Miklos Szeredi) [1651362]
- [fs] ovl: check whiteout in ovl_create_over_whiteout() (Miklos Szeredi) [1651362]
- [fs] ovl: fix recursive oi->lock in ovl_link() (Miklos Szeredi) [1651362]
- [fs] ovl: fix error handling in ovl_verify_set_fh() (Miklos Szeredi) [1651362]
- [mm] mm, memory_hotplug: check zone_movable in has_unmovable_pages (Baoquan He) [1643839]
- [netdrv] hv_netvsc: fix vf serial matching with pci slot info (Vitaly Kuznetsov) [1637519]
- [netdrv] hv_netvsc: remove ndo_poll_controller (Vitaly Kuznetsov) [1637519]
- [netdrv] hv_netvsc: pair VF based on serial number (Vitaly Kuznetsov) [1637519]
- [netdrv] hv_netvsc: fix schedule in RCU context (Vitaly Kuznetsov) [1637519]
- [pci] PCI: hv: Fix return value check in hv_pci_assign_slots() (Vitaly Kuznetsov) [1637519]
- [pci] PCI: hv: support reporting serial number as slot information (Vitaly Kuznetsov) [1637519]
- [pci] PCI: hv: Replace GFP_ATOMIC with GFP_KERNEL in new_pcichild_device() (Vitaly Kuznetsov) [1637519]
- [char] ipmi: Fix timer race with module unload (Robert Richter) [1649812]
- [arm64] arm64: hugetlb: Avoid unnecessary clearing in huge_ptep_set_access_flags (Christoph von Recklinghausen) [1635192]
- [arm64] arm64: hugetlb: Fix handling of young ptes (Christoph von Recklinghausen) [1635192]
- [mm] mm: Preserve _PAGE_DEVMAP across mprotect() calls (Jeff Moyer) [1647647]

* Thu Nov 29 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-47.el8]
- [crypto] crypto: vmx - Fix sleep-in-atomic bugs (Steve Best) [1653662]
- [netdrv] net: ena: update driver version from 2.0.1 to 2.0.2 (John Linville) [1634044]
- [netdrv] net: ena: fix crash during ena_remove() (John Linville) [1634044]
- [netdrv] net: ena: fix crash during failed resume from hibernation (John Linville) [1634044]
- [netdrv] net: ena: enable CONFIG_ENA_ETHERNET for aarch64 (John Linville) [1634044]
- [netdrv] net: ena: enable Low Latency Queues (John Linville) [1634044]
- [netdrv] net: ena: Fix Kconfig dependency on X86 (John Linville) [1634044]
- [netdrv] net: ena: fix indentations in ena_defs for better readability (John Linville) [1634044]
- [netdrv] net: ena: update driver version to 2.0.1 (John Linville) [1634044]
- [netdrv] net: ena: remove redundant parameter in ena_com_admin_init() (John Linville) [1634044]
- [netdrv] net: ena: change rx copybreak default to reduce kernel memory pressure (John Linville) [1634044]
- [netdrv] net: ena: limit refill Rx threshold to 256 to avoid latency issues (John Linville) [1634044]
- [netdrv] net: ena: explicit casting and initialization, and clearer error handling (John Linville) [1634044]
- [netdrv] net: ena: use CSUM_CHECKED device indication to report skb's checksum status (John Linville) [1634044]
- [netdrv] net: ena: add functions for handling Low Latency Queues in ena_netdev (John Linville) [1634044]
- [netdrv] net: ena: add functions for handling Low Latency Queues in ena_com (John Linville) [1634044]
- [netdrv] net: ena: introduce Low Latency Queues data structures according to ENA spec (John Linville) [1634044]
- [netdrv] net: ena: complete host info to match latest ENA spec (John Linville) [1634044]
- [netdrv] net: ena: minor performance improvement (John Linville) [1634044]
- [netdrv] net: ena: fix auto casting to boolean (John Linville) [1634044]
- [netdrv] net: ena: fix NULL dereference due to untimely napi initialization (John Linville) [1634044]
- [netdrv] net: ena: fix rare bug when failed restart/resume is followed by driver removal (John Linville) [1634044]
- [netdrv] net: ena: fix warning in rmmod caused by double iounmap (John Linville) [1634044]
- [netdrv] net: ena: remove ndo_poll_controller (John Linville) [1634044]
- [netdrv] net: ena: fix incorrect usage of memory barriers (John Linville) [1634044]
- [netdrv] net: ena: fix missing calls to READ_ONCE (John Linville) [1634044]
- [netdrv] net: ena: fix missing lock during device destruction (John Linville) [1634044]
- [netdrv] net: ena: fix potential double ena_destroy_device() (John Linville) [1634044]
- [netdrv] net: ena: fix device destruction to gracefully free resources (John Linville) [1634044]
- [netdrv] net: ena: fix driver when PAGE_SIZE == 64kB (John Linville) [1634044]
- [netdrv] net: ena: fix surprise unplug NULL dereference kernel crash (John Linville) [1634044]
- [s390] s390/zcrypt: reinit ap queue state machine during device probe (Philipp Rudo) [1653668]
- [s390] s390/kdump: Make elfcorehdr size calculation ABI compliant (Philipp Rudo) [1653245]
- [s390] s390/kdump: Fix elfcorehdr size calculation (Philipp Rudo) [1653245]
- [block] block: fix 32 bit overflow in __blkdev_issue_discard() (Ming Lei) [1638826]
- [ata] libata: blacklist SAMSUNG MZ7TD256HAFV-000L9 SSD (Ming Lei) [1638826]
- [block] block: copy ioprio in __bio_clone_fast() and bounce (Ming Lei) [1638826]
- [trace] kyber: fix wrong strlcpy() size in trace_kyber_latency() (Ming Lei) [1638826]
- [block] floppy: fix race condition in __floppy_read_block_0() (Ming Lei) [1638826]
- [block] block: make blk_try_req_merge() static (Ming Lei) [1638826]
- [block] block: remove dead queue members (Ming Lei) [1638826]
- [block] block: clean up dead code that is now redundant (Ming Lei) [1638826]
- [nvme] nvme: fix boot hang with only being able to get one IRQ vector (Ming Lei) [1638826]
- [block] ide: don't clear special on ide_queue_rq() entry (Ming Lei) [1638826]
- [block] null_blk: remove unused nullb device (Ming Lei) [1638826]
- [block] ide: don't use req->special (Ming Lei) [1638826]
- [block] pd: replace ->special use with private data in the request (Ming Lei) [1638826]
- [block] aoe: replace ->special use with private data in the request (Ming Lei) [1638826]
- [block] skd_main: don't use req->special (Ming Lei) [1638826]
- [block] nullb: remove leftover legacy request code (Ming Lei) [1638826]
- [scsi] fnic: fix fnic_scsi_host_{start,end}_tag (Ming Lei) [1638826]
- [block] block: remove set but not used variable 'et' (Ming Lei) [1638826]
- [block] block: remove the BLKPREP_* values. (Ming Lei) [1638826]
- [scsi] scsi: return blk_status_t from device handler ->prep_fn (Ming Lei) [1638826]
- [scsi] scsi: return blk_status_t from scsi_init_io and ->init_command (Ming Lei) [1638826]
- [scsi] scsi: clean up error handling in scsi_init_io (Ming Lei) [1638826]
- [scsi] scsi: push blk_status_t up into scsi_setup_{fs,scsi}_cmnd (Ming Lei) [1638826]
- [scsi] scsi: simplify scsi_prep_state_check (Ming Lei) [1638826]
- [block] ide: cleanup ->prep_rq calling convention (Ming Lei) [1638826]
- [block] block: remove req->timeout_list (Ming Lei) [1638826]
- [block] blk-mq: provide a helper to check if a queue is busy (Ming Lei) [1638826]
- [block] blk-mq-tag: change busy_iter_fn to return whether to continue or not (Ming Lei) [1638826]
- [block] ms_block: remove unused pointer 'set' (Ming Lei) [1638826]
- [block] sunvdc: fix compiler warning (Ming Lei) [1638826]
- [nvme] nvme: add separate poll queue map (Ming Lei) [1638826]
- [block] block: add REQ_HIPRI and inherit it from IOCB_HIPRI (Ming Lei) [1638826]
- [nvme] nvme: utilize two queue maps, one for reads and one for writes (Ming Lei) [1638826]
- [block] blk-mq: initial support for multiple queue maps (Ming Lei) [1638826]
- [block] blk-mq: improve plug list sorting (Ming Lei) [1638826]
- [block] blk-mq: cleanup and improve list insertion (Ming Lei) [1638826]
- [block] blk-mq: cache request hardware queue mapping (Ming Lei) [1638826]
- [block] blk-mq: separate number of hardware queues from nr_cpu_ids (Ming Lei) [1638826]
- [block] blk-mq: support multiple hctx maps (Ming Lei) [1638826]
- [block] blk-mq: add 'type' attribute to the sysfs hctx directory (Ming Lei) [1638826]
- [block] blk-mq: allow software queue to map to multiple hardware queues (Ming Lei) [1638826]
- [block] blk-mq: pass in request/bio flags to queue mapping (Ming Lei) [1638826]
- [block] blk-mq: provide dummy blk_mq_map_queue_type() helper (Ming Lei) [1638826]
- [block] blk-mq: abstract out queue map (Ming Lei) [1638826]
- [block] blk-mq: kill q->mq_map (Ming Lei) [1638826]
- [kernel] genirq/affinity: Add support for allocating interrupt sets (Ming Lei) [1638826]
- [kernel] genirq/affinity: Pass first vector to __irq_build_affinity_masks() (Ming Lei) [1638826]
- [kernel] genirq/affinity: Move two stage affinity spreading into a helper function (Ming Lei) [1638826]
- [kernel] genirq/affinity: Spread IRQs to all available NUMA nodes (Ming Lei) [1638826]
- [block] block: kill request ->cpu member (Ming Lei) [1638826]
- [block] block: get rid of q->softirq_done_fn() (Ming Lei) [1638826]
- [block] block: get rid of blk_queued_rq() (Ming Lei) [1638826]
- [block] blk-merge: kill dead queue lock held check (Ming Lei) [1638826]
- [block] block: remove req_no_special_merge() from merging code (Ming Lei) [1638826]
- [block] block: kill request slab cache (Ming Lei) [1638826]
- [block] block: remove request_list code (Ming Lei) [1638826]
- [block] bsg: move bsg-lib parts outside of request queue (Ming Lei) [1638826]
- [block] block: kill legacy parts of timeout handling (Ming Lei) [1638826]
- [block] block: remove __blk_put_request() (Ming Lei) [1638826]
- [block] block: get rid of MQ scheduler ops union (Ming Lei) [1638826]
- [block] block: remove dead elevator code (Ming Lei) [1638826]
- [block] block: remove legacy IO schedulers (Ming Lei) [1638826]
- [block] block: cleanup kick/queued handling (Ming Lei) [1638826]
- [block] block: remove non mq parts from the flush code (Ming Lei) [1638826]
- [block] block: remove legacy rq tagging (Ming Lei) [1638826]
- [block] blk-cgroup: remove legacy queue bypassing (Ming Lei) [1638826]
- [block] blk-wbt: kill check for legacy queue type (Ming Lei) [1638826]
- [block] block: remove blk_complete_request() (Ming Lei) [1638826]
- [block] bsg: convert to use blk-mq (Ming Lei) [1638826]
- [block] bsg: provide bsg_remove_queue() helper (Ming Lei) [1638826]
- [block] bsg: pass in desired timeout handler (Ming Lei) [1638826]
- [s390] dasd: remove dead code (Ming Lei) [1638826]
- [block] block: remove q->lld_busy_fn() (Ming Lei) [1638826]
- [scsi] scsi: kill off the legacy IO path (Ming Lei) [1638826]
- [scsi] scsi: provide mq_ops->busy() hook (Ming Lei) [1638826]
- [block] blk-mq: provide mq_ops->busy() hook (Ming Lei) [1638826]
- [block] blk-mq: remove legacy check in queue blk_freeze_queue() (Ming Lei) [1638826]
- [block] blk-mq: remove the request_list usage (Ming Lei) [1638826]
- [block] ide: convert to blk-mq (Ming Lei) [1638826]
- [block] mspro_block: convert to blk-mq (Ming Lei) [1638826]
- [block] ms_block: convert to blk-mq (Ming Lei) [1638826]
- [block] sunvdc: convert to blk-mq (Ming Lei) [1638826]
- [block] null_blk: Add conventional zone configuration for zoned support (Ming Lei) [1638826]
- [ata] libata: Apply NOLPM quirk for SAMSUNG MZ7TD256HAFV-000L9 (Ming Lei) [1638826]
- [block] block, bfq: fix asymmetric scenarios detection (Ming Lei) [1638826]
- [cdrom] gdrom: fix mistake in assignment of error (Ming Lei) [1638826]
- [block] blk-mq: place trace_block_getrq() in correct place (Ming Lei) [1638826]
- [block] block: Introduce blk_revalidate_disk_zones() (Ming Lei) [1638826]
- [block] block: add a report_zones method (Ming Lei) [1638826]
- [block] block: Expose queue nr_zones in sysfs (Ming Lei) [1638826]
- [block] block: Improve zone reset execution (Ming Lei) [1638826]
- [block] block: Introduce BLKGETNRZONES ioctl (Ming Lei) [1638826]
- [block] block: Introduce BLKGETZONESZ ioctl (Ming Lei) [1638826]
- [block] block: Limit allocation of zone descriptors for report zones (Ming Lei) [1638826]
- [block] block: Introduce blkdev_nr_zones() helper (Ming Lei) [1638826]
- [scsi] scsi: sd_zbc: Fix sd_zbc_check_zones() error checks (Ming Lei) [1638826]
- [scsi] scsi: sd_zbc: Reduce boot device scan and revalidate time (Ming Lei) [1638826]
- [scsi] scsi: sd_zbc: Rearrange code (Ming Lei) [1638826]
- [scsi] scsi: sd_zbc: Remove an assignment from sd_zbc_setup_report_cmnd() (Ming Lei) [1638826]
- [scsi] scsi: sd: don't crash the host on invalid commands (Ming Lei) [1638826]
- [pci] PCI/MSI: Warn and return error if driver enables MSI/MSI-X twice (Ming Lei) [1638826]
- [fs] f2fs: remove request_list check in is_idle() (Ming Lei) [1638826]
- [scsi] scsi: osd: initiator should use mq variant of request ending (Ming Lei) [1638826]
- [scsi] scsi: fnic: replace gross legacy tag hack with blk-mq hack (Ming Lei) [1638826]
- [infiniband] ib_srp: Remove WARN_ON in srp_terminate_io() (Ming Lei) [1638826]
- [scsi] scsi: ufs: Disable blk-mq for now (Ming Lei) [1638826]
- [block] sx8: convert to blk-mq (Ming Lei) [1638826]
- [block] z2ram: convert to blk-mq (Ming Lei) [1638826]
- [cdrom] gdrom: convert to blk-mq (Ming Lei) [1638826]
- [block] floppy: convert to blk-mq (Ming Lei) [1638826]
- [block] ataflop: convert to blk-mq (Ming Lei) [1638826]
- [block] ataflop: fix error handling during setup (Ming Lei) [1638826]
- [block] ataflop: fold headers into C file (Ming Lei) [1638826]
- [block] amiflop: convert to blk-mq (Ming Lei) [1638826]
- [block] amiflop: clean up on errors during setup (Ming Lei) [1638826]
- [block] amiflop: fold headers into C file (Ming Lei) [1638826]
- [block] swim3: convert to blk-mq (Ming Lei) [1638826]
- [block] swim3: add real error handling in setup (Ming Lei) [1638826]
- [block] swim: convert to blk-mq (Ming Lei) [1638826]
- [block] swim: fix cleanup on setup error (Ming Lei) [1638826]
- [mtd] mtd_blkdevs: convert to blk-mq (Ming Lei) [1638826]
- [block] xsysace: convert to blk-mq (Ming Lei) [1638826]
- [block] paride: convert pf to blk-mq (Ming Lei) [1638826]
- [block] paride: convert pd to blk-mq (Ming Lei) [1638826]
- [block] paride: convert pcd to blk-mq (Ming Lei) [1638826]
- [block] ps3disk: convert to blk-mq (Ming Lei) [1638826]
- [block] blk-mq: provide helper for setting up an SQ queue and tag set (Ming Lei) [1638826]
- [block] null_blk: remove set but not used variable 'q' (Ming Lei) [1638826]
- [cdrom] cdrom: don't attempt to fiddle with cdo->capability (Ming Lei) [1638826]
- [block] block: remove bogus check for queue_lock assignment (Ming Lei) [1638826]
- [block] null_blk: remove legacy IO path (Ming Lei) [1638826]
- [block] um: Convert ubd driver to blk-mq (Ming Lei) [1638826]
- [block] skd: fixup usage of legacy IO API (Ming Lei) [1638826]
- [block] aoe: convert aoeblk to blk-mq (Ming Lei) [1638826]
- [block] ide: remove redundant variables queue_run_ms and left (Ming Lei) [1638826]
- [scsi] scsi: core: scsi_io_completion convert BUGs to WARNs (Ming Lei) [1638826]
- [scsi] scsi: core: scsi_io_completion hints on fastpath (Ming Lei) [1638826]
- [scsi] scsi: core: add scsi_io_completion_reprep helper (Ming Lei) [1638826]
- [scsi] scsi: core: add scsi_io_completion_action helper (Ming Lei) [1638826]
- [scsi] scsi: core: add scsi_io_completion_nz_result function (Ming Lei) [1638826]
- [scsi] scsi: core: scsi_io_completion: rename variables (Ming Lei) [1638826]
- [scsi] scsi: core: scsi_io_completion: comment on end_request return (Ming Lei) [1638826]
- [scsi] scsi: core: use blk_mq_run_hw_queues in scsi_kick_queue (Ming Lei) [1638826]
- [scsi] scsi: sg: remove bad blk_end_request_all() call (Ming Lei) [1638826]
- [block] blk-mq: complete req in softirq context in case of single queue (Ming Lei) [1638826]
- [block] block, bfq: improve asymmetric scenarios detection (Ming Lei) [1638826]
- [block] block: remove redundant 'default n' from Kconfig-s (Ming Lei) [1638826]
- [block] blk-mq-debugfs: Also show requests that have not yet been started (Ming Lei) [1638826]
- [block] block: Finish renaming REQ_DISCARD into REQ_OP_DISCARD (Ming Lei) [1638826]
- [block] kyber: fix integer overflow of latency targets on 32-bit (Ming Lei) [1638826]
- [block] kyber: add tracepoints (Ming Lei) [1638826]
- [block] kyber: implement improved heuristics (Ming Lei) [1638826]
- [block] kyber: don't make domain token sbitmap larger than necessary (Ming Lei) [1638826]
- [block] block: export blk_stat_enable_accounting() (Ming Lei) [1638826]
- [block] block: move call of scheduler's ->completed_request() hook (Ming Lei) [1638826]
- [block] blk-mq: Enable support for runtime power management (Ming Lei) [1638826]
- [block] block: Make blk_get_request() block for non-PM requests while suspended (Ming Lei) [1638826]
- [block] block: Allow unfreezing of a queue while requests are in progress (Ming Lei) [1638826]
- [lib] percpu-refcount: Introduce percpu_ref_resurrect() (Ming Lei) [1638826]
- [block] block: Schedule runtime resume earlier (Ming Lei) [1638826]
- [block] block: Split blk_pm_add_request() and blk_pm_put_request() (Ming Lei) [1638826]
- [block] block, scsi: Change the preempt-only flag into a counter (Ming Lei) [1638826]
- [block] block: Move power management code into a new source file (Ming Lei) [1638826]
- [block] Blk-throttle: update to use rbtree with leftmost node cached (Ming Lei) [1638826]
- [block] block: use bio_add_page in bio_iov_iter_get_pages (Ming Lei) [1638826]
- [block] blok, bfq: do not plug I/O if all queues are weight-raised (Ming Lei) [1638826]
- [block] block, bfq: inject other-queue I/O into seeky idle queues on NCQ flash (Ming Lei) [1638826]
- [block] block, bfq: correctly charge and reset entity service in all cases (Ming Lei) [1638826]

* Wed Nov 28 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-46.el8]
- [rpmspec] redhat: fix bpf_samples build (Jiri Benc) [1611579]
- [fs] mnt: fix __detach_mounts infinite loop (Benjamin Coddington) [1628736]
- [pci] pcie: Enable Broadom iProc PCIE and mark it is as tech preview (Mark Langsdorf) [1576958]
- [pci] PCI/ACPI: Add iProc PCIe MCFG quirk (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Add ACPI/ECAM support (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Remove PAXC slot check to allow VF support (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Reduce inbound/outbound mapping print level (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Reject unconfigured physical functions from PAXC (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Disable MSI parsing in certain PAXC blocks (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Fix up corrupted PAXC root complex config registers (Mark Langsdorf) [1576958]
- [pci] PCI: iproc: Activate PAXC bridge quirk for more devices (Mark Langsdorf) [1576958]

* Tue Nov 27 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-45.el8]
- [s390] s390/mm: fix mis-accounting of pgtable_bytes (Joe Lawrence) [1644481]
- [mm] mm: add mm_pxd_folded checks to pgtable_bytes accounting functions (Joe Lawrence) [1644481]
- [mm] mm: introduce mm_[p4d|pud|pmd]_folded (Joe Lawrence) [1644481]
- [mm] mm: make the __PAGETABLE_PxD_FOLDED defines non-empty (Joe Lawrence) [1644481]
- [x86] x86/cpu/vmware: Do not trace vmware_sched_clock() (Vitaly Kuznetsov) [1650273]
- [fs] fuse: fix possibly missed wake-up after abort (Lukas Czerner) [1649244]
- [fs] fuse: fix leaked notify reply (Lukas Czerner) [1649244]
- [fs] fuse: fix blocked_waitq wakeup (Lukas Czerner) [1649244]
- [fs] fuse: set FR_SENT while locked (Lukas Czerner) [1649244]
- [fs] fuse: Fix use-after-free in fuse_dev_do_write() (Lukas Czerner) [1649244]
- [fs] fuse: Fix use-after-free in fuse_dev_do_read() (Lukas Czerner) [1649244]
- [fs] fuse: Add missed unlock_page() to fuse_readpages_fill() (Lukas Czerner) [1649244]
- [fs] fuse: Don't access pipe->buffers without pipe_lock() (Lukas Czerner) [1649244]
- [fs] fuse: fix initial parallel dirops (Lukas Czerner) [1649244]
- [fs] fuse: Fix oops at process_init_reply() (Lukas Czerner) [1649244]
- [fs] fuse: umount should wait for all requests (Lukas Czerner) [1649244]
- [fs] fuse: fix unlocked access to processing queue (Lukas Czerner) [1649244]
- [fs] fuse: fix double request_end() (Lukas Czerner) [1649244]
- [fs] fuse: fix use-after-free in fuse_direct_IO() (Lukas Czerner) [1599195]

* Fri Nov 23 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-44.el8]
- [firmware] efi: Fix debugobjects warning on 'efi_rts_work' (Waiman Long) [1652190]
- [rpmspec] kernel.spec: Do not zip modules on noarch builds (Prarit Bhargava) [1646471]
- [iommu] iommu/amd: Clear memory encryption mask from physical address (Gary Hook) [1640384]

* Thu Nov 22 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-43.el8]
- [powerpc] powerpc/mm/radix: Only need the Nest MMU workaround for R -> RW transition (Steve Best) [1651276]
- [powerpc] powerpc/mm/books3s: Add new pte bit to mark pte temporarily invalid (Steve Best) [1651276]
- [powerpc] powerpc/tm: Fix HFSCR bit for no suspend case (Steve Best) [1651275]

* Wed Nov 21 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-42.el8]
- [powerpc] powerpc/powernv: Fix concurrency issue with npu->mmio_atsd_usage (Steve Best) [1651267]
- [tools] perf tools: Remove ext from struct kmod_path (Jiri Olsa) [1581390]
- [tools] perf tools: Add gzip_is_compressed function (Jiri Olsa) [1581390]
- [tools] perf tools: Add lzma_is_compressed function (Jiri Olsa) [1581390]
- [tools] perf tools: Add is_compressed callback to compressions array (Jiri Olsa) [1581390]
- [tools] perf tools: Move the temp file processing into decompress_kmodule (Jiri Olsa) [1581390]
- [tools] perf tools: Use compression id in decompress_kmodule() (Jiri Olsa) [1581390]
- [tools] perf tools: Store compression id into struct dso (Jiri Olsa) [1581390]
- [tools] perf tools: Add compression id into 'struct kmod_path' (Jiri Olsa) [1581390]
- [tools] perf tools: Make is_supported_compression() static (Jiri Olsa) [1581390]
- [tools] perf tools: Make decompress_to_file() function static (Jiri Olsa) [1581390]
- [tools] perf tools: Get rid of dso__needs_decompress() call in __open_dso() (Jiri Olsa) [1581390]
- [tools] perf tools: Get rid of dso__needs_decompress() call in symbol__disassemble() (Jiri Olsa) [1581390]
- [tools] perf tools: Get rid of dso__needs_decompress() call in read_object_code() (Jiri Olsa) [1581390]
- [rpmspec] redhat: Enable kernel-tools (for kvm_stat) on s390x, too (Thomas Huth) [1631222]

* Tue Nov 20 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-41.el8]
- [drm] drm/atomic_helper: Stop modesets on unregistered connectors harder (Lyude Paul) [1631575]
- [drm] drm/nouveau: Fix nv50_mstc->best_encoder() (Lyude Paul) [1631575]
- [drm] drm/atomic_helper: Allow DPMS On<->Off changes for unregistered connectors (Lyude Paul) [1631575]
- [drm] drm/i915: Fix intel_dp_mst_best_encoder() (Lyude Paul) [1631575]
- [drm] drm/i915: Skip vcpi allocation for MSTB ports that are gone (Lyude Paul) [1631575]
- [drm] drm/i915: Don't unset intel_connector->mst_port (Lyude Paul) [1631575]
- [drm] drm/atomic_helper: Disallow new modesets on unregistered connectors (Lyude Paul) [1631575]
- [s390] s390/qeth: fix HiperSockets sniffer (Philipp Rudo) [1649773]
- [s390] s390/qeth: report 25Gbit link speed (Philipp Rudo) [1649772]
- [s390] s390/qeth: sanitize strings in debug messages (Philipp Rudo) [1649770]
- [s390] s390/qeth: fix initial operstate (Philipp Rudo) [1649769]
- [s390] s390/qeth: unregister netdevice only when registered (Philipp Rudo) [1649769]
- [powerpc] powerpc/64s: consolidate MCE counter increment (Steve Best) [1633550]
- [powerpc] powerpc/64s: move machine check SLB flushing to mm/slb.c (Steve Best) [1633550]
- [powerpc] powernv/pseries: consolidate code for mce early handling (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Dump the SLB contents on SLB MCE errors (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Display machine check error details (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Flush SLB contents on SLB MCE errors (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Define MCE error event section (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Avoid using the size greater than RTAS_ERROR_LOG_MAX (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Defer the logging of rtas error to irq work queue (Steve Best) [1633550]
- [powerpc] powerpc/pseries: Fix endianness while restoring of r3 in MCE handler (Steve Best) [1633550]
- [cdrom] cdrom: fix improper type cast, which can leat to information leak (Maurizio Lombardi) [1650476]

* Thu Nov 15 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-40.el8]
- [drm] drm/amdgpu/pm: Fix potential Spectre v1 (Rob Clark) [1637115]
- [drm] drm/i915/kvmgt: Fix potential Spectre v1 (Rob Clark) [1637115]
- [fs] gfs2: Fix metadata read-ahead during truncate (2) (Andreas Grunbacher) [1647982]
- [block] block: make sure writesame bio is aligned with logical block size (Ming Lei) [1648750]
- [block] block: cleanup __blkdev_issue_discard() (Ming Lei) [1648750]
- [block] block: make sure discard bio is aligned with logical block size (Ming Lei) [1648750]
- [block] block: Clear kernel memory before copying to user (Ming Lei) [1648752]
- [block] block: respect virtual boundary mask in bvecs (Ming Lei) [1648756]
- [block] xen: don't include <xen/xen.h> from <asm/io.h> and <asm/dma-mapping.h> (Ming Lei) [1648756]
- [block] block: remove ARCH_BIOVEC_PHYS_MERGEABLE (Ming Lei) [1648756]
- [block] xen: provide a prototype for xen_biovec_phys_mergeable in xen.h (Ming Lei) [1648756]
- [block] xen: remove the xen_biovec_phys_mergeable export (Ming Lei) [1648756]
- [block] arm: remove the unused BIOVEC_MERGEABLE define (Ming Lei) [1648756]
- [block] block: don't include bug.h from bio.h (Ming Lei) [1648756]
- [block] block: don't include io.h from bio.h (Ming Lei) [1648756]
- [block] block: remove bvec_to_phys (Ming Lei) [1648756]
- [block] block: merge BIOVEC_SEG_BOUNDARY into biovec_phys_mergeable (Ming Lei) [1648756]
- [block] block: add a missing BIOVEC_SEG_BOUNDARY check in bio_add_pc_page (Ming Lei) [1648756]
- [block] block: simplify BIOVEC_PHYS_MERGEABLE (Ming Lei) [1648756]
- [block] block: move req_gap_back_merge to blk.h (Ming Lei) [1648756]
- [block] block: move req_gap_{back,front}_merge to blk-merge.c (Ming Lei) [1648756]
- [block] block: move integrity_req_gap_{back,front}_merge to blk.h (Ming Lei) [1648756]
- [fs] gfs2: Fix iomap buffer head reference counting bug (Andreas Grunbacher) [1647073]
- [scsi] qla2xxx: Update driver version to 10.00.00.07.08.0-k1 (Himanshu Madhani) [1615896]
- [scsi] scsi: qla2xxx: Initialize port speed to avoid setting lower speed (Himanshu Madhani) [1615896]
- [scsi] scsi: qla2xxx: Fix incorrect port speed being set for FC adapters (Himanshu Madhani) [1615896]
- [block] block: brd: associate with queue until adding disk (Ming Lei) [1644602]
- [block] block: call rq_qos_exit() after queue is frozen (Ming Lei) [1641558]
- [block] block: fix the DISCARD request merge (Ming Lei) [1646776]
- [block] blk-mq: fallback to previous nr_hw_queues when updating fails (Ming Lei) [1642218]
- [block] blk-mq: realloc hctx when hw queue is mapped to another node (Ming Lei) [1642218]
- [block] blk-mq: change gfp flags to GFP_NOIO in blk_mq_realloc_hw_ctxs (Ming Lei) [1642218]
- [block] blk-mq: adjust debugfs and sysfs register when updating nr_hw_queues (Ming Lei) [1642218]
- [block] block: remove bio_rewind_iter() (Ming Lei) [1642208]

* Wed Nov 14 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-39.el8]
- [fs] jbd2: fix use after free in jbd2_log_do_checkpoint() (Lukas Czerner) [1644694]
- [fs] ext4: initialize retries variable in ext4_da_write_inline_data_begin() (Lukas Czerner) [1644694]
- [fs] ext4: fix build error when DX_DEBUG is defined (Lukas Czerner) [1644694]

* Tue Nov 13 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-38.el8]
- [pinctrl] pinctrl: intel: Add Ice Lake PCH pin controller support (David Arcari) [1483413]
- [netdrv] nfp: flower: fix vlan match by checking both vlan id and vlan pcp (Pablo Cascon) [1645220]
- [netdrv] nfp: flower: reject tunnel encap with ipv6 outer headers for offloading (Pablo Cascon) [1646644]
- [netdrv] nfp: populate bus-info on representors (Pablo Cascon) [1643998]
- [powerpc] KVM: PPC: Validate TCEs against preregistered memory page sizes (David Gibson) [1625821]
- [powerpc] KVM: PPC: Inform the userspace about TCE update failures (David Gibson) [1625821]
- [powerpc] KVM: PPC: Book3S: Fix guest DMA when guest partially backed by THP pages (David Gibson) [1625821]

* Fri Nov 09 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-37.el8]
- [kernel] locking/lockdep: Fix debug_locks off performance problem (Waiman Long) [1647560]
- [kernel] locking/lockdep: Remove duplicated 'lock_class_ops' percpu array (Waiman Long) [1647560]
- [kernel] locking/lockdep: Make class->ops a percpu counter and move it under CONFIG_DEBUG_LOCKDEP=y (Waiman Long) [1647560]
- [kernel] locking/lockdep: Add a faster path in __lock_release() (Waiman Long) [1647560]
- [kernel] locking/lockdep: Eliminate redundant IRQs check in __lock_acquire() (Waiman Long) [1647560]
- [kernel] locking/lockdep: Remove add_chain_cache_classes() (Waiman Long) [1647560]
- [fs] gfs2: Put bitmap buffers in put_super (Andreas Grunbacher) [1647073]
- [scsi] scsi: hpsa: limit transfer length to 1MB, not 512kB (Joseph Szczypek) [1643956]
- [netdrv] nfp: report FW vNIC stats in interface stats (Pablo Cascon) [1645032]
- [rpmspec] spec: Add bpftool debuginfo package (Jiri Olsa) [1633018]
- [crypto] crypto: chelsio: Fix memory corruption in DMA Mapped buffers (Arjun Vynipadath) [1631750]
- [cdrom] cdrom: Fix info leak/OOB read in cdrom_ioctl_drive_status (Maurizio Lombardi) [1627732] {CVE-2018-16658}

* Wed Nov 07 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-36.el8]
- [kernel] srcu: Make early-boot call_srcu() reuse workqueue lists (Waiman Long) [1644375]
- [tools] rcutorture: Test early boot call_srcu() (Waiman Long) [1644375]
- [kernel] srcu: Make call_srcu() available during very early boot (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_state.ofl_lock to raw_spinlock_t (Waiman Long) [1644375]
- [kernel] rcu: Remove obsolete ->dynticks_fqs and ->cond_resched_completed (Waiman Long) [1644375]
- [kernel] rcu: Switch ->dynticks to rcu_data structure, remove rcu_dynticks (Waiman Long) [1644375]
- [kernel] rcu: Switch dyntick nesting counters to rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Switch urgent quiescent-state requests to rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Switch lazy counts to rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Switch last accelerate/advance to rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Switch ->tick_nohz_enabled_snap to rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Merge rcu_dynticks structure into rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Remove unused rcu_dynticks_snap() from Tiny RCU (Waiman Long) [1644375]
- [kernel] rcu: Convert "1UL << x" to "BIT(x)" (Waiman Long) [1644375]
- [kernel] rcu: Avoid resched_cpu() when rescheduling the current CPU (Waiman Long) [1644375]
- [kernel] rcu: More aggressively enlist scheduler aid for nohz_full CPUs (Waiman Long) [1644375]
- [kernel] rcu: Compute jiffies_till_sched_qs from other kernel parameters (Waiman Long) [1644375]
- [kernel] rcu: Provide functions for determining if call_rcu() has been invoked (Waiman Long) [1644375]
- [kernel] rcu: Eliminate ->rcu_qs_ctr from the rcu_dynticks structure (Waiman Long) [1644375]
- [kernel] rcu: Motivate Tiny RCU forward progress (Waiman Long) [1644375]
- [kernel] rcutorture: Dump reader protection sequence if failures or close calls (Waiman Long) [1644375]
- [kernel] rcu: Provide improved interrupt-from-idle check in rcu_check_callbacks() (Waiman Long) [1644375]
- [kernel] rcu: Make need_resched() respond to urgent RCU-QS needs (Waiman Long) [1644375]
- [kernel] rcu: Inline _rcu_barrier() into its sole remaining caller (Waiman Long) [1644375]
- [kernel] rcu: Define rcu_all_qs() only in !PREEMPT builds (Waiman Long) [1644375]
- [kernel] rcu: Remove !PREEMPT code from rcu_note_voluntary_context_switch() (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in update.c (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in tree_plugin.h (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in tree_exp.h (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in tree.c (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in tiny.c (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in srcutree.h (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in rcutorture.c (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in rcu.h (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in Kconfig (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in rcupdate_wait.h (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in rculist.h (Waiman Long) [1644375]
- [kernel] rcu: Clean up flavor-related definitions and comments in rcupdate.h (Waiman Long) [1644375]
- [kernel] rcu: Remove now-unused rcutorture APIs (Waiman Long) [1644375]
- [kernel] rcuperf: Remove the "rcu_bh" and "sched" torture types (Waiman Long) [1644375]
- [kernel] rcutorture: Remove the "rcu_bh" and "sched" torture types (Waiman Long) [1644375]
- [kernel] rcu: Stop testing RCU-bh and RCU-sched (Waiman Long) [1644375]
- [kernel] rcutorture: Add RCU-bh and RCU-sched support for extended readers (Waiman Long) [1644375]
- [kernel] rcu: Consolidate RCU-sched update-side function definitions (Waiman Long) [1644375]
- [kernel] rcu: Consolidate RCU-bh update-side function definitions (Waiman Long) [1644375]
- [kernel] rcu: Pull rcu_gp_kthread() FQS loop into separate function (Waiman Long) [1644375]
- [kernel] rcu: Inline increment_cpu_stall_ticks() into its sole caller (Waiman Long) [1644375]
- [kernel] rcu: Fix typo in force_qs_rnp()'s parameter's parameter (Waiman Long) [1644375]
- [kernel] rcu: Eliminate initialization-time use of rsp (Waiman Long) [1644375]
- [kernel] rcu: Eliminate RCU-barrier use of rsp (Waiman Long) [1644375]
- [kernel] rcu: Eliminate quiescent-state and grace-period-nonstart use of rsp (Waiman Long) [1644375]
- [kernel] rcu: Eliminate callback-invocation/invocation use of rsp (Waiman Long) [1644375]
- [kernel] rcu: Eliminate grace-period management code use of rsp (Waiman Long) [1644375]
- [kernel] rcu: Eliminate stall-warning use of rsp (Waiman Long) [1644375]
- [kernel] rcu: Restructure rcu_check_gp_kthread_starvation() (Waiman Long) [1644375]
- [kernel] rcu: Simplify rcutorture_get_gp_data() (Waiman Long) [1644375]
- [kernel] rcu: Remove for_each_rcu_flavor() flavor-traversal macro (Waiman Long) [1644375]
- [kernel] rcu: Remove last non-flavor-traversal rsp local variable from tree_plugin.h (Waiman Long) [1644375]
- [kernel] rcu: Remove rcu_data structure's ->rsp field (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_node tree accessor macros (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from expedited grace-period functions (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from no-CBs CPU functions (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from print_cpu_stall_info() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_spawn_one_boost_kthread() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from dump_blkd_tasks() and friend (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_print_detail_task_stall() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_init_one() and friends (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_boot_init_percpu_data() and friends (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from _rcu_barrier() and friends (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from __rcu_pending() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from __call_rcu() and friend (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from __rcu_process_callbacks() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_check_gp_start_stall() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from force-quiescent-state functions (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_do_batch() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from CPU hotplug functions (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_check_quiescent_state() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_gp_kthread() and friends (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_gp_slow() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from note_gp_changes() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from __note_gp_changes() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_advance_cbs() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_accelerate_cbs_unlocked() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_accelerate_cbs() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_gp_kthread_wake() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_future_gp_cleanup() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from check_cpu_stall() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from print_cpu_stall() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from print_other_cpu_stall() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_stall_kick_kthreads() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_dump_cpu_stacks() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_check_gp_kthread_starvation() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from record_gp_stall_check_time() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_get_root() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_gp_in_progress() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_report_qs_rdp() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_report_unblock_qs_rnp() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_report_qs_rsp() (Waiman Long) [1644375]
- [kernel] rcu: Remove rsp parameter from rcu_report_qs_rnp() (Waiman Long) [1644375]
- [kernel] rcu: Remove rcu_data_p pointer to default rcu_data structure (Waiman Long) [1644375]
- [kernel] rcu: Remove rcu_state_p pointer to default rcu_state structure (Waiman Long) [1644375]
- [kernel] rcu: Remove rcu_state structure's ->rda field (Waiman Long) [1644375]
- [kernel] rcu: Eliminate rcu_state structure's ->call field (Waiman Long) [1644375]
- [kernel] rcu: Remove RCU_STATE_INITIALIZER() (Waiman Long) [1644375]
- [kernel] rcu: Express Tiny RCU updates in terms of RCU rather than RCU-sched (Waiman Long) [1644375]
- [kernel] rcu: Define RCU-sched API in terms of RCU for Tree RCU PREEMPT builds (Waiman Long) [1644375]
- [kernel] rcu: Fix typo in rcu_get_gp_kthreads_prio() header comment (Waiman Long) [1644375]
- [kernel] rcu: Drop "wake" parameter from rcu_report_exp_rdp() (Waiman Long) [1644375]
- [kernel] rcu: Update comments and help text for no more RCU-bh updaters (Waiman Long) [1644375]
- [kernel] rcu: Define RCU-bh update API in terms of RCU (Waiman Long) [1644375]
- [kernel] rcu: Report expedited grace periods at context-switch time (Waiman Long) [1644375]
- [kernel] rcu: Apply RCU-bh QSes to RCU-sched and RCU-preempt when safe (Waiman Long) [1644375]
- [kernel] rcu: Add warning to detect half-interrupts (Waiman Long) [1644375]
- [kernel] rcu: Remove now-unused ->b.exp_need_qs field from the rcu_special union (Waiman Long) [1644375]
- [kernel] rcu: Allow processing deferred QSes for exiting RCU-preempt readers (Waiman Long) [1644375]
- [kernel] rcutorture: Test extended "rcu" read-side critical sections (Waiman Long) [1644375]
- [kernel] rcu: Defer reporting RCU-preempt quiescent states when disabled (Waiman Long) [1644375]
- [kernel] rcu: Refactor rcu_{nmi,irq}_{enter,exit}() (Waiman Long) [1644375]
- [documentation] doc: Fix broken HTML directive (Waiman Long) [1644375]
- [documentation] doc: Update removal of RCU-bh/sched update machinery (Waiman Long) [1644375]
- [kernel] rcutorture: Maintain self-propagating CB only during forward-progress test (Waiman Long) [1644375]
- [kernel] rcutorture: Check GP completion at stutter end (Waiman Long) [1644375]
- [kernel] rcutorture: Print forward-progress test interval on error (Waiman Long) [1644375]
- [kernel] rcutorture: Adjust number of reader kthreads per CPU-hotplug operations (Waiman Long) [1644375]
- [kernel] rcutorture: Reduce priority of forward-progress testing (Waiman Long) [1644375]
- [kernel] rcutorture: Limit reader duration if irq or bh disabled (Waiman Long) [1644375]
- [kernel] rcutorture: Increase rcu_read_delay() longdelay_ms (Waiman Long) [1644375]
- [kernel] rcutorture: Add self-propagating callback to forward-progress testing (Waiman Long) [1644375]
- [kernel] rcutorture: Vary forward-progress test interval (Waiman Long) [1644375]
- [kernel] rcutorture: Avoid no-test complaint if too few forward-progress tries (Waiman Long) [1644375]
- [kernel] rcutorture: Also use GP sequence to judge forward progress (Waiman Long) [1644375]
- [kernel] rcutorture: Add forward-progress tests for RCU grace periods (Waiman Long) [1644375]
- [tools] rcutorture: Remove TREE06 and TREE08 from the default test list (Waiman Long) [1644375]
- [kernel] rcuperf: Warn on bad perf type for built-in tests (Waiman Long) [1644375]
- [kernel] rcutorture: Warn on bad torture type for built-in tests (Waiman Long) [1644375]
- [kernel] rcutorture: Force occasional reader waits (Waiman Long) [1644375]
- [tools] torture: Stop overwriting Make.out file with obsolete version (Waiman Long) [1644375]
- [documentation] doc: Improve rcu_dynticks::dynticks documentation (Waiman Long) [1644375]
- [documentation] doc: Fix broken RCU-requirements link to LKML archive (Waiman Long) [1644375]
- [documentation] doc: Add design documentation on interruption of NMI handlers (Waiman Long) [1644375]
- [kernel] rcutorture: Fix rcu_barrier successes counter (Waiman Long) [1644375]
- [kernel] rcutorture: Add support to detect if boost kthread prio is too low (Waiman Long) [1644375]
- [kernel] rcutorture: Use monotonic timestamp for stall detection (Waiman Long) [1644375]
- [kernel] rcutorture: Make boost test more robust (Waiman Long) [1644375]
- [kernel] rcutorture: Disable RT throttling for boost tests (Waiman Long) [1644375]
- [kernel] rcutorture: Emphasize testing of single reader protection type (Waiman Long) [1644375]
- [kernel] rcutorture: Handle extended read-side critical sections (Waiman Long) [1644375]
- [kernel] rcutorture: Make rcu_torture_timer() use rcu_torture_one_read() (Waiman Long) [1644375]
- [kernel] rcutorture: Use per-CPU random state for rcu_torture_timer() (Waiman Long) [1644375]
- [kernel] rcutorture: Use atomic increment for n_rcu_torture_timers (Waiman Long) [1644375]
- [kernel] rcutorture: Extract common code from rcu_torture_reader() (Waiman Long) [1644375]
- [kernel] rcuperf: Remove unused torturing_tasks() function (Waiman Long) [1644375]
- [kernel] rcu: Remove rcutorture test version and sequence number (Waiman Long) [1644375]
- [kernel] rcutorture: Change units of onoff_interval to jiffies (Waiman Long) [1644375]
- [kernel] rcu: Assign higher prio to RCU threads if rcutorture is built-in (Waiman Long) [1644375]
- [documentation] rculist: Improve documentation for list_for_each_entry_from_rcu() (Waiman Long) [1644375]
- [kernel] srcu: Add grace-period number to rcutorture statistics printout (Waiman Long) [1644375]
- [kernel] rcu: Print stall-warning NMI dyntick state in hexadecimal (Waiman Long) [1644375]
- [maintainers] MAINTAINERS: Update RCU, SRCU, and TORTURE-TEST entries (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_seq_diff() more exact (Waiman Long) [1644375]
- [documentation] doc: Update synchronize_rcu() definition in whatisRCU.txt (Waiman Long) [1644375]
- [kernel] rcu: Check the range of jiffies_till_{first, next}_fqs when setting them (Waiman Long) [1644375]
- [kernel] rcu: Add diagnostics for rcutorture writer stall warning (Waiman Long) [1644375]
- [kernel] rcu: Add comment to the last sleep in the rcu tasks loop (Waiman Long) [1644375]
- [kernel] rcu: Speed up calling of RCU tasks callbacks (Waiman Long) [1644375]
- [kernel] rcu: Add comment documenting how rcu_seq_snap works (Waiman Long) [1644375]
- [kernel] rcu: Use RCU CPU stall timeout for rcu_check_gp_start_stall() (Waiman Long) [1644375]
- [kernel] rcu: Remove __maybe_unused from rcu_cpu_has_callbacks() (Waiman Long) [1644375]
- [kernel] rcu: Remove "inline" from rcu_perf_print_module_parms() (Waiman Long) [1644375]
- [kernel] rcu: Remove "inline" from rcu_torture_print_module_parms() (Waiman Long) [1644375]
- [kernel] rcu: Remove "inline" from panic_on_rcu_stall() and rcu_blocking_is_gp() (Waiman Long) [1644375]
- [kernel] rcu: Remove unused local variable "cpu" (Waiman Long) [1644375]
- [kernel] rcu: Remove unused rcu_kick_nohz_cpu() function (Waiman Long) [1644375]
- [kernel] rcu: Clarify and correct the rcu_preempt_qs() header comment (Waiman Long) [1644375]
- [kernel] rcu: Inline rcu_dynticks_momentary_idle() into its sole caller (Waiman Long) [1644375]
- [kernel] rcu: Mark task as .need_qs less aggressively (Waiman Long) [1644375]
- [kernel] rcu: Improve RCU-tasks naming and comments (Waiman Long) [1644375]
- [kernel] rcu: Use pr_fmt to prefix "rcu: " to logging output (Waiman Long) [1644375]
- [kernel] rcu: rcupdate.h: Get rid of Sphinx warnings at rcu_pointer_handoff() (Waiman Long) [1644375]
- [kernel] rcu: Improve rcu_note_voluntary_context_switch() reporting (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_read_unlock_special() static (Waiman Long) [1644375]
- [kernel] rcu: Add diagnostics for offline CPUs failing to report QS (Waiman Long) [1644375]
- [kernel] rcu: Record ->gp_state for both phases of grace-period initialization (Waiman Long) [1644375]
- [kernel] rcu: Add CPU online/offline state to dump_blkd_tasks() (Waiman Long) [1644375]
- [kernel] rcu: Add up-tree information to dump_blkd_tasks() diagnostics (Waiman Long) [1644375]
- [kernel] rcu: Remove CPU-hotplug failsafe from force-quiescent-state code path (Waiman Long) [1644375]
- [kernel] rcu: Remove failsafe check for lost quiescent state (Waiman Long) [1644375]
- [kernel] rcu: Move grace-period pre-init delay after pre-init (Waiman Long) [1644375]
- [kernel] rcu: Add RCU-preempt check for waiting on newly onlined CPU (Waiman Long) [1644375]
- [kernel] rcu: Fix grace-period hangs due to race with CPU offline (Waiman Long) [1644375]
- [kernel] rcu: Fix grace-period hangs from mid-init task resume (Waiman Long) [1644375]
- [kernel] rcu: Suppress false-positive splats from mid-init task resume (Waiman Long) [1644375]
- [kernel] rcu: Suppress more involved false-positive preempted-task splats (Waiman Long) [1644375]
- [kernel] rcu: Suppress false-positive preempted-task splats (Waiman Long) [1644375]
- [kernel] rcu: Suppress false-positive offline-CPU lockdep-RCU splat (Waiman Long) [1644375]
- [kernel] rcu: Prevent useless FQS scan after all CPUs have checked in (Waiman Long) [1644375]
- [kernel] rcu: Replace smp_wmb() with smp_store_release() for stall check (Waiman Long) [1644375]
- [kernel] rcu: Fix typo and add additional debug (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_report_unblock_qs_rnp() warn on violated preconditions (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_init_new_rnp() stop upon already-set bit (Waiman Long) [1644375]
- [kernel] rcu: Fix an obsolete ->qsmaskinit comment (Waiman Long) [1644375]
- [kernel] rcu: Clean up handling of tasks blocked across full-rcu_node offline (Waiman Long) [1644375]
- [kernel] rcu: Identify grace period is in progress as we advance up the tree (Waiman Long) [1644375]
- [kernel] rcu: Use better variable names in funnel locking loop (Waiman Long) [1644375]
- [kernel] rcu: Rename the grace-period-request variables and parameters (Waiman Long) [1644375]
- [kernel] rcu: Regularize resetting of rcu_data wrap indicator (Waiman Long) [1644375]
- [kernel] rcutorture: Correctly handle grace-period sequence wrap (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_start_this_gp() check for grace period already started (Waiman Long) [1644375]
- [kernel] rcu: Fix cpustart tracepoint gp_seq number (Waiman Long) [1644375]
- [kernel] rcu: Produce last "CleanupMore" trace only if late-breaking request (Waiman Long) [1644375]
- [kernel] rcu: Don't funnel-lock above leaf node if GP in progress (Waiman Long) [1644375]
- [documentation] doc: Update RCU CPU stall-warning documentation (Waiman Long) [1644375]
- [documentation] doc: Update memory-ordering documentation for ->gp-seq (Waiman Long) [1644375]
- [documentation] doc: Update data-structure documentation for ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Make simple callback acceleration refer to rdp->gp_seq_needed (Waiman Long) [1644375]
- [kernel] rcu: Remove ->gpnum and ->completed (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_fqs tracepoint to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_quiescent_state_report tracepoint to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_unlock_preempted_task tracepoint to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_preempt_task tracepoint to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_grace_period_init tracepoint to gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_future_grace_period tracepoint to gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_grace_period tracepoint to gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_nocb_wait_gp() check if GP already requested (Waiman Long) [1644375]
- [kernel] rcu: Move from ->need_future_gp[] to ->gp_seq_needed (Waiman Long) [1644375]
- [kernel] rcutorture: Convert rcutorture_get_gp_data() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Make RCU CPU stall warnings use ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert grace-period requests to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert ->completedqs to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert ->rcu_iw_gpnum to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Move rcu_gp_in_progress() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Move rcu_nocb_gp_get() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Move rcu_try_advance_all_cbs() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Move rcu_implicit_dynticks_qs() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_gpnum_ovf() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Move RCU's grace-period-change code to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert conditional grace-period primitives to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Make quiescent-state reporting use ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Convert rcu_check_gp_kthread_starvation() to GP sequence number (Waiman Long) [1644375]
- [kernel] rcu: Make rcutorture's batches-completed API use ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Move rcu_gp_slow() to ->gp_seq (Waiman Long) [1644375]
- [kernel] rcu: Introduce grace-period sequence numbers (Waiman Long) [1644375]
- [kernel] rcu: Make rcu_gp_cleanup() write only once to ->gp_flags (Waiman Long) [1644375]
- [kernel] rcu: Diagnostics for grace-period startup hangs (Waiman Long) [1644375]
- [kernel] rcu: Exclude near-simultaneous RCU CPU stall warnings (Waiman Long) [1644375]
- [kernel] rcu: Use the proper lockdep annotation in dump_blkd_tasks() (Waiman Long) [1644375]
- [kernel] rcu: Add debugging info to assertion (Waiman Long) [1644375]
- [kernel] torture: Keep old-school dmesg format (Waiman Long) [1644375]
- [kernel] torture: Make online/offline messages appear only for verbose=2 (Waiman Long) [1644375]
- [tools] rcutorture: Make kvm-find-errors.sh find close calls (Waiman Long) [1644375]
- [tools] rcutorture: Remove obsolete TREE08-T.boot file (Waiman Long) [1644375]
- [tools] torture: Use a single build directory for torture scenarios (Waiman Long) [1644375]
- [kernel] srcu: Introduce srcu_read_{un,}lock_notrace() (Waiman Long) [1644375]
- [kernel] srcu: Add address of first callback to rcutorture output (Waiman Long) [1644375]
- [kernel] srcu: Document that srcu_funnel_gp_start() implies srcu_funnel_exp_start() (Waiman Long) [1644375]
- [kernel] srcu: Fix typos in __call_srcu() header comment (Waiman Long) [1644375]
- [kernel] rcu: Make expedited grace period use direct call on last leaf (Waiman Long) [1644375]

* Tue Nov 06 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-35.el8]
- [netdrv] nfp: flower: use offsets provided by pedit instead of index for ipv6 (Pablo Cascon) [1645132]
- [netdrv] nfp: flower: fix multiple keys per pedit action (Pablo Cascon) [1645132]
- [netdrv] nfp: flower: fix pedit set actions for multiple partial masks (Pablo Cascon) [1645132]
- [netdrv] nfp: flower: ignore checksum actions when performing pedit actions (Pablo Cascon) [1644400]
- [kernel] sched/fair: Fix throttle_list starvation with low CFS quota (Phil Auld) [1638526]
- [net] tipc: fix the big/little endian issue in tipc_dest (Jon Maloy) [1640712]
- [rpmspec] kernel.spec: Include kernel-signing-ca.cer public key (Prarit Bhargava) [1638465]
- [block] block: don't deal with discard limit in blkdev_issue_discard() (Ming Lei) [1631255]
- [powerpc] powerpc/mm: Check memblock_add against MAX_PHYSMEM_BITS range (Gustavo Duarte) [1561402]
- [powerpc] powerpc/mm: Increase MAX_PHYSMEM_BITS to 128TB with SPARSEMEM_VMEMMAP config (Gustavo Duarte) [1561402]

* Tue Nov 06 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-34.el8]
- [s390] s390/crypto: Enhance paes cipher to accept variable length key material (Philipp Rudo) [1644387]
- [s390] s390/pkey: move pckmo subfunction available checks away from module init (Philipp Rudo) [1644387]
- [s390] s390/pkey: Load pkey kernel module automatically (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: fix broken zcrypt_send_cprb in-kernel api function (Philipp Rudo) [1644387]
- [s390] s390/pkey: Introduce new API for transforming key blobs (Philipp Rudo) [1644387]
- [s390] s390/pkey: Introduce new API for random protected key verification (Philipp Rudo) [1644387]
- [s390] s390/pkey: Add sysfs attributes to emit secure key blobs (Philipp Rudo) [1644387]
- [s390] s390/pkey: Add sysfs attributes to emit protected key blobs (Philipp Rudo) [1644387]
- [s390] s390/pkey: Define protected key blob format (Philipp Rudo) [1644387]
- [s390] s390/pkey: Introduce new API for random protected key generation (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: add ap_adapter_mask sysfs attribute (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: provide apfs failure code on type 86 error reply (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: zcrypt device driver cleanup (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: multiple zcrypt device nodes support (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: enable AP bus scan without a valid default domain (Philipp Rudo) [1644387]
- [s390] s390/zcrypt: Use kmemdup to replace kmalloc + memcpy (Philipp Rudo) [1644387]
- [s390] s390/qeth: add TSO support for L2 devices (Philipp Rudo) [1644381]
- [s390] s390/qeth: add support for IPv6 TSO (Philipp Rudo) [1644381]
- [s390] s390/qeth: enhance TSO control sequence (Philipp Rudo) [1644381]
- [s390] s390/qeth: make TSO controls protocol-agnostic (Philipp Rudo) [1644381]
- [s390] s390: qeth: Fix potential array overrun in cmd/rc lookup (Philipp Rudo) [1644381]
- [s390] s390: qeth_core_mpc: Use ARRAY_SIZE instead of reimplementing its function (Philipp Rudo) [1644381]
- [scsi] scsi: mpt3sas: Remove unnecessary parentheses and simplify null checks (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Use dma_pool_zalloc (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Remove unused macro MPT3SAS_FMT (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Convert logging uses with MPT3SAS_FMT without logging levels (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Remove KERN_WARNING from panic uses (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Convert logging uses with MPT3SAS_FMT and reply_q_name to s: (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Convert mlsleading uses of pr_<level> with MPT3SAS_FMT (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Convert uses of pr_<level> with MPT3SAS_FMT to ioc_<level> (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Add ioc_<level> logging macros (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Fix calltrace observed while running IO & reset (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Improve kernel-doc headers (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Split _base_reset_handler(), mpt3sas_scsih_reset_handler() and mpt3sas_ctl_reset_handler() (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Fix a race condition in mpt3sas_base_hard_reset_handler() (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Fix _transport_smp_handler() error path (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Introduce struct mpt3sas_nvme_cmd (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Annotate switch/case fall-through (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Remove set-but-not-used variables (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Fix indentation (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Update driver version "26.100.00.00" (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: As per MPI-spec, use combined reply queue for SAS3.5 controllers when HBA supports more than 16 MSI-x vectors (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Fix, False timeout prints for ioctl and other internal commands during controller reset (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Don't access the structure after decrementing it's instance reference count (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Incorrect command status was set/marked as not used (Tomas Henzl) [1638649]
- [scsi] scsi: mpt3sas: Don't abort I/Os issued to NVMe drives while processing Async Broadcast primitive event (Tomas Henzl) [1638649]
- [netdrv] net/mlx5e: Do not ignore netdevice TX/RX queues number (Alaa Hleihel) [1643103]
- [netdrv] net/mlx5e: Use non-delayed work for update stats (Alaa Hleihel) [1643103]
- [netdrv] net/mlx5e: Initialize all netdev common structures in one place (Alaa Hleihel) [1643103]
- [netdrv] net/mlx5e: Always initialize update stats delayed work (Alaa Hleihel) [1643103]
- [netdrv] net/mlx5e: Gather common netdev init/cleanup functionality in one place (Alaa Hleihel) [1643103]
- [infiniband] RDMA/netdev: Fix netlink support in IPoIB (Alaa Hleihel) [1643103]
- [infiniband] RDMA/netdev: Hoist alloc_netdev_mqs out of the driver (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Consolidate checking of the proposed child interface (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Maintain the child_intfs list from ndo_init/uninit (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Do not remove child devices from within the ndo_uninit (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Get rid of the sysfs_mutex (Alaa Hleihel) [1643103]
- [infiniband] RDMA/netdev: Use priv_destructor for netdev cleanup (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Move init code to ndo_init (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Move all uninit code into ndo_uninit (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Use cancel_delayed_work_sync for neigh-clean task (Alaa Hleihel) [1643103]
- [infiniband] IB/ipoib: Get rid of IPOIB_FLAG_GOING_DOWN (Alaa Hleihel) [1643103]
- [infiniband] RDMA/ipoib: Fix use of sizeof() (Alaa Hleihel) [1643103]
- [netdrv] net/mlx5e: Do not recycle RX pages in interface down flow (Alaa Hleihel) [1643103 1643047]
- [netdrv] net/mlx5e: Replace call to MPWQE free with dealloc in interface down flow (Alaa Hleihel) [1643103 1643047]
- [net] net/xdp: Fix suspicious RCU usage warning (Alaa Hleihel) [1643103 1643047]
- [netdrv] net/mlx5: WQ, fixes for fragmented WQ buffers API (Alaa Hleihel) [1643103 1636183]
- [netdrv] net/mlx4_en: Use minimal rx and tx ring sizes on kdump kernel (Alaa Hleihel) [1643103 1615267]
- [x86] mark coffeelake-s/h 8+2 as supported (David Arcari) [1575461 1575460]
- [x86] x86/spec_ctrl: Synchronize STIBP changes with RHEL IBRS code (Waiman Long) [1643233]
- [x86] x86/speculation: Propagate information about RSB filling mitigation to sysfs (Waiman Long) [1643233]
- [x86] x86/speculation: Enable cross-hyperthread spectre v2 STIBP mitigation (Waiman Long) [1643233]
- [x86] x86/speculation: Apply IBPB more strictly to avoid cross-process data leak (Waiman Long) [1643233]
- [x86] x86/speculation: Add RETPOLINE_AMD support to the inline asm CALL_NOSPEC variant (Waiman Long) [1643233]
- [x86] x86/CPU: Fix unused variable warning when !CONFIG_IA32_EMULATION (Waiman Long) [1643233]
- [x86] x86/pti/64: Remove the SYSCALL64 entry trampoline (Waiman Long) [1643233]
- [x86] x86/entry/64: Use the TSS sp2 slot for SYSCALL/SYSRET scratch space (Waiman Long) [1643233]
- [x86] x86/entry/64: Document idtentry (Waiman Long) [1643233]
- [x86] x86/asm-offsets: Move TSS_sp0 and TSS_sp1 to asm-offsets.c (Waiman Long) [1643233]
- [x86] x86: Add entry trampolines to kcore (Waiman Long) [1643233]
- [kernel] kallsyms, x86: Export addresses of PTI entry trampolines (Waiman Long) [1643233]
- [kernel] kallsyms: Simplify update_iter_mod() (Waiman Long) [1643233]
- [scsi] scsi: csiostor: fix incorrect port capabilities (Arjun Vynipadath) [1628866]
- [scsi] scsi: csiostor: add a check for NULL pointer after kmalloc() (Arjun Vynipadath) [1628866]
- [scsi] scsi: csiostor: update ingress pack and pad boundary value (Arjun Vynipadath) [1628866]

* Wed Oct 31 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-33.el8]
- [netdrv] nfp: flower: use host context count provided by firmware (Pablo Cascon) [1639609]
- [netdrv] nfp: flower: use stats array instead of storing stats per flow (Pablo Cascon) [1639609]
- [netdrv] nfp: flower: use rhashtable for flow caching (Pablo Cascon) [1639609]
- [netdrv] nfp: avoid soft lockups under control message storm (Pablo Cascon) [1639609]
- [kernel] sched: disable autogroups by default (Phil Auld) [1568166]
- [s390] s390/keyboard: sanitize array index in do_kdsk_ioctl (Steve Best) [1637591]
- [char] ipmi:ssif: Add support for multi-part transmit messages > 2 parts (Tony Camuso) [1622053]
- [scsi] scsi: libsas: fix a race condition when smp task timeout (Zhou Wang) [1640426]
- [scsi] scsi: libsas: check the ata device status by ata_dev_enabled() (Zhou Wang) [1640426]
- [scsi] scsi: libsas: always unregister the old device if going to discover new (Zhou Wang) [1640426]
- [scsi] scsi: libsas: dynamically allocate and free ata host (Zhou Wang) [1640426]
- [scsi] scsi: libsas: remove irq save in sas_ata_qc_issue() (Zhou Wang) [1640426]

* Sat Oct 27 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-32.el8]
- [video] fbdev: make FB_BACKLIGHT a tristate (Rob Clark) [1643333 1589158]
- [netdrv] Taint kernel if e1000 is loaded (Neil Horman) [1643617]
- [netdrv] iavf: fix a typo (Stefan Assmann) [1627882]
- [netdrv] i40evf: remove ndo_poll_controller (Stefan Assmann) [1627882]
- [netdrv] intel-ethernet: use correct module license (Stefan Assmann) [1627882]
- [netdrv] iavf: finish renaming files to iavf (Stefan Assmann) [1627882]
- [netdrv] iavf: rename most of i40e strings (Stefan Assmann) [1627882]
- [netdrv] iavf: tracing infrastructure rename (Stefan Assmann) [1627882]
- [netdrv] iavf: replace i40e_debug with iavf version (Stefan Assmann) [1627882]
- [netdrv] iavf: rename i40e_hw to iavf_hw (Stefan Assmann) [1627882]
- [netdrv] iavf: rename I40E_ADMINQ_DESC (Stefan Assmann) [1627882]
- [netdrv] iavf: rename device ID defines (Stefan Assmann) [1627882]
- [netdrv] iavf: remove references to old names (Stefan Assmann) [1627882]
- [netdrv] iavf: move i40evf files to new name (Stefan Assmann) [1627882]
- [netdrv] iavf: rename i40e_status to iavf_status (Stefan Assmann) [1627882]
- [netdrv] iavf: rename functions and structs to new name (Stefan Assmann) [1627882]
- [netdrv] iavf: diet and reformat (Stefan Assmann) [1627882]
- [netdrv] configs: enable CONFIG_IAVF=m (Stefan Assmann) [1627882]
- [netdrv] intel-ethernet: rename i40evf to iavf (Stefan Assmann) [1627882]
- [netdrv] i40e(vf): remove i40e_ethtool_stats.h header file (Stefan Assmann) [1627882]
- [netdrv] i40evf: cancel workqueue sync for adminq when a VF is removed (Stefan Assmann) [1627882]
- [netdrv] i40evf: Don't enable vlan stripping when rx offload is turned on (Stefan Assmann) [1627882]
- [netdrv] i40evf: set IFF_UNICAST_FLT flag for the VF (Stefan Assmann) [1627882]
- [netdrv] i40evf: Validate the number of queues a PF sends (Stefan Assmann) [1627882]
- [netdrv] i40evf: Change a VF mac without reloading the VF driver (Stefan Assmann) [1627882]
- [netdrv] i40evf: update ethtool stats code and use helper functions (Stefan Assmann) [1627882]
- [netdrv] i40e: Add AQ command for rearrange NVM structure (Stefan Assmann) [1627882]
- [netdrv] i40e: Add additional return code to i40e_asq_send_command (Stefan Assmann) [1627882]
- [netdrv] i40e/i40evf: remove redundant functions i40evf_aq_(set/get)_phy_register (Stefan Assmann) [1627882]
- [netdrv] cls_flower: fix error values for commands not supported by drivers (Stefan Assmann) [1627882]
- [init] init/main.c: Enable watchdog_thresh control from kernel line (Prarit Bhargava) [1643161]
- [s390] s390/purgatory: Remove duplicate variable definitions (Philipp Rudo) [1642447]
- [s390] s390/purgatory: Add missing FORCE to Makefile targets (Philipp Rudo) [1642447]
- [s390] s390/purgatory: Fix crash with expoline enabled (Philipp Rudo) [1642447]
- [s390] s390: disable asm code expolines if cc does not support it (Philipp Rudo) [1642447]
- [netdrv] Revert be2net: remove desc field from be_eq_obj (Ivan Vecera) [1639867]

* Tue Oct 23 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-31.el8]
- [rpmspec] redhat: add optional bpf_samples package (Jiri Benc) [1611579]
- [powerpc] powerpc/time: Fix clockevent_decrementer initalisation for PR KVM (Steve Best) [1641615]
- [net] ip: frags: fix crash in ip_do_fragment() (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ipfrag: let ip(6)frag_high_thresh in ns be higher than in init_net (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ipv6: discard IP frag queue on more errors (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ip: fail fast on IP defrag errors (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ip: process in-order fragments efficiently (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ip: add helpers to process in-order fragments faster (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ipv6: defrag: drop non-last frags smaller than min mtu (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ipv4: frags: precedence bug in ip_expire() (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ip: use rb trees for IP frag queue (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] modify skb_rbtree_purge to return the truesize of all purged skbs (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [net] ip: discard IPv4 datagrams with overlapping segments (Sabrina Dubroca) [1616058] {CVE-2018-5391}
- [fs] ovl: fix format of setxattr debug (Miklos Szeredi) [1636875]
- [fs] ovl: fix access beyond unterminated strings (Miklos Szeredi) [1636875]
- [fs] ovl: make symbol 'ovl_aops' static (Miklos Szeredi) [1636875]
- [fs] vfs: swap names of (do,vfs)_clone_file_range() (Miklos Szeredi) [1636875]
- [fs] ovl: fix freeze protection bypass in ovl_clone_file_range() (Miklos Szeredi) [1636875]
- [fs] ovl: fix freeze protection bypass in ovl_write_iter() (Miklos Szeredi) [1636875]
- [fs] ovl: fix memory leak on unlink of indexed file (Miklos Szeredi) [1636875]
- [fs] ovl: fix oopses in ovl_fill_super() failure paths (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_fadvise() (Miklos Szeredi) [1636875]
- [fs] vfs: implement readahead(2) using POSIX_FADV_WILLNEED (Miklos Szeredi) [1636875]
- [fs] vfs: add the fadvise() file operation (Miklos Szeredi) [1636875]
- [fs] Documentation/filesystems: update documentation of file_operations (Miklos Szeredi) [1636875]
- [fs] ovl: fix GPF in swapfile_activate of file from overlayfs over xfs (Miklos Szeredi) [1636875]
- [fs] ovl: respect FIEMAP_FLAG_SYNC flag (Miklos Szeredi) [1636875]
- [fs] ovl: Enable metadata only feature (Miklos Szeredi) [1636875]
- [fs] ovl: Do not do metacopy only for ioctl modifying file attr (Miklos Szeredi) [1636875]
- [fs] ovl: Do not do metadata only copy-up for truncate operation (Miklos Szeredi) [1636875]
- [fs] ovl: add helper to force data copy-up (Miklos Szeredi) [1636875]
- [fs] ovl: Check redirect on index as well (Miklos Szeredi) [1636875]
- [fs] ovl: Set redirect on upper inode when it is linked (Miklos Szeredi) [1636875]
- [fs] ovl: Set redirect on metacopy files upon rename (Miklos Szeredi) [1636875]
- [fs] ovl: Do not set dentry type ORIGIN for broken hardlinks (Miklos Szeredi) [1636875]
- [fs] ovl: Add an inode flag OVL_CONST_INO (Miklos Szeredi) [1636875]
- [fs] ovl: Treat metacopy dentries as type OVL_PATH_MERGE (Miklos Szeredi) [1636875]
- [fs] ovl: Check redirects for metacopy files (Miklos Szeredi) [1636875]
- [fs] ovl: Move some dir related ovl_lookup_single() code in else block (Miklos Szeredi) [1636875]
- [fs] ovl: Do not expose metacopy only dentry from d_real() (Miklos Szeredi) [1636875]
- [fs] ovl: Open file with data except for the case of fsync (Miklos Szeredi) [1636875]
- [fs] ovl: Add helper ovl_inode_realdata() (Miklos Szeredi) [1636875]
- [fs] ovl: Store lower data inode in ovl_inode (Miklos Szeredi) [1636875]
- [fs] ovl: Fix ovl_getattr() to get number of blocks from lower (Miklos Szeredi) [1636875]
- [fs] ovl: Add helper ovl_dentry_lowerdata() to get lower data dentry (Miklos Szeredi) [1636875]
- [fs] ovl: Copy up meta inode data from lowest data inode (Miklos Szeredi) [1636875]
- [fs] ovl: Modify ovl_lookup() and friends to lookup metacopy dentry (Miklos Szeredi) [1636875]
- [fs] ovl: Use out_err instead of out_nomem (Miklos Szeredi) [1636875]
- [fs] ovl: A new xattr OVL_XATTR_METACOPY for file on upper (Miklos Szeredi) [1636875]
- [fs] ovl: Add helper ovl_already_copied_up() (Miklos Szeredi) [1636875]
- [fs] ovl: Copy up only metadata during copy up where it makes sense (Miklos Szeredi) [1636875]
- [fs] ovl: During copy up, first copy up metadata and then data (Miklos Szeredi) [1636875]
- [fs] ovl: Provide a mount option metacopy=on/off for metadata copyup (Miklos Szeredi) [1636875]
- [fs] ovl: Move the copy up helpers to copy_up.c (Miklos Szeredi) [1636875]
- [fs] ovl: Initialize ovl_inode->redirect in ovl_get_inode() (Miklos Szeredi) [1636875]
- [fs] ovl: fix documentation of non-standard behavior (Miklos Szeredi) [1636875]
- [fs] ovl: obsolete "check_copy_up" module option (Miklos Szeredi) [1636875]
- [fs] vfs: remove open_flags from d_real() (Miklos Szeredi) [1636875]
- [fs] Revert "fsnotify: support overlayfs" (Miklos Szeredi) [1636875]
- [fs] Partially revert "locks: fix file locking on overlayfs" (Miklos Szeredi) [1636875]
- [fs] Revert "vfs: do get_write_access() on upper layer of overlayfs" (Miklos Szeredi) [1636875]
- [fs] Revert "vfs: add flags to d_real()" (Miklos Szeredi) [1636875]
- [fs] Revert "vfs: update ovl inode before relatime check" (Miklos Szeredi) [1636875]
- [fs] Revert "ovl: fix relatime for directories" (Miklos Szeredi) [1636875]
- [fs] vfs: fix freeze protection in mnt_want_write_file() for overlayfs (Miklos Szeredi) [1636875]
- [fs] Revert "ovl: don't allow writing ioctl on lower layer" (Miklos Szeredi) [1636875]
- [fs] Revert "ovl: fix may_write_real() for overlayfs directories" (Miklos Szeredi) [1636875]
- [fs] vfs: don't open real (Miklos Szeredi) [1636875]
- [fs] ovl: add reflink/copyfile/dedup support (Miklos Szeredi) [1636875]
- [fs] ovl: add O_DIRECT support (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_fiemap() (Miklos Szeredi) [1636875]
- [fs] ovl: add lsattr/chattr support (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_fallocate() (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_mmap() (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_fsync() (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_write_iter() (Miklos Szeredi) [1636875]
- [fs] ovl: add ovl_read_iter() (Miklos Szeredi) [1636875]
- [fs] ovl: add helper to return real file (Miklos Szeredi) [1636875]
- [fs] ovl: stack file ops (Miklos Szeredi) [1636875]
- [fs] ovl: deal with overlay files in ovl_d_real() (Miklos Szeredi) [1636875]
- [fs] ovl: copy up file size as well (Miklos Szeredi) [1636875]
- [fs] Revert "Revert "ovl: get_write_access() in truncate"" (Miklos Szeredi) [1636875]
- [fs] ovl: copy up inode flags (Miklos Szeredi) [1636875]
- [fs] ovl: copy up times (Miklos Szeredi) [1636875]
- [fs] vfs: export vfs_dedupe_file_range_one() to modules (Miklos Szeredi) [1636875]
- [fs] vfs: export vfs_ioctl() to modules (Miklos Szeredi) [1636875]
- [fs] vfs: make open_with_fake_path() not contribute to nr_files (Miklos Szeredi) [1636875]
- [fs] ovl: fix wrong use of impure dir cache in ovl_iterate() (Miklos Szeredi) [1636875]
- [fs] new helper: open_with_fake_path() (Miklos Szeredi) [1636875]
- [fs] now we can fold open_check_o_direct() into do_dentry_open() (Miklos Szeredi) [1636875]
- [fs] lift fput() on late failures into path_openat() (Miklos Szeredi) [1636875]
- [fs] fold put_filp() into fput() (Miklos Szeredi) [1636875]
- [fs] introduce FMODE_OPENED (Miklos Szeredi) [1636875]
- [fs] ->file_open(): lose cred argument (Miklos Szeredi) [1636875]
- [fs] security_file_open(): lose cred argument (Miklos Szeredi) [1636875]
- [fs] get rid of cred argument of vfs_open() and do_dentry_open() (Miklos Szeredi) [1636875]
- [fs] pass ->f_flags value to alloc_empty_file() (Miklos Szeredi) [1636875]
- [fs] pass creds to get_empty_filp(), make sure dentry_open() passes the right creds (Miklos Szeredi) [1636875]
- [fs] alloc_file(): switch to passing O_... flags instead of FMODE_... mode (Miklos Szeredi) [1636875]
- [fs] make sure do_dentry_open() won't return positive as an error (Miklos Szeredi) [1636875]
- [fs] create_pipe_files(): use fput() if allocation of the second file fails (Miklos Szeredi) [1636875]
- [fs] turn filp_clone_open() into inline wrapper for dentry_open() (Miklos Szeredi) [1636875]
- [fs] fold security_file_free() into file_free() (Miklos Szeredi) [1636875]
- [fs] vfs: dedupe: extract helper for a single dedup (Miklos Szeredi) [1636875]
- [fs] vfs: dedupe: rationalize args (Miklos Szeredi) [1636875]
- [fs] vfs: dedupe: return int (Miklos Szeredi) [1636875]
- [fs] vfs: limit size of dedupe (Miklos Szeredi) [1636875]
- [fs] ovl: set I_CREATING on inode being created (Miklos Szeredi) [1636875]

* Tue Oct 23 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-30.el8]
- [rpmspec] redhat spec: Add new perf tools file (Jiri Olsa) [1579484]
- [tools] perf tools: Fix use of alternatives to find JDIR (Jiri Olsa) [1579484]
- [net] net: sock_diag: Fix spectre v1 gadget in __sock_diag_cmd() (Paolo Abeni) [1637576]
- [thunderbolt] thunderbolt: Add Intel as copyright holder (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Convert rest of the driver files to use SPDX identifier (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Print connected devices (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Make the driver less verbose (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Remove a meaningless NULL pointer check before dma_pool_destroy (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Initialize after IOMMUs (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Do not handle ICM events after domain is stopped (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Add support for runtime PM (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Remove redundant variable 'approved' (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Use correct ICM commands in system suspend (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: No need to take tb->lock in domain suspend/complete (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Do not unnecessarily call ICM get route (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Use 64-bit DMA mask if supported by the platform (Jarod Wilson) [1588929]
- [thunderbolt] thunderbolt: Fix small typo in variable name (Jarod Wilson) [1588929]
- [mm] Revert x86/e820: put !E820_TYPE_RAM regions into memblock.reserved (Baoquan He) [1639450]
- [mm] mm: return zero_resv_unavail optimization (Baoquan He) [1639450]
- [mm] mm: zero remaining unavailable struct pages (Baoquan He) [1639450]
- [mm] mm: skip invalid pages block at a time in zero_resv_unresv() (Baoquan He) [1639450]
- [mm] docs/mm: memblock: update kernel-doc comments (Baoquan He) [1639450]
- [mm] mm/memblock: add a name for memblock flags enumeration (Baoquan He) [1639450]
- [block] blk-wbt: wake up all when we scale up, not down (Ming Lei) [1640035]

* Sat Oct 20 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-29.el8]
- [video] fbdev: make FB_BACKLIGHT a tristate (Rob Clark) [1589158]
- [kernel] EDAC: Raise the maximum number of memory controllers (Aristeu Rozanski) [1634077]
- [netdrv] i40e: disallow changing the number of descriptors when AF_XDP is on (Stefan Assmann) [1630760]
- [netdrv] i40e: clean zero-copy XDP Rx ring on shutdown/reset (Stefan Assmann) [1630760]
- [netdrv] i40e: clean zero-copy XDP Tx ring on shutdown/reset (Stefan Assmann) [1630760]
- [netdrv] i40e: Remove unused msglen parameter from virtchnl functions (Stefan Assmann) [1630760]
- [netdrv] i40e: fix double 'NIC Link is Down' messages (Stefan Assmann) [1630760]
- [netdrv] i40e: add a helper function to validate a VF based on the vf id (Stefan Assmann) [1630760]
- [netdrv] i40e: use declared variables for pf and hw (Stefan Assmann) [1630760]
- [netdrv] i40e: Unset promiscuous settings on VF reset (Stefan Assmann) [1630760]
- [netdrv] i40e: Fix VF's link state notification (Stefan Assmann) [1630760]
- [netdrv] intel-ethernet: use correct module license (Stefan Assmann) [1630760]
- [netdrv] i40e(vf): remove i40e_ethtool_stats.h header file (Stefan Assmann) [1630760]
- [netdrv] i40e: fix possible compiler warning in xsk TX path (Stefan Assmann) [1630760]
- [netdrv] i40e: add AF_XDP zero-copy Tx support (Stefan Assmann) [1630760]
- [netdrv] i40e: move common Tx functions to i40e_txrx_common.h (Stefan Assmann) [1630760]
- [netdrv] xsk: i40e: get rid of useless struct xdp_umem_props (Stefan Assmann) [1630760]
- [netdrv] i40e: add AF_XDP zero-copy Rx support (Stefan Assmann) [1630760]
- [netdrv] i40e: move common Rx functions to i40e_txrx_common.h (Stefan Assmann) [1630760]
- [netdrv] i40e: refactor Rx path for re-use (Stefan Assmann) [1630760]
- [netdrv] i40e: added queue pair disable/enable functions (Stefan Assmann) [1630760]
- [netdrv] i40e: Prevent deleting MAC address from VF when set by PF (Stefan Assmann) [1630760]
- [netdrv] i40e: hold the rtnl lock on clearing interrupt scheme (Stefan Assmann) [1630760]
- [netdrv] i40e: Check and correct speed values for link on open (Stefan Assmann) [1630760]
- [netdrv] i40e: report correct statistics when XDP is enabled (Stefan Assmann) [1630760]
- [netdrv] i40e: static analysis report from community (Stefan Assmann) [1630760]
- [netdrv] i40e: use correct length for strncpy (Stefan Assmann) [1630760]
- [netdrv] i40evf: Change a VF mac without reloading the VF driver (Stefan Assmann) [1630760]
- [netdrv] i40e: move ethtool stats boiler plate code to i40e_ethtool_stats.h (Stefan Assmann) [1630760]
- [netdrv] i40e: convert queue stats to i40e_stats array (Stefan Assmann) [1630760]
- [netdrv] i40e: fix condition of WARN_ONCE for stat strings (Stefan Assmann) [1630760]
- [netdrv] i40e_txrx: mark expected switch fall-through (Stefan Assmann) [1630760]
- [netdrv] i40e_main: mark expected switch fall-through (Stefan Assmann) [1630760]
- [netdrv] i40e: fix i40e_add_queue_stats data pointer update (Stefan Assmann) [1630760]
- [netdrv] i40e: Add AQ command for rearrange NVM structure (Stefan Assmann) [1630760]
- [netdrv] i40e: Add additional return code to i40e_asq_send_command (Stefan Assmann) [1630760]
- [netdrv] i40e: fix warning about shadowed ring parameter (Stefan Assmann) [1630760]
- [netdrv] i40e: remove unnecessary i variable causing -Wshadow warning (Stefan Assmann) [1630760]
- [netdrv] i40e: convert priority flow control stats to use helpers (Stefan Assmann) [1630760]
- [netdrv] i40e: convert VEB TC stats to use an i40e_stats array (Stefan Assmann) [1630760]
- [netdrv] i40e: Set fec_config when forcing link state (Stefan Assmann) [1630760]
- [netdrv] i40e: add helper to copy statistic values into ethtool buffer (Stefan Assmann) [1630760]
- [netdrv] i40e: add helper function for copying strings from stat arrays (Stefan Assmann) [1630760]
- [netdrv] i40e: Remove duplicated prepare call in i40e_shutdown (Stefan Assmann) [1630760]
- [netdrv] cls_flower: fix error values for commands not supported by drivers (Stefan Assmann) [1630760]
- [netdrv] net: drivers/net: Convert random_ether_addr to eth_random_addr (Stefan Assmann) [1630760]
- [net] ipv4: don't let PMTU updates increase route MTU (Sabrina Dubroca) [1638845]
- [net] ipv4: update fnhe_pmtu when first hop's MTU changes (Sabrina Dubroca) [1638845]
- [net] xsk: add a simple buffer reuse queue (Ivan Vecera) [1634774]
- [net] samples/bpf: add -c/--copy -z/--zero-copy flags to xdpsock (Ivan Vecera) [1634774]
- [net] add napi_if_scheduled_mark_missed (Ivan Vecera) [1634774]
- [net] xsk: expose xdp_umem_get_(data, dma) to drivers (Ivan Vecera) [1634774]
- [net] xdp: export xdp_rxq_info_unreg_mem_model (Ivan Vecera) [1634774]
- [net] xdp: implement convert_to_xdp_frame for MEM_TYPE_ZERO_COPY (Ivan Vecera) [1634774]
- [net] xdp: Helper function to clear kernel pointers in xdp_frame (Ivan Vecera) [1634774]
- [net] xsk: i40e: get rid of useless struct xdp_umem_props (Ivan Vecera) [1631809]
- [net] xdp: fix uninitialized 'err' variable (Ivan Vecera) [1631805]
- [tools] headers uapi: Update tools's copy of linux/if_link.h (Ivan Vecera) [1631805]
- [tools] selftests/bpf: add test for multiple programs (Ivan Vecera) [1631805]
- [net] netdevsim: add support for simultaneous driver and hw XDP (Ivan Vecera) [1631805]
- [net] xdp: support simultaneous driver and hw XDP attachment (Ivan Vecera) [1631805]
- [net] xdp: factor out common program/flags handling from drivers (Ivan Vecera) [1631805]
- [net] xdp: don't make drivers report attachment mode (Ivan Vecera) [1631805]
- [net] xdp: add per mode attributes for attached programs (Ivan Vecera) [1631805]
- [net] sched: cls_flower: set correct offload data in fl_reoffload (Ivan Vecera) [1631522]
- [net] sched: call reoffload op on block callback reg (Ivan Vecera) [1631522]
- [net] sched: cls_bpf: implement offload tcf_proto_op (Ivan Vecera) [1631522]
- [net] sched: cls_u32: implement offload tcf_proto_op (Ivan Vecera) [1631522]
- [net] sched: cls_matchall: implement offload tcf_proto_op (Ivan Vecera) [1631522]
- [net] sched: cls_flower: implement offload tcf_proto_op (Ivan Vecera) [1631522]
- [net] sched: add tcf_proto_op to offload a rule (Ivan Vecera) [1631522]
- [net] sched: pass extack pointer to block binds and cb registration (Ivan Vecera) [1631522]

* Fri Oct 19 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-28.el8]
- [rpmspec] kernel.spec: s390/zfcpdump: add -zfcpdump kernel variant (Philipp Rudo) [1567291]
- [kernel] rh_taint: correct loaddable module support dependencies (Philipp Rudo) [1567291]
- [powerpc] KVM: PPC: Book3S HV: Avoid crash from THP collapse during radix page fault (David Gibson) [1639555]
- [irqchip] irqchip/gic-v3-its: Allow use of LPI tables in reserved memory (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Register LPI tables with EFI config table (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Check that all RDs have the same property table (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Use pre-programmed redistributor tables with kdump kernels (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Allow use of pre-programmed LPI tables (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Keep track of property table's PA and VA (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Move pending table allocation to init time (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Split property table clearing from allocation (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Simplify LPI_PENDBASE_SZ usage (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Change initialization ordering for LPIs (Jeremy Linton) [1625746]
- [firmware] efi: add API to reserve memory persistently across kexec reboot (Jeremy Linton) [1625746]
- [firmware] efi/arm: libstub: add a root memreserve config table (Jeremy Linton) [1625746]
- [firmware] efi: honour memory reservations passed via a linux specific config table (Jeremy Linton) [1625746]
- [irqchip] irqchip/gic-v3-its: Cap lpi_id_bits to reduce memory footprint (Jeremy Linton) [1625746]
- [infiniband] RDMA/bnxt_re: Fix system crash during RDMA resource initialization (Selvin Xavier) [1637122]
- [infiniband] RDMA/bnxt_re: Fix couple of memory leaks that could lead to IOMMU call traces (Selvin Xavier) [1637120]
- [arm64] arm64: KVM: Sanitize PSTATE.M when being set from userspace (Wei Huang) [1635721] {CVE-2018-18021}
- [arm64] arm64: KVM: Tighten guest core register access from userspace (Wei Huang) [1635721] {CVE-2018-18021}
- [fs] fs/cifs: require sha512 (Leif Sahlberg) [1610619]
- [fs] smb3: simplify code by removing CONFIG_CIFS_SMB311 (Leif Sahlberg) [1610619]
- [fs] smb3: add support for statfs for smb3.1.1 posix extensions (Leif Sahlberg) [1610619]
- [fs] cifs: allow disabling insecure dialects in the config (Leif Sahlberg) [1610619]
- [fs] smb3: if server does not support posix do not allow posix mount option (Leif Sahlberg) [1610619]

* Tue Oct 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-27.el8]
- [security] cap_inode_getsecurity: use d_find_any_alias() instead of d_find_alias() (Joe Lawrence) [1638647]
- [powerpc] powerpc/cacheinfo: Report the correct shared_cpu_map on big-cores (Steve Best) [1639265]
- [powerpc] powerpc: Use cpu_smallcore_sibling_mask at SMT level on bigcores (Steve Best) [1639265]
- [powerpc] powerpc: Detect the presence of big-cores via ibm, thread-groups (Steve Best) [1639265]
- [x86] mark amd rome as unsupported (David Arcari) [1638506]
- [netdrv] qed: Add support for virtual link (Chad Dupuis) [1638013]
- [netdrv] qede: Add driver support for 20G link speed (Chad Dupuis) [1638013]
- [netdrv] qed: Add driver support for 20G link speed (Chad Dupuis) [1638013]
- [netdrv] qed: Fix shmem structure inconsistency between driver and the mfw (Chad Dupuis) [1638013]
- [netdrv] qed: Add missing device config for RoCE EDPM in UFP mode (Chad Dupuis) [1638013]
- [netdrv] qed: Add a flag which indicates if offload TC is set (Chad Dupuis) [1638013]
- [netdrv] qed: Do not add VLAN 0 tag to untagged frames in multi-function mode (Chad Dupuis) [1638013]
- [netdrv] qed: Fix populating the invalid stag value in multi function mode (Chad Dupuis) [1638013]
- [tools] perf python: Fix pyrf_evlist__read_on_cpu() interface (Jiri Olsa) [1628229]
- [tools] perf mmap: Store real cpu number in 'struct perf_mmap' (Jiri Olsa) [1628229]

* Tue Oct 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-26.el8]
- [fs] gfs2: Fix iomap buffered write support for journaled files (2) (Andreas Grunbacher) [1637944]
- [xen] xen/manage: don't complain about an empty value in control/sysrq node (Vitaly Kuznetsov) [1623344]
- [drm] drm/amdgpu: Silence harmless WARN_ON() during MST disable (Lyude Paul) [1638137]
- [netdrv] net: macb: Fix regression breaking non-MDIO fixed-link PHYs (Petr Oros) [1638259]
- [netdrv] net: macb: do not disable MDIO bus at open/close time (Petr Oros) [1638259]
- [fs] proc: restrict kernel stack dumps to root (Waiman Long) [1638044]
- [base] firmware: Always initialize the fw_priv list object (Waiman Long) [1638044]
- [base] firmware: Fix security issue with request_firmware_into_buf() (Waiman Long) [1638044]
- [fs] sysfs: Do not return POSIX ACL xattrs via listxattr (Waiman Long) [1638044]
- [fs] vfs: don't evict uninitialized inode (Waiman Long) [1638044]
- [fs] new primitive: discard_new_inode() (Waiman Long) [1638044]
- [arm64] arm64: jump_label.h: use asm_volatile_goto macro instead of "asm goto" (Waiman Long) [1638044]
- [kernel] sched/topology: Set correct NUMA topology type (Waiman Long) [1638044]
- [kernel] bpf: 32-bit RSH verification must truncate input before the ALU op (Waiman Long) [1638044]
- [mm] mm: madvise(MADV_DODUMP): allow hugetlbfs pages (Waiman Long) [1638044]
- [x86] x86/pti: Fix section mismatch warning/error (Waiman Long) [1638044]
- [kernel] uaccess: Fix is_source param for check_copy_size() in copy_to_iter_mcsafe() (Waiman Long) [1638044]
- [x86] x86/mm: Expand static page table for fixmap space (Waiman Long) [1638044]
- [fs] fs/lock: skip lock owner pid translation in case we are in init_pid_ns (Waiman Long) [1638044]
- [x86] perf/x86/intel/lbr: Fix incomplete LBR call stack (Waiman Long) [1638044]
- [kernel] perf/hw_breakpoint: Split attribute parse and commit (Waiman Long) [1638044]
- [kernel] bitfield: fix *_encode_bits() (Waiman Long) [1638044]
- [kernel] posix-timers: Sanitize overrun handling (Waiman Long) [1638044]
- [kernel] posix-timers: Make forward callback return s64 (Waiman Long) [1638044]
- [kernel] alarmtimer: Prevent overflow for relative nanosleep (Waiman Long) [1638044]
- [x86] x86/entry/64: Add two more instruction suffixes (Waiman Long) [1638044]
- [powerpc] powerpc/kdump: Handle crashkernel memory reservation failure (Waiman Long) [1638044]
- [s390] s390/mm: correct allocate_pgste proc_handler callback (Waiman Long) [1638044]
- [x86] x86/numa_emulation: Fix emulated-to-physical node mapping (Waiman Long) [1638044]
- [x86] x86/paravirt: Fix some warning messages (Waiman Long) [1638044]
- [kernel] sched/fair: Fix vruntime_normalized() for remote non-migration wakeup (Waiman Long) [1638044]
- [kernel] bpf/verifier: disallow pointer subtraction (Waiman Long) [1638044]
- [mm] mm: shmem.c: Correctly annotate new inodes for lockdep (Waiman Long) [1638044]
- [kernel] sched/core: Use smp_mb() in wake_woken_function() (Waiman Long) [1638044]
- [kernel] bpf: fix rcu annotations in compute_effective_progs() (Waiman Long) [1638044]
- [x86] x86/mm/pti: Add an overflow check to pti_clone_pmds() (Waiman Long) [1638044]
- [x86] x86/pti: Check the return value of pti_user_pagetable_walk_pmd() (Waiman Long) [1638044]
- [x86] x86/pti: Check the return value of pti_user_pagetable_walk_p4d() (Waiman Long) [1638044]
- [powerpc] powerpc/pseries/mm: call H_BLOCK_REMOVE (Steve Best) [1637116]
- [powerpc] powerpc/pseries/mm: factorize PTE slot computation (Steve Best) [1637116]
- [powerpc] powerpc/pseries/mm: Introducing FW_FEATURE_BLOCK_REMOVE (Steve Best) [1637116]
- [watchdog] watchdog/hpwdt: Disable PreTimeout when Timeout is smaller (Joseph Szczypek) [1632945]
- [watchdog] watchdog: hpwdt: Update Driver Documentation (Joseph Szczypek) [1632945]
- [watchdog] watchdog: hpwdt: Update version number (Joseph Szczypek) [1632945]
- [watchdog] watchdog: hpwdt: Module parameter alias (Joseph Szczypek) [1632945]
- [watchdog] watchdog: hpwdt: Display module parameters (Joseph Szczypek) [1632945]
- [watchdog] watchdog: hpwdt: Claim NMI from iLO (Joseph Szczypek) [1632945]
- [watchdog] watchdog: hpwdt: Initialize pretimeout from module parameter (Joseph Szczypek) [1632945]

* Sat Oct 13 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-25.el8]
- [mm] mm/sparse: delete old sparse_init and enable new one (Baoquan He) [1625105]
- [mm] mm/sparse: add new sparse_init_nid() and sparse_init() (Baoquan He) [1625105]
- [mm] mm/sparse: move buffer init/fini to the common place (Baoquan He) [1625105]
- [mm] mm/sparse: use the new sparse buffer functions in non-vmemmap (Baoquan He) [1625105]
- [mm] mm/sparse: abstract sparse buffer allocations (Baoquan He) [1625105]
- [mm] mm/sparse: optimize memmap allocation during sparse_init() (Baoquan He) [1625105]
- [mm] mm/sparse.c: add a new parameter 'data_unit_size' for alloc_usemap_and_memmap (Baoquan He) [1625105]
- [mm] mm/sparsemem.c: defer the ms->section_mem_map clearing (Baoquan He) [1625105]
- [mm] mm/sparse.c: add a static variable nr_present_sections (Baoquan He) [1625105]
- [mm] mm/sparse.c: make sparse_init_one_section void and remove check (Baoquan He) [1625105]
- [target] scsi: target: iscsi: cxgbit: fix csk leak (Arjun Vynipadath) [1628864]
- [target] scsi: target: iscsi: cxgbit: use pr_debug() instead of pr_info() (Arjun Vynipadath) [1628864]
- [infiniband] iw_cxgb4: only allow 1 flush on user qps (Arjun Vynipadath) [1628865]
- [infiniband] iw_cxgb4: pass window scale in flowc work request (Arjun Vynipadath) [1628865]
- [infiniband] iw_cxgb4: remove duplicate memcpy() in c4iw_create_listen() (Arjun Vynipadath) [1628865]
- [netdrv] mlxsw: spectrum_switchdev: Do not leak RIFs when removing bridge (Petr Oros) [1638268]
- [tty] tty: vt_ioctl: fix potential Spectre v1 (Prarit Bhargava) [1637123]
- [powerpc] powerpc/time: Add set_state_oneshot_stopped decrementer callback (Steve Best) [1638287]
- [powerpc] powerpc/time: Use clockevents_register_device(), fixing an issue with large decrementer (Steve Best) [1638287]
- [hwmon] hwmon: (nct6775) Fix potential Spectre v1 (Dean Nelson) [1637464]
- [vfio] vfio-pci: Disable binding to PFs with SR-IOV enabled (Alex Williamson) [1637871]
- [netdrv] net: hns3: fix page_offset overflow when CONFIG_ARM64_64K_PAGES (Petr Oros) [1638385]
- [netdrv] net: hns: fix skb->truesize underestimation (Petr Oros) [1638385]
- [netdrv] net: hns: fix length and page_offset overflow when CONFIG_ARM64_64K_PAGES (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix get_vector ops in hclgevf_main module (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix warning bug when doing lp selftest (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix for mac pause not disable in pfc mode (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix for mailbox message truncated problem (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix return value error in hns3_reset_notify_down_enet (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix for reset_level default assignment probelm (Petr Oros) [1638385]
- [netdrv] net: hns3: Reset net device with rtnl_lock (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix for phy link issue when using marvell phy driver (Petr Oros) [1638385]
- [netdrv] net: hns3: Fix for command format parsing error in hclge_is_all_function_id_zero (Petr Oros) [1638385]
- [net] xprtrdma: Fix disconnect regression (Don Dutile) [1635418]
- [infiniband] RDMA/uverbs: Fix validity check for modify QP (Don Dutile) [1635418]
- [infiniband] IB/srp: Avoid that sg_reset -d $srp_device triggers an infinite loop (Don Dutile) [1635418]
- [infiniband] ucma: fix a use-after-free in ucma_resolve_ip() (Don Dutile) [1635418]
- [infiniband] RDMA/uverbs: Atomically flush and mark closed the comp event queue (Don Dutile) [1635418]
- [infiniband] RDMA/mlx4: Ensure that maximal send/receive SGE less than supported by HW (Don Dutile) [1635418 1623100]
- [infiniband] RDMA/cma: Protect cma dev list with lock (Don Dutile) [1635418]
- [infiniband] IB/ipoib: Avoid a race condition between start_xmit and cm_rep_handler (Don Dutile) [1635418]
- [infiniband] RDMA/ucma: check fd type in ucma_migrate_id() (Don Dutile) [1635418]
- [infiniband] RDMA/rxe: Set wqe->status correctly if an unexpected response is received (Don Dutile) [1635418]
- [infiniband] IB/IPoIB: Set ah valid flag in multicast send flow (Don Dutile) [1635418]
- [infiniband] RDMA/core: Avoid holding lock while initializing fields on stack (Don Dutile) [1635418]
- [infiniband] IB/rxe: Drop QP0 silently (Don Dutile) [1635418]
- [infiniband] RDMA/umem: Don't hold mmap_sem for too long (Don Dutile) [1635418]
- [infiniband] IB/srpt: Fix srpt_cm_req_recv() error path (2/2) (Don Dutile) [1635418]
- [infiniband] IB/srpt: Fix srpt_cm_req_recv() error path (1/2) (Don Dutile) [1635418]
- [infiniband] RDMA: Fix storage of PortInfo CapabilityMask in the kernel (Don Dutile) [1635418]
- [infiniband] IB/core: type promotion bug in rdma_rw_init_one_mr() (Don Dutile) [1635418]
- [infiniband] RDMA/i40w: Hold read semaphore while looking after VMA (Don Dutile) [1635418]
- [infiniband] vmw_pvrdma: Release netdev when vmxnet3 module is removed (Don Dutile) [1635418]
- [infiniband] ib_srpt: Fix a use-after-free in __srpt_close_all_ch() (Don Dutile) [1635418]
- [infiniband] ib_srpt: Fix a use-after-free in srpt_close_ch() (Don Dutile) [1635418]
- [infiniband] IB/srpt: Support HCAs with more than two ports (Don Dutile) [1635418]
- [infiniband] IB/rxe: don't clear the tx queue on every transfer (Don Dutile) [1635418]
- [infiniband] IB/core: add max_send_sge and max_recv_sge attributes (Don Dutile) [1635418 1623100]
- [infiniband] IB/rxe: support for 802.1q VLAN on the listener (Don Dutile) [1635418]
- [netdrv] cxgb4: impose mandatory VLAN usage when non-zero TAG ID (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: when max_tx_rate is 0 disable tx rate limiting (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: do not return DUPLEX_UNKNOWN when link is down (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: expose stats fetched from firmware via debugfs (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: remove stats fetched from firmware (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: specify IQTYPE in fw_iq_cmd (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: Fix the condition to check if the card is T5 (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: Support ethtool private flags (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: Add support for FW_ETH_TX_PKT_VM_WR (Arjun Vynipadath) [1628863]
- [netdrv] cxgb4: Add flag tc_flower_initialized (Arjun Vynipadath) [1628863]
- [s390] s390/zcrypt: remove VLA usage from the AP bus (Philipp Rudo) [1637865]
- [s390] s390/ap_bus: replace PTR_RET with PTR_ERR_OR_ZERO (Philipp Rudo) [1637865]
- [s390] s390/crypto: fix gcc 8 stringop-truncation warning (Philipp Rudo) [1637865]
- [s390] s390/zcrypt: code beautify (Philipp Rudo) [1637865]
- [s390] s390/zcrypt: add copy_from_user length plausibility checks (Philipp Rudo) [1637865]
- [s390] s390/zcrypt: Show load of cards and queues in sysfs (Philipp Rudo) [1637865]
- [s390] s390/kvm: fix deadlock when killed by oom (Philipp Rudo) [1638264]
- [fs] xfs: fix data corruption w/ unaligned reflink ranges (Brian Foster) [1633476]
- [fs] xfs: fix data corruption w/ unaligned dedupe ranges (Brian Foster) [1633476]
- [fs] xfs: update ctime and remove suid before cloning files (Brian Foster) [1633476]
- [fs] xfs: zero posteof blocks when cloning above eof (Brian Foster) [1633476]
- [fs] xfs: refactor clonerange preparation into a separate helper (Brian Foster) [1633476]
- [netdrv] nfp: avoid buffer leak when FW communication fails (Petr Oros) [1638233]
- [netdrv] nfp: don't fail probe on pci_sriov_set_totalvfs() errors (Petr Oros) [1638233]
- [netdrv] nfp: wait for posted reconfigs when disabling the device (Petr Oros) [1638233]
- [netdrv] liquidio: fix hang when re-binding VF host drv after running DPDK VF driver (Petr Oros) [1638224]
- [netdrv] r8169: set RxConfig after tx/rx is enabled for RTL8169sb/8110sb devices (Petr Oros) [1638210]
- [netdrv] r8169: add support for NCube 8168 network card (Petr Oros) [1638210]
- [netdrv] r8169: don't use MSI-X on RTL8106e (Petr Oros) [1638210]
- [netdrv] r8169: don't use MSI-X on RTL8168g (Petr Oros) [1638210]
- [powerpc] KVM: PPC: Book3S HV: Fix guest r11 corruption with POWER9 TM workarounds (David Gibson) [1637766]
- [drm] drm/amdgpu: Suppress keypresses from ACPI_VIDEO events (Lyude Paul) [1631918]
- [infiniband] IB/hfi1: Remove race conditions in user_sdma send path (Alex Estrin) [1637068]
- [infiniband] IB/hfi1: Eliminate races in the SDMA send error path (Alex Estrin) [1637068]
- [infiniband] IB/hfi1: Fix destroy_qp hang after a link down (Alex Estrin) [1637068]
- [infiniband] IB/hfi1: Fix context recovery when PBC has an UnsupportedVL (Alex Estrin) [1637068]
- [infiniband] IB/hfi1: Invalid user input can result in crash (Alex Estrin) [1637068]
- [infiniband] IB/hfi1: Fix SL array bounds check (Alex Estrin) [1637068]
- [powerpc] powerpc/fadump: re-register firmware-assisted dump if already registered (Steve Best) [1637383]
- [powerpc] powerpc/fadump: cleanup crash memory ranges support (Steve Best) [1637383]
- [powerpc] powerpc/fadump: merge adjacent memory ranges to reduce PT_LOAD segements (Steve Best) [1637383]
- [powerpc] powerpc/fadump: handle crash memory ranges array index overflow (Steve Best) [1637383]
- [scsi] scsi: qedi: Initialize the stats mutex lock (Chad Dupuis) [1637245]
- [fs] gfs2: Fix iomap buffered write support for journaled files (Andreas Grunbacher) [1637944]
- [fs] gfs2: eliminate update_rgrp_lvb_unlinked (Andreas Grunbacher) [1637944]
- [fs] gfs2: Fix gfs2_testbit to use clone bitmaps (Andreas Grunbacher) [1637944]
- [fs] gfs2: Get rid of gfs2_ea_strlen (Andreas Grunbacher) [1637944]
- [fs] GFS2: rgrp free blocks used incorrectly (Andreas Grunbacher) [1637944]
- [fs] gfs2: remove redundant variable 'moved' (Andreas Grunbacher) [1637944]
- [fs] gfs2: use iomap_readpage for blocksize == PAGE_SIZE (Andreas Grunbacher) [1637944]
- [fs] gfs2: Use iomap for stuffed direct I/O reads (Andreas Grunbacher) [1637944]
- [fs] gfs2: fallocate_chunk: Always initialize struct iomap (Andreas Grunbacher) [1637944]
- [fs] gfs2: Remove gfs2_write_(begin,end) (Andreas Grunbacher) [1637944]
- [fs] gfs2: iomap direct I/O support (Andreas Grunbacher) [1637944]
- [fs] gfs2: gfs2_extent_length cleanup (Andreas Grunbacher) [1637944]
- [fs] gfs2: iomap buffered write support (Andreas Grunbacher) [1637944]
- [fs] gfs2: Further iomap cleanups (Andreas Grunbacher) [1637944]
- [fs] fs: gfs2: Adding new return type vm_fault_t (Andreas Grunbacher) [1637944]
- [fs] gfs2: using posix_acl_xattr_size instead of posix_acl_to_xattr (Andreas Grunbacher) [1637944]
- [fs] gfs2: Don't reject a supposedly full bitmap if we have blocks reserved (Andreas Grunbacher) [1637944]
- [fs] gfs2: Eliminate redundant ip->i_rgd (Andreas Grunbacher) [1637944]
- [fs] gfs2: Stop messing with ip->i_rgd in the rlist code (Andreas Grunbacher) [1637944]
- [fs] gfs2: call ktime_get_coarse_real_ts64() directly (Andreas Grunbacher) [1637944]
- [fs] gfs2: Minor clarification to __gfs2_punch_hole (Andreas Grunbacher) [1637944]
- [fs] gfs2: Don't withdraw under a spin lock (Andreas Grunbacher) [1637944]
- [fs] gfs2: eliminate rs_inum and reduce the size of gfs2 inodes (Andreas Grunbacher) [1637944]
- [drm] drm/nouveau/drm/nouveau: Grab runtime PM ref in nv50_mstc_detect() (Lyude Paul) [1628749]
- [drm] drm/nouveau/disp: fix DP disable race (Lyude Paul) [1628749]
- [drm] drm/nouveau/drm/nouveau: Don't forget to cancel hpd_work on suspend/unload (Lyude Paul) [1628749]
- [drm] drm/nouveau/drm/nouveau: Prevent handling ACPI HPD events too early (Lyude Paul) [1628749]
- [drm] drm/nouveau: Reset MST branching unit before enabling (Lyude Paul) [1628749]
- [drm] drm/nouveau: Only write DP_MSTM_CTRL when needed (Lyude Paul) [1628749]
- [drm] drm/nouveau: Remove useless poll_enable() call in drm_load() (Lyude Paul) [1628749]
- [drm] drm/nouveau: Remove useless poll_disable() call in switcheroo_set_state() (Lyude Paul) [1628749]
- [drm] drm/nouveau: Remove useless poll_enable() call in switcheroo_set_state() (Lyude Paul) [1628749]
- [drm] drm/nouveau: Fix deadlocks in nouveau_connector_detect() (Lyude Paul) [1628749]
- [drm] drm/nouveau/drm/nouveau: Use pm_runtime_get_noresume() in connector_detect() (Lyude Paul) [1628749]
- [drm] drm/nouveau/drm/nouveau: Fix deadlock with fb_helper with async RPM requests (Lyude Paul) [1628749]
- [drm] drm/nouveau: Remove duplicate poll_enable() in pmops_runtime_suspend() (Lyude Paul) [1628749]
- [drm] drm/nouveau/drm/nouveau: Fix bogus drm_kms_helper_poll_enable() placement (Lyude Paul) [1628749]
- [md] dm table: require that request-based DM be layered on blk-mq devices (Mike Snitzer) [1637682]
- [md] dm: rename DM_TYPE_MQ_REQUEST_BASED to DM_TYPE_REQUEST_BASED (Mike Snitzer) [1637682]
- [md] dm: remove legacy request-based IO path (Mike Snitzer) [1637682]
- [md] dm linear: fix linear_end_io conditional definition (Mike Snitzer) [1637682]
- [md] dm linear: eliminate linear_end_io call if CONFIG_DM_ZONED disabled (Mike Snitzer) [1637682]
- [md] dm: fix report zone remapping to account for partition offset (Mike Snitzer) [1637682]
- [md] dm cache: destroy migration_cache if cache target registration failed (Mike Snitzer) [1637682]
- [md] dm cache: fix resize crash if user doesn't reload cache table (Mike Snitzer) [1637682]
- [md] dm cache metadata: ignore hints array being too small during resize (Mike Snitzer) [1637682]
- [md] dm raid: remove bogus const from decipher_sync_action() return type (Mike Snitzer) [1637682]
- [md] dm mpath: fix attached_handler_name leak and dangling hw_handler_name pointer (Mike Snitzer) [1637682]
- [md] dm thin metadata: fix __udivdi3 undefined on 32-bit (Mike Snitzer) [1637682]
- [md] dm thin metadata: try to avoid ever aborting transactions (Mike Snitzer) [1637682]
- [md] dm raid: bump target version, update comments and documentation (Mike Snitzer) [1637682]
- [md] dm raid: fix RAID leg rebuild errors (Mike Snitzer) [1637682]
- [md] dm raid: fix rebuild of specific devices by updating superblock (Mike Snitzer) [1637682]
- [md] dm raid: fix stripe adding reshape deadlock (Mike Snitzer) [1637682]
- [md] dm raid: fix reshape race on small devices (Mike Snitzer) [1637682]
- [md] dm: disable CRYPTO_TFM_REQ_MAY_SLEEP to fix a GFP_KERNEL recursion deadlock (Mike Snitzer) [1637682]
- [md] dm verity: fix crash on bufio buffer that was allocated with vmalloc (Mike Snitzer) [1637682]
- [md] dm writecache: fix a crash due to reading past end of dirty_bitmap (Mike Snitzer) [1637682]
- [md] dm crypt: don't decrease device limits (Mike Snitzer) [1637682]
- [md] dm cache metadata: set dirty on all cache blocks after a crash (Mike Snitzer) [1637682]
- [md] dm snapshot: remove stale FIXME in snapshot_map() (Mike Snitzer) [1637682]
- [md] dm snapshot: improve performance by switching out_of_order_list to rbtree (Mike Snitzer) [1637682]
- [md] dm kcopyd: avoid softlockup in run_complete_job (Mike Snitzer) [1637682]
- [md] dm cache metadata: save in-core policy_hint_size to on-disk superblock (Mike Snitzer) [1637682]
- [md] dm thin: stop no_space_timeout worker when switching to write-mode (Mike Snitzer) [1637682]
- [md] dm kcopyd: return void from dm_kcopyd_copy() (Mike Snitzer) [1637682]
- [md] dm thin: include metadata_low_watermark threshold in pool status (Mike Snitzer) [1637682]
- [md] dm writecache: report start_sector in status line (Mike Snitzer) [1637682]
- [md] dm crypt: convert essiv from ahash to shash (Mike Snitzer) [1637682]
- [md] dm crypt: use wake_up_process() instead of a wait queue (Mike Snitzer) [1637682]
- [md] dm integrity: recalculate checksums on creation (Mike Snitzer) [1637682]
- [md] dm integrity: flush journal on suspend when using separate metadata device (Mike Snitzer) [1637682]
- [md] dm integrity: use version 2 for separate metadata (Mike Snitzer) [1637682]
- [md] dm integrity: allow separate metadata device (Mike Snitzer) [1637682]
- [md] dm integrity: add ic->start in get_data_sector() (Mike Snitzer) [1637682]
- [md] dm integrity: report provided data sectors in the status (Mike Snitzer) [1637682]
- [md] dm integrity: implement fair range locks (Mike Snitzer) [1637682]
- [md] dm integrity: decouple common code in dm_integrity_map_continue() (Mike Snitzer) [1637682]
- [md] dm integrity: change 'suspending' variable from bool to int (Mike Snitzer) [1637682]
- [md] dm delay: add flush as a third class of IO (Mike Snitzer) [1637682]
- [md] dm delay: refactor repetitive code (Mike Snitzer) [1637682]
- [md] dm cache: only allow a single io_mode cache feature to be requested (Mike Snitzer) [1637682]
- [md] dm thin: update stale "Status" Documentation (Mike Snitzer) [1637682]
- [pci] PCI: Reprogram bridge prefetch registers on resume (Myron Stowe) [1637155]
- [input] Input: xen-kbdfront - fix multi-touch XenStore node's locations (Benjamin Tissoires) [1637027]
- [input] Input: elantech - enable middle button of touchpad on ThinkPad P72 (Benjamin Tissoires) [1637027]
- [hid] HID: i2c-hid: Use devm to allocate i2c_hid struct (Benjamin Tissoires) [1637027]
- [hid] HID: input: fix leaking custom input node name (Benjamin Tissoires) [1637027]
- [hid] HID: core: fix grouping by application (Benjamin Tissoires) [1637027]
- [hid] HID: multitouch: fix Elan panels with 2 input modes declaration (Benjamin Tissoires) [1637027]
- [input] Input: do not use WARN() in input_alloc_absinfo() (Benjamin Tissoires) [1637027]
- [s390] s390: vfio-ap: setup APCB mask using KVM dedicated function (Cornelia Huck) [1508118]
- [s390] KVM: s390: Tracing APCB changes (Cornelia Huck) [1508118]
- [s390] KVM: s390: fix locking for crypto setting error path (Cornelia Huck) [1508118]
- [s390] s390: doc: detailed specifications for AP virtualization (Cornelia Huck) [1508118]
- [s390] KVM: s390: CPU model support for AP virtualization (Cornelia Huck) [1508118]
- [s390] KVM: s390: device attrs to enable/disable AP interpretation (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: allow guest FORMAT-0 CRYCB on host FORMAT-2 (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: allow guest FORMAT-1 CRYCB on host FORMAT-2 (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: allow guest FORMAT-0 CRYCB on host FORMAT-1 (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: allow CRYCB FORMAT-0 (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: allow CRYCB FORMAT-1 (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: Allow CRYCB FORMAT-2 (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: Make use of CRYCB FORMAT2 clear (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: Do the CRYCB validation first (Cornelia Huck) [1508118]
- [s390] KVM: s390: Clear Crypto Control Block when using vSIE (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: implement VFIO_DEVICE_RESET ioctl (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: zeroize the AP queues (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: implement VFIO_DEVICE_GET_INFO ioctl (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: implement mediated device open callback (Cornelia Huck) [1508118]
- [s390] KVM: s390: interface to clear CRYCB masks (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: sysfs interface to view matrix mdev matrix (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: sysfs interfaces to configure control domains (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: sysfs interfaces to configure domains (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: sysfs interfaces to configure adapters (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: register matrix device with VFIO mdev framework (Cornelia Huck) [1508118]
- [s390] s390: vfio-ap: base implementation of VFIO AP device driver (Cornelia Huck) [1508118]
- [s390] KVM: s390: refactor crypto initialization (Cornelia Huck) [1508118]
- [s390] KVM: s390: introduce and use KVM_REQ_VSIE_RESTART (Cornelia Huck) [1508118]
- [s390] KVM: s390: vsie: simulate VCPU SIE entry/exit (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: hex string mask improvements for apmask and aqmask (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: AP bus support for alternate driver(s) (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: switch return type to bool for ap_instructions_available() (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: fix ap_instructions_available() returncodes (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: Integrate ap_asm.h into include/asm/ap.h (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: Review inline assembler constraints (Cornelia Huck) [1508118]
- [s390] s390/zcrypt: Add ZAPQ inline function (Cornelia Huck) [1508118]
- [net] ipv6: use rt6_info members when dst is set in rt6_fill_node (Xin Long) [1625864 1625803 1625117]

* Thu Oct 11 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-24.el8]
- [netdrv] amd-xgbe: use dma_mapping_error to check map errors (David Arcari) [1637666]
- [crypto] crypto: qat - Fix KASAN stack-out-of-bounds bug in adf_probe() (Waiman Long) [1629547]
- [powerpc] powerpc: fix csum_ipv6_magic() on little endian platforms (Diego Domingos) [1625579]
- [net] smc: generic netlink family should be __ro_after_init (Philipp Rudo) [1632435]
- [net] net/smc: fix sizeof to int comparison (Philipp Rudo) [1632435]
- [net] net/smc: no urgent data check for listen sockets (Philipp Rudo) [1632435]
- [net] net/smc: enable fallback for connection abort in state INIT (Philipp Rudo) [1632435]
- [net] net/smc: remove duplicate mutex_unlock (Philipp Rudo) [1632435]
- [net] net/smc: fix non-blocking connect problem (Philipp Rudo) [1632435]
- [net] net/smc: send response to test link signal (Philipp Rudo) [1632435]
- [net] net: simplify sock_poll_wait (Philipp Rudo) [1632435]
- [net] net/smc: Simplify ib_post_(send|recv|srq_recv)() calls (Philipp Rudo) [1632435]
- [net] net/smc: Remove a WARN_ON() statement (Philipp Rudo) [1632435]
- [powerpc] KVM: PPC: Book3S HV: Add NO_HASH flag to GET_SMMU_INFO ioctl result (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Add a VM capability to enable nested virtualization (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Add nested shadow page tables to debugfs (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Allow HV module to load without hypervisor mode (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Handle differing endianness for H_ENTER_NESTED (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Sanitise hv_regs on nested guest entry (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Add one-reg interface to virtual PTCR register (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Don't access HFSCR, LPIDR or LPCR when running nested (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Invalidate TLB when nested vcpu moves physical cpu (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Use hypercalls for TLB invalidation when nested (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Implement H_TLB_INVALIDATE hcall (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Introduce rmap to track nested guest mappings (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Handle page fault for a nested guest (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Handle hypercalls correctly when nested (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Use XICS hypercalls when running as a nested hypervisor (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Nested guest entry via hypercall (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Framework and hcall stubs for nested virtualization (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Use kvmppc_unmap_pte() in kvm_unmap_radix() (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Refactor radix page fault handler (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Make kvmppc_mmu_radix_xlate process/partition table agnostic (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Clear partition table entry on vm teardown (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Use ccr field in pt_regs struct embedded in vcpu struct (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Add a debugfs file to dump radix mappings (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Handle hypervisor instruction faults better (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Streamlined guest entry/exit path on P9 for radix guests (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Call kvmppc_handle_exit_hv() with vcore unlocked (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S: Rework TM save/restore code and make it C-callable (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Simplify real-mode interrupt handling (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Extract PMU save/restore operations as C-callable functions (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Move interrupt delivery on guest entry to C code (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S HV: Remove left-over code in XICS-on-XIVE emulation (Suraj Jitindar Singh) [1505999]
- [powerpc] KVM: PPC: Book3S: Simplify external interrupt handling (Suraj Jitindar Singh) [1505999]
- [powerpc] powerpc: Turn off CPU_FTR_P9_TM_HV_ASSIST in non-hypervisor mode (Suraj Jitindar Singh) [1505999]
- [powerpc] powerpc/64s: Remove POWER9 DD1 support (Suraj Jitindar Singh) [1505999]
- [netdrv] net/mlx5: Add Fast teardown support (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Set vlan masks for all offloaded TC rules (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: E-Switch, Fix out of bound access when setting vport rate (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Avoid unbounded peer devices when unpairing TC hairpin rules (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Cache the system image guid (Alaa Hleihel) [1636554]
- [netdrv] mlx5: remove ndo_poll_controller (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Check for SQ and not RQ state when modifying hairpin SQ (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Fix read from coherent memory (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: don't set CHECKSUM_COMPLETE on SCTP packets (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Set ECN for received packets using CQE indication (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Fix possible deadlock from lockdep when adding fte to fg (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Check for error in mlx5_attach_interface (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Consider PCI domain in search for next dev (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Fix not releasing read lock when adding flow rules (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: E-Switch, Fix memory leak when creating switchdev mode FDB tables (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Use u16 for Work Queue buffer strides offset (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Use u16 for Work Queue buffer fragment size (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Fix debugfs cleanup in the device init/remove flow (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Fix use-after-free in self-healing flow (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Make function mlx5i_grp_sw_update_stats() static (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: IPoIB, Use priv stats in completion rx flow (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: IPoIB, Add ndo stats support for IPoIB child devices (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: IPoIB, Add ndo stats support for IPoIB netdevices (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: IPoIB, Initialize max_opened_tc in mlx5i_init flow (Alaa Hleihel) [1636554]
- [netdrv] IB/mlx5: Fix leaking stack memory to userspace (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Reorganize the makefile (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: clock.c depends on CONFIG_PTP_1588_CLOCK (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: vxlan.c depends on CONFIG_VXLAN (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Move flow steering declarations into en/fs.h (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add CONFIG_MLX5_EN_ARFS for accelerated flow steering support (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add CONFIG_MLX5_EN_RXNFC for ethtool rx nfc (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Ethtool steering, move ethtool callbacks (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Reduce command polling interval (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Use max_num_eqs for calculation of required MSIX vectors (Alaa Hleihel) [1636554]
- [netdrv] RDMA/mlx5: Fix shift overflow in mlx5_ib_create_wq (Alaa Hleihel) [1636554]
- [netdrv] overflow.h: Add arithmetic shift helper (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Fix uninitialized variable (Alaa Hleihel) [1636554]
- [netdrv] RDMA: Fix return code check in rdma_set_cq_moderation (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, move vxlan logic to core driver (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, add sync lock for add/del vxlan port (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, return values for add/del port (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, rename from mlx5e to mlx5 (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, rename struct mlx5e_vxlan to mlx5_vxlan_port (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, move netdev only logic to en_main.c (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, add direct delete function (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, cleanup an unused member in vxlan work (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, replace ports radix-tree with hash table (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, check maximum number of UDP ports (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Vxlan, reflect 4789 UDP port default addition to software database (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Move XDP related code into new XDP files (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Restrict the combination of large MTU and XDP (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Gather all XDP pre-requisite checks in a single function (Alaa Hleihel) [1636554]
- [netdrv] IB/mlx5: avoid excessive warning msgs when creating VFs on 2nd port (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Use PARTIAL_GSO for UDP segmentation (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Remove redundant WARN when we cannot find neigh entry (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Fix tristate and description for MLX5 module (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Better return types for CQE API (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Use ERR_CAST() instead of coding it (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Add missing SET_DRIVER_VERSION command translation (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: fix uaccess beyond "count" in debugfs read/write handlers (Alaa Hleihel) [1636554]
- [netdrv] IB/mlx5: Honor cnt_set_id_valid flag instead of set_id (Alaa Hleihel) [1636554]
- [infiniband] IB/mlx5: fix uaccess beyond "count" in debugfs read/write handlers (Alaa Hleihel) [1636554]
- [infiniband] IB/mlx5: Fix GRE flow specification (Alaa Hleihel) [1636554]
- [infiniband] IB/mlx5: Remove set-but-not-used variables (Alaa Hleihel) [1636554]
- [infiniband] RDMA/mlx5: Don't leak UARs in case of free fails (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Update NIC HW stats on demand only (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add counter for total num of NOP operations (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add counter for MPWQE filler strides (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add channel events counter (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add a counter for congested UMRs (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add NAPI statistics (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add XDP_TX completions statistics (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add TX completions statistics (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: RX, Use existing WQ local variable (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Convert large order kzalloc allocations to kvzalloc (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add UDP GSO remaining counter (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5e: Add UDP GSO support (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Rate limit errors in command interface (Alaa Hleihel) [1636554]
- [netdrv] net/mlx5: Prevent warns in dmesg upon firmware commands (Alaa Hleihel) [1636554]
- [netdrv] mlx4: remove ndo_poll_controller (Alaa Hleihel) [1636553]
- [netdrv] net/mlx4: Use cpumask_available for eq->affinity_mask (Alaa Hleihel) [1636553]
- [netdrv] net/mlx4/en_rx: Mark expected switch fall-throughs (Alaa Hleihel) [1636553]
- [netdrv] net/mlx4/mcg: Mark expected switch fall-throughs (Alaa Hleihel) [1636553]
- [infiniband] IB/mlx4: Use 4K pages for kernel QP's WQE buffer (Alaa Hleihel) [1636553]
- [netdrv] net/mlx4_core: Allow MTTs starting at any index (Alaa Hleihel) [1636553]
- [infiniband] IB/mlx4: Test port number before querying type (Alaa Hleihel) [1636553]
- [powerpc] powerpc/numa: Skip onlining a offline node in kdump path (Steve Best) [1637118]
- [netdrv] net: aquantia: Make function aq_fw1x_set_power() static (David Arcari) [1636533]
- [netdrv] net: aquantia: memory corruption on jumbo frames (David Arcari) [1636533 1630377]
- [netdrv] net: aquantia: bump driver version (David Arcari) [1636533]
- [netdrv] net: aquantia: renaming for better visibility (David Arcari) [1636533]
- [netdrv] net: aquantia: whitespace changes (David Arcari) [1636533]
- [netdrv] net: aquantia: implement EEE support (David Arcari) [1636533]
- [netdrv] net: aquantia: implement WOL support (David Arcari) [1636533]
- [netdrv] net: aquantia: definitions for WOL (David Arcari) [1636533]
- [netdrv] net: aquantia: fix hw_atl_utils_fw_upload_dwords (David Arcari) [1636533]
- [netdrv] net: aquantia: Make some functions static (David Arcari) [1636533]
- [netdrv] net: aquantia: bump driver version (David Arcari) [1636533]
- [netdrv] net: aquantia: Add renegotiate ethtool operation support (David Arcari) [1636533]
- [netdrv] net: aquantia: Implement rx/tx flow control ethtools callback (David Arcari) [1636533]
- [netdrv] net: aquantia: Improve adapter init/deinit logic (David Arcari) [1636533]
- [netdrv] net: aquantia: Ethtool based ring size configuration (David Arcari) [1636533]
- [wireless] ath10k: fix memory leak of tpc_stats (Petr Oros) [1637528]
- [wireless] ath10k: snoc: use correct bus-specific pointer in RX retry (Petr Oros) [1637528]
- [wireless] ath10k: fix incorrect size of dma_free_coherent in ath10k_ce_alloc_src_ring_64 (Petr Oros) [1637528]
- [wireless] brcmsmac: fix wrap around in conversion from constant to s16 (Petr Oros) [1637528]
- [wireless] mt76x2: fix mrr idx/count estimation in mt76x2_mac_fill_tx_status() (Petr Oros) [1637528]
- [wireless] ath10k: transmit queued frames after processing rx packets (Petr Oros) [1637528]
- [wireless] ath10k: protect ath10k_htt_rx_ring_free with rx_ring.lock (Petr Oros) [1637528]
- [wireless] ath10k: use locked skb_dequeue for rx completions (Petr Oros) [1637528]
- [wireless] ath10k: sdio: set skb len for all rx packets (Petr Oros) [1637528]
- [wireless] ath10k: sdio: use same endpoint id for all packets in a bundle (Petr Oros) [1637528]
- [wireless] iwlwifi: cancel the injective function between hw pointers to tfd entry index (Petr Oros) [1637528]
- [wireless] ath10k: disable bundle mgmt tx completion event support (Petr Oros) [1637528]
- [wireless] ath10k: prevent active scans on potential unusable channels (Petr Oros) [1637528]
- [wireless] ath9k_hw: fix channel maximum power level test (Petr Oros) [1637528]
- [wireless] ath9k: report tx status on EOSP (Petr Oros) [1637528]
- [wireless] iwlwifi: pcie: don't access periphery registers when not available (Petr Oros) [1637528]
- [wireless] brcmfmac: fix brcmf_wiphy_wowl_params() NULL pointer dereference (Petr Oros) [1637528]
- [netdrv] be2net: don't flip hw_features when VXLANs are added/deleted (Petr Oros) [1637133]
- [netdrv] be2net: Fix memory leak in be_cmd_get_profile_config() (Petr Oros) [1637133]
- [netdrv] be2net: Mark expected switch fall-through (Petr Oros) [1637133]
- [netdrv] be2net: fix spelling mistake "seqence" -> "sequence" (Petr Oros) [1637133]
- [netdrv] be2net: Update the driver version to 12.0.0.0 (Petr Oros) [1637133]
- [netdrv] be2net: gather debug info and reset adapter (only for Lancer) on a tx-timeout (Petr Oros) [1637133]
- [netdrv] be2net: move rss_flags field in rss_info to ensure proper alignment (Petr Oros) [1637133]
- [netdrv] be2net: re-order fields in be_error_recovert to avoid hole (Petr Oros) [1637133]
- [netdrv] be2net: remove unused tx_jiffies field from be_tx_stats (Petr Oros) [1637133]
- [netdrv] be2net: move txcp field in be_tx_obj to eliminate holes in the struct (Petr Oros) [1637133]
- [netdrv] be2net: reorder fields in be_eq_obj structure (Petr Oros) [1637133]
- [netdrv] be2net: remove desc field from be_eq_obj (Petr Oros) [1637133]
- [netdrv] be2net: remove unused old custom busy-poll fields (Petr Oros) [1637133]
- [netdrv] be2net: remove unused old AIC info (Petr Oros) [1637133]
- [x86] x86/spec_ctrl/compat: Call IBRS_ENTRY only after valid kernel stack (Waiman Long) [1636843]
- [acpi] ACPI/PPTT: Handle architecturally unknown cache types (Jeremy Linton) [1636567]
- [base] drivers: base: cacheinfo: Do not populate sysfs for unknown cache types (Jeremy Linton) [1636567]
- [fs] getxattr: use correct xattr length (Lukas Czerner) [1637049]
- [x86] Mark Intel Cascade Lake supported (Steve Best) [1636651]
- [x86] x86/boot: Fix kexec booting failure in the SEV bit detection code (Kairui Song) [1632514]
- [scsi] scsi: megaraid_sas: driver version upgrade (Tomas Henzl) [1635565]
- [scsi] scsi: megaraid_sas: Support FW provided TM timeout values (Tomas Henzl) [1635565]
- [scsi] scsi: megaraid_sas: Return immediately from wait_for_adapter_operational after kill adapter (Tomas Henzl) [1635565]
- [scsi] scsi: megaraid_sas: Update controller info during resume (Tomas Henzl) [1635565]
- [scsi] scsi: megaraid_sas: Do not do Kill adapter if GET_CTRL_INFO times out (Tomas Henzl) [1635565]
- [scsi] qla2xxx: Update driver version to 10.00.00.07.08.0-k (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Check for Register disconnect (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix driver hang when FC-NVMe LUNs are configured (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix re-using LoopID when handle is in use (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix duplicate switch database entries (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix NVMe session hang on unload (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix iIDMA error (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix stalled relogin (Himanshu Madhani) [1633373]
- [scsi] scsi: qla2xxx: Fix unintended Logout (Himanshu Madhani) [1633373]
- [powerpc] powerpc/pseries: Disable CPU hotplug across migrations (Steve Best) [1633587]
- [block] blk-mq: I/O and timer unplugs are inverted in blktrace (Ming Lei) [1634330]
- [block] block: fix deadline elevator drain for zoned block devices (Ming Lei) [1634333]
- [block] blk-mq: Allow blocking queue tag iter callbacks (Ming Lei) [1634328]
- [block] block: use nanosecond resolution for iostat (Ming Lei) [1634329]
- [block] null_blk: fix zoned support for non-rq based operation (Ming Lei) [1634324]
- [block] blk-cgroup: increase number of supported policies (Ming Lei) [1634335]
- [block] block: bfq: swap puts in bfqg_and_blkg_put (Ming Lei) [1634334]
- [block] block: don't warn when doing fsync on read-only devices (Ming Lei) [1634331]
- [block] blkcg: use tryget logic when associating a blkg with a bio (Ming Lei) [1634332]
- [block] blkcg: delay blkg destruction until after writeback has (Ming Lei) [1634332]
- [block] Revert "blk-throttle: fix race between (Ming Lei) [1634332]
- [block] blk-wbt: remove dead code (Ming Lei) [1634326]
- [block] blk-wbt: improve waking of tasks (Ming Lei) [1634326]
- [block] blk-wbt: abstract out end IO completion handler (Ming Lei) [1634326]

* Tue Oct 09 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-23.el8]
- [dma] driver/dma/ioat: Call del_timer_sync() without holding prep_lock (Waiman Long) [1607654]
- [netdrv] bnxt_en: Fix VF mac address regression (Jonathan Toppins) [1635846]
- [netdrv] bnxt_en: Do not adjust max_cp_rings by the ones used by RDMA (Jonathan Toppins) [1635846]
- [netdrv] bnxt_en: Clean up unused functions (Jonathan Toppins) [1635846]
- [fs] fsnotify: fix ignore mask logic in fsnotify() (Lukas Czerner) [1635537]
- [net] net/af_iucv: locate IUCV header via skb_network_header() (Philipp Rudo) [1635332]
- [net] net/af_iucv: drop inbound packets with invalid flags (Philipp Rudo) [1635332]
- [net] net/af_iucv: fix skb handling on HiperTransport xmit error (Philipp Rudo) [1635332]
- [hid] HID: i2c-hid: Fix flooded incomplete report after S3 on Rayd touchscreen (David Arcari) [1635746]
- [i2c] i2c: core: ACPI: Make acpi_gsb_i2c_read_bytes() check i2c_transfer return value (David Arcari) [1635746]
- [i2c] i2c: designware: Re-init controllers with pm_disabled set on resume (David Arcari) [1635746]
- [i2c] i2c: core: ACPI: Properly set status byte to 0 for multi-byte writes (David Arcari) [1635746]
- [fs] fs/quota: Fix spectre gadget in do_quotactl (Lukas Czerner) [1635521]
- [fs] xfs: fix error handling in xfs_bmap_extents_to_btree (Brian Foster) [1633171]
- [fs] xfs: remove invalid log recovery first/last cycle check (Brian Foster) [1633171]
- [fs] xfs: validate inode di_forkoff (Brian Foster) [1633171]
- [fs] xfs: skip delalloc COW blocks in xfs_reflink_end_cow (Brian Foster) [1633171]
- [fs] xfs: don't treat unknown di_flags2 as corruption in scrub (Brian Foster) [1633171]
- [fs] xfs: remove duplicated include from alloc.c (Brian Foster) [1633171]
- [fs] xfs: don't bring in extents in xfs_bmap_punch_delalloc_range (Brian Foster) [1633171]
- [fs] xfs: fix transaction leak in xfs_reflink_allocate_cow() (Brian Foster) [1633171]
- [fs] xfs: avoid lockdep false positives in xfs_trans_alloc (Brian Foster) [1633171]
- [fs] xfs: refactor xfs_buf_log_item reference count handling (Brian Foster) [1633171]
- [fs] xfs: clean up xfs_trans_brelse() (Brian Foster) [1633171]
- [fs] xfs: don't unlock invalidated buf on aborted tx commit (Brian Foster) [1633171]
- [fs] xfs: remove last of unnecessary xfs_defer_cancel() callers (Brian Foster) [1633171]
- [fs] xfs: don't crash the vfs on a garbage inline symlink (Brian Foster) [1633171]
- [fs] iomap: set page dirty after partial delalloc on mkwrite (Brian Foster) [1633171]
- [fs] xfs: sanity check ag header values in xrep_calc_ag_resblks (Brian Foster) [1633171]
- [fs] xfs: recalculate summary counters at mount time if icount is bad (Brian Foster) [1633171]
- [fs] xfs: fix a null pointer dereference in xfs_bmap_extents_to_btree (Brian Foster) [1633171]
- [fs] xfs: remove b_last_holder & associated macros (Brian Foster) [1633171]
- [fs] xfs: repair the AGI (Brian Foster) [1633171]
- [fs] xfs: repair the AGFL (Brian Foster) [1633171]
- [fs] xfs: repair the AGF (Brian Foster) [1633171]
- [fs] xfs: remove dead error handling code in xfs_dquot_disk_alloc() (Brian Foster) [1633171]
- [fs] xfs: use WRITE_ONCE to update if_seq (Brian Foster) [1633171]
- [fs] xfs: fix a comment in xfs_log_reserve (Brian Foster) [1633171]
- [fs] xfs: only validate summary counts on primary superblock (Brian Foster) [1633171]
- [fs] xfs: substitute spaces with tabs (Brian Foster) [1633171]
- [fs] xfs: fold dfops into the transaction (Brian Foster) [1633171]
- [fs] xfs: always defer agfl block frees (Brian Foster) [1633171]
- [fs] xfs: pass transaction to xfs_defer_add() (Brian Foster) [1633171]
- [fs] xfs: replace xfs_defer_ops ->dop_pending with on-stack list (Brian Foster) [1633171]
- [fs] xfs: cancel dfops on xfs_defer_finish() error (Brian Foster) [1633171]
- [fs] xfs: clean out superfluous dfops dop params/vars (Brian Foster) [1633171]
- [fs] xfs: drop dop param from xfs_defer_op_type ->finish_item() callback (Brian Foster) [1633171]
- [fs] xfs: automatic dfops inode relogging (Brian Foster) [1633171]
- [fs] xfs: automatic dfops buffer relogging (Brian Foster) [1633171]
- [fs] xfs: add missing defer ijoins for held inodes (Brian Foster) [1633171]
- [fs] xfs: replace dop_low with transaction flag (Brian Foster) [1633171]
- [fs] xfs: pass transaction to dfops reset/move helpers (Brian Foster) [1633171]
- [fs] xfs: remove unused __xfs_defer_cancel() internal helper (Brian Foster) [1633171]
- [fs] xfs: use transaction for intent recovery instead of raw dfops (Brian Foster) [1633171]
- [fs] xfs: refactor internal dfops initialization (Brian Foster) [1633171]
- [fs] xfs: check da node magic in _node_lookup_int (Brian Foster) [1633171]
- [fs] xfs: use a local variable for magic number in xfs_da3_node_lookup_int (Brian Foster) [1633171]
- [fs] xfs: refactor log recovery check (Brian Foster) [1633171]
- [fs] xfs: move extent busy tree initialization to xfs_initialize_perag (Brian Foster) [1633171]
- [fs] xfs: avoid COW fork extent lookups in writeback if the fork didn't change (Brian Foster) [1633171]
- [fs] xfs: maintain a sequence count for inode fork manipulations (Brian Foster) [1633171]
- [fs] xfs: check for unknown v5 feature bits in superblock write verifier (Brian Foster) [1633171]
- [fs] xfs: verify icount in superblock write (Brian Foster) [1633171]
- [fs] libxfs: add more bounds checking to sb sanity checks (Brian Foster) [1633171]
- [fs] xfs: refactor superblock verifiers (Brian Foster) [1633171]
- [fs] xfs: refactor the xrep_extent_list into xfs_bitmap (Brian Foster) [1633171]
- [fs] xfs: introduce a new xfs_inode_has_cow_data helper (Brian Foster) [1633171]
- [fs] xfs: remove the xfs_ifork_t typedef (Brian Foster) [1633171]
- [fs] xfs: simplify xfs_idata_realloc (Brian Foster) [1633171]
- [fs] xfs: remove if_real_bytes (Brian Foster) [1633171]
- [fs] xfs: move the repair extent list into its own file (Brian Foster) [1633171]
- [fs] xfs: pass transaction lock while setting up agresv on cyclic metadata (Brian Foster) [1633171]
- [fs] xfs: remove deprecated barrier/nobarrier mount (Brian Foster) [1633171]
- [fs] xfs: clean up IRELE/iput callsites (Brian Foster) [1633171]
- [fs] xfs: kill IHOLD (Brian Foster) [1633171]
- [fs] xfs: bypass final dfops roll in trans commit path (Brian Foster) [1633171]
- [fs] xfs: drop unnecessary xfs_defer_finish() dfops parameter (Brian Foster) [1633171]
- [fs] xfs: remove unnecessary dfops init calls in xattr code (Brian Foster) [1633171]
- [fs] xfs: remove all boilerplate defer init/finish code (Brian Foster) [1633171]
- [fs] xfs: use internal dfops during (b|c)ui recovery (Brian Foster) [1633171]
- [fs] xfs: use internal dfops in attr code (Brian Foster) [1633171]
- [fs] xfs: use internal dfops in cow blocks cancel (Brian Foster) [1633171]
- [fs] xfs: support embedded dfops in transaction (Brian Foster) [1633171]
- [fs] xfs: pack holes in xfs_defer_ops and xfs_trans (Brian Foster) [1633171]
- [fs] xfs: reset dfops to initial state after finish (Brian Foster) [1633171]
- [fs] xfs: remove unused deferred ops committed field (Brian Foster) [1633171]
- [fs] xfs: make deferred processing safe for embedded dfops (Brian Foster) [1633171]
- [fs] xfs: fix transaction leak on remote attr set/remove failure (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops in log recovery intent processing (Brian Foster) [1633171]
- [fs] xfs: pull up dfops from xfs_itruncate_extents() (Brian Foster) [1633171]
- [fs] xfs: force summary counter recalc at next mount (Brian Foster) [1633171]
- [fs] xfs: refactor unmount record write (Brian Foster) [1633171]
- [fs] xfs: detect and fix bad summary counts at mount (Brian Foster) [1633171]
- [fs] xfs: fix indentation and other whitespace problems in scrub/repair (Brian Foster) [1633171]
- [fs] xfs: shorten struct xfs_scrub_context to struct xfs_scrub (Brian Foster) [1633171]
- [fs] xfs: shorten xfs_repair_ prefix to xrep_ (Brian Foster) [1633171]
- [fs] xfs: shorten xfs_scrub_ prefix (Brian Foster) [1633171]
- [fs] xfs: clean up xfs_btree_del_cursor callers (Brian Foster) [1633171]
- [fs] xfs: trivial xfs_btree_del_cursor cleanups (Brian Foster) [1633171]
- [fs] xfs: return from _defer_finish with a clean transaction (Brian Foster) [1633171]
- [fs] xfs: check leaf attribute block freemap in verifier (Brian Foster) [1633171]
- [fs] libxfs: Fix a couple of sparse complaintis (Brian Foster) [1633171]
- [fs] xfs: use swap macro in xfs_dir2_leafn_rebalance (Brian Foster) [1633171]
- [fs] xfs_bmap_util: use swap macro (Brian Foster) [1633171]
- [fs] xfs_attr_leaf: use swap macro in xfs_attr3_leaf_rebalance (Brian Foster) [1633171]
- [fs] xfs: don't assume a left rmap when allocating a new rmap (Brian Foster) [1633171]
- [fs] xfs: kill __xfs_buf_submit_common() (Brian Foster) [1633171]
- [fs] xfs: combine (a)sync buffer submission apis (Brian Foster) [1633171]
- [fs] xfs: use sync buffer I/O for sync delwri queue submission (Brian Foster) [1633171]
- [fs] xfs: refactor buffer submission into a common helper (Brian Foster) [1633171]
- [fs] xfs: remove xfs_defer_init() firstblock param (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in inode inactivate (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in extent swap (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in reflink cow block cancel (Brian Foster) [1633171]
- [fs] xfs: replace no-op firstblock init with ->t_firstblock (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in dq alloc (Brian Foster) [1633171]
- [fs] xfs: remove xfs_alloc_arg firstblock field (Brian Foster) [1633171]
- [fs] xfs: remove xfs_btree_cur private firstblock field (Brian Foster) [1633171]
- [fs] xfs: remove bmap format helpers firstblock params (Brian Foster) [1633171]
- [fs] xfs: remove bmap extent add helper firstblock params (Brian Foster) [1633171]
- [fs] xfs: remove xfs_bmalloca firstblock field (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in bmap extent split (Brian Foster) [1633171]
- [fs] xfs: remove bmap insert/collapse firstblock param (Brian Foster) [1633171]
- [fs] xfs: remove xfs_bunmapi() firstblock param (Brian Foster) [1633171]
- [fs] xfs: remove xfs_bmapi_write() firstblock param (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in insert/collapse range (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in xfs_bmapi_remap() (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock for all xfs_bunmapi() callers (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock for all xfs_bmapi_write() callers (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in xattr ops (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in attrfork add (Brian Foster) [1633171]
- [fs] xfs: remove firstblock param from xfs dir ops (Brian Foster) [1633171]
- [fs] xfs: use ->t_firstblock in dir ops (Brian Foster) [1633171]
- [fs] xfs: add firstblock field to xfs_trans (Brian Foster) [1633171]
- [fs] xfs: allow null firstblock in xfs_bmapi_write() when tp is null (Brian Foster) [1633171]
- [fs] xfs: refactor dfops init to attach to transaction (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops in reflink cow recover path (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops in cancel cow blocks operation (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops for rmap extent swap operations (Brian Foster) [1633171]
- [fs] xfs: remove unused btree cursor bc_private.a.dfops field (Brian Foster) [1633171]
- [fs] xfs: remove xfs_btree_cur bmbt dfops field (Brian Foster) [1633171]
- [fs] xfs: remove dfops param from internal bmap extent helpers (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops for collapse/insert range operations (Brian Foster) [1633171]
- [fs] xfs: remove struct xfs_bmalloca dfops field (Brian Foster) [1633171]
- [fs] xfs: remove xfs_bmapi_remap() dfops param (Brian Foster) [1633171]
- [fs] xfs: remove xfs_bunmapi() dfops param (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops for all xfs_bunmapi() callers (Brian Foster) [1633171]
- [fs] xfs: remove xfs_bmapi_write() dfops param (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops for all xfs_bmapi_write() callers (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops in dqalloc transaction (Brian Foster) [1633171]
- [fs] xfs: replace xfs_da_args->dfops accesses with ->t_dfops and remove (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops in extent split tx and remove param (Brian Foster) [1633171]
- [fs] xfs: remove dfops param in attr fork add path (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops for attr set/remove operations (Brian Foster) [1633171]
- [fs] xfs: use ->t_dfops for recovery of (b|c)ui log items (Brian Foster) [1633171]
- [fs] xfs: remove dfops param from high level dirname calls (Brian Foster) [1633171]
- [fs] xfs: remove dfops parameter from ifree call stack (Brian Foster) [1633171]
- [fs] xfs: rename xfs_trans ->t_agfl_dfops to ->t_dfops (Brian Foster) [1633171]
- [fs] xfs: cow unwritten conversion uses uninitialized dfops (Brian Foster) [1633171]
- [fs] xfs: update my copyrights for the writeback and iomap code (Brian Foster) [1633171]
- [fs] xfs: add support for sub-pagesize writeback without buffer_heads (Brian Foster) [1633171]
- [fs] xfs: allow writeback on pages without buffer heads (Brian Foster) [1633171]
- [fs] xfs: refactor the tail of xfs_writepage_map (Brian Foster) [1633171]
- [fs] xfs: remove xfs_start_page_writeback (Brian Foster) [1633171]
- [fs] xfs: move all writeback buffer_head manipulation into xfs_map_at_offset (Brian Foster) [1633171]
- [fs] xfs: don't look at buffer heads in xfs_add_to_ioend (Brian Foster) [1633171]
- [fs] xfs: remove the imap_valid flag (Brian Foster) [1633171]
- [fs] xfs: simplify xfs_map_blocks by using xfs_iext_lookup_extent directly (Brian Foster) [1633171]
- [fs] xfs: remove xfs_reflink_find_cow_mapping (Brian Foster) [1633171]
- [fs] xfs: remove the now unused XFS_BMAPI_IGSTATE flag (Brian Foster) [1633171]
- [fs] xfs: make xfs_writepage_map extent map centric (Brian Foster) [1633171]
- [fs] xfs: rename the offset variable in xfs_writepage_map (Brian Foster) [1633171]
- [fs] xfs: remove xfs_map_cow (Brian Foster) [1633171]
- [fs] xfs: remove xfs_reflink_trim_irec_to_next_cow (Brian Foster) [1633171]
- [fs] xfs: don't use XFS_BMAPI_IGSTATE in xfs_map_blocks (Brian Foster) [1633171]
- [fs] xfs: don't clear imap_valid for a non-uptodate buffers (Brian Foster) [1633171]
- [fs] xfs: do not set the page uptodate in xfs_writepage_map (Brian Foster) [1633171]
- [fs] xfs: move locking into xfs_bmap_punch_delalloc_range (Brian Foster) [1633171]
- [fs] xfs: simplify xfs_aops_discard_page (Brian Foster) [1633171]
- [fs] xfs: use iomap for blocksize == PAGE_SIZE readpage and readpages (Brian Foster) [1633171]
- [fs] iomap: fix WARN_ON_ONCE on uninitialized variable (Brian Foster) [1633171]
- [fs] iomap: Switch to offset_in_page for clarity (Brian Foster) [1633171]
- [fs] iomap: add support for sub-pagesize buffered I/O without buffer heads (Brian Foster) [1633171]
- [fs] iomap: add inline data support to iomap_readpage_actor (Brian Foster) [1633171]
- [fs] iomap: support direct I/O to inline data (Brian Foster) [1633171]
- [fs] iomap: refactor iomap_dio_actor (Brian Foster) [1633171]
- [fs] iomap: add initial support for writes without buffer heads (Brian Foster) [1633171]
- [fs] iomap: add an iomap-based readpage and readpages implementation (Brian Foster) [1633171]
- [fs] iomap: add private pointer to struct iomap (Brian Foster) [1633171]
- [fs] iomap: add a page_done callback (Brian Foster) [1633171]
- [fs] iomap: generic inline data handling (Brian Foster) [1633171]
- [fs] iomap: complete partial direct I/O writes synchronously (Brian Foster) [1633171]
- [fs] iomap: mark newly allocated buffer heads as new (Brian Foster) [1633171]
- [fs] fs: factor out a __generic_write_end helper (Brian Foster) [1633171]
- [netdrv] amd-xgbe: mark driver as tech preview (David Arcari) [1633209]
- [fs] ext4, dax: set ext4_dax_aops for dax files (Lukas Czerner) [1633239]
- [fs] ext4, dax: add ext4_bmap to ext4_dax_aops (Lukas Czerner) [1633239]
- [fs] ext4: don't mark mmp buffer head dirty (Lukas Czerner) [1633239]
- [fs] ext4: show test_dummy_encryption mount option in /proc/mounts (Lukas Czerner) [1633239]
- [fs] ext4: fix online resizing for bigalloc file systems with a 1k block size (Lukas Czerner) [1633239]
- [fs] ext4: fix online resize's handling of a too-small final block group (Lukas Czerner) [1633239]
- [fs] ext4: recalucate superblock checksum after updating free blocks/inodes (Lukas Czerner) [1633239]
- [fs] ext4: avoid arithemetic overflow that can trigger a BUG (Lukas Czerner) [1633239]
- [fs] ext4: avoid divide by zero fault when deleting corrupted inline directories (Lukas Czerner) [1633239]
- [fs] ext4: check to make sure the rename(2)'s destination is not freed (Lukas Czerner) [1633239]
- [fs] ext4: remove unneeded variable "err" in ext4_mb_release_inode_pa() (Lukas Czerner) [1633239]
- [fs] ext4: fix spectre gadget in ext4_mb_regular_allocator() (Lukas Czerner) [1633239]
- [fs] ext4: check for NUL characters in extended attribute's name (Lukas Czerner) [1633239]
- [fs] ext4: use ext4_warning() for sb_getblk failure (Lukas Czerner) [1633239]
- [fs] ext4: fix race when setting the bitmap corrupted flag (Lukas Czerner) [1633239]
- [fs] ext4: reset error code in ext4_find_entry in fallback (Lukas Czerner) [1633239]
- [fs] ext4: check allocation failure when duplicating "data" in ext4_remount() (Lukas Czerner) [1633239]
- [fs] ext4: sysfs: print ext4_super_block fields as little-endian (Lukas Czerner) [1633239]
- [firmware] efi/x86: Handle page faults occurring while running EFI runtime services (Bhupesh Sharma) [1627557]
- [firmware] efi: Make efi_rts_work accessible to efi page fault handler (Bhupesh Sharma) [1627557]
- [firmware] efi: Remove the declaration of efi_late_init() as the function is unused (Bhupesh Sharma) [1627557]
- [firmware] efi: Use a work queue to invoke EFI Runtime Services (Bhupesh Sharma) [1627557]
- [firmware] efi/x86: Use non-blocking SetVariable() for efi_delete_dummy_variable() (Bhupesh Sharma) [1627557]
- [fs] gfs2: Special-case rindex for gfs2_grow (Robert S Peterson) [1628360]
- [fs] GFS2: Fix recovery issues for spectators (Robert S Peterson) [1628298]

* Fri Oct 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-22.el8]
- [powerpc] powerpc/pkeys: Fix reading of ibm, processor-storage-keys property (Steve Best) [1633551]
- [powerpc] powerpc/pseries: Remove unneeded uses of dlpar work queue (Steve Best) [1633544]
- [powerpc] powerpc/pseries: Remove prrn_work workqueue (Steve Best) [1633544]
- [pci] ACPI / hotplug / PCI: Don't scan for non-hotplug bridges if slot is not bridge (Myron Stowe) [1634816]
- [pci] PCI: Fix enabling of PASID on RC integrated endpoints (Myron Stowe) [1634816]
- [pci] IB/hfi1,PCI: Allow bus reset while probing (Myron Stowe) [1634816]
- [pci] PCI: Fix faulty logic in pci_reset_bus() (Myron Stowe) [1634816]
- [pci] PCI: pciehp: Fix hot-add vs powerfault detection order (Myron Stowe) [1634816]
- [pci] Revert "PCI: Add ACS quirk for Intel 300 series" (Myron Stowe) [1634816]
- [powerpc] powerpc/numa: Use associativity if VPHN hcall is successful (Steve Best) [1633569]
- [pci] PCI: vmd: White list for fast interrupt handlers (Myron Stowe) [1632816]
- [pci] PCI: Add function 1 DMA alias quirk for Marvell 88SS9183 (Myron Stowe) [1632816]
- [pci] PCI: Rename pci_try_reset_bus() to pci_reset_bus() (Myron Stowe) [1632816]
- [pci] PCI: Deprecate pci_reset_bus() and pci_reset_slot() functions (Myron Stowe) [1632816]
- [pci] PCI: Unify try slot and bus reset API (Myron Stowe) [1632816]
- [pci] PCI: Hide pci_reset_bridge_secondary_bus() from drivers (Myron Stowe) [1632816]
- [pci] IB/hfi1: Use pci_try_reset_bus() for initiating PCI Secondary Bus Reset (Myron Stowe) [1632816]
- [pci] PCI: Handle error return from pci_reset_bridge_secondary_bus() (Myron Stowe) [1632816]
- [pci] PCI/IOV: Tidy pci_sriov_set_totalvfs() (Myron Stowe) [1632816]
- [pci] PCI: Enable PASID only if entire path supports End-End TLP prefixes (Myron Stowe) [1632816]
- [pci] PCI: Expand documentation for pci_add_dma_alias() (Myron Stowe) [1632816]
- [pci] PCI: Add DMA alias quirk for Microsemi Switchtec NTB (Myron Stowe) [1632816]
- [pci] switchtec: Use generic PCI Vendor ID and Class Code (Myron Stowe) [1632816]
- [pci] PCI: Make pci_get_rom_size() static (Myron Stowe) [1632816]
- [pci] PCI: Add check code for last image indicator not set (Myron Stowe) [1632816]
- [pci] PCI: Avoid accessing memory outside the ROM BAR (Myron Stowe) [1632816]
- [pci] PCI: Make early dump functionality generic (Myron Stowe) [1632816]
- [pci] PCI: Cleanup PCI_REBAR_CTRL_BAR_SHIFT handling (Myron Stowe) [1632816]
- [pci] PCI: Restore resized BAR state on resume (Myron Stowe) [1632816]
- [pci] PCI: Clean up resource allocation in devm_of_pci_get_host_bridge_resources() (Myron Stowe) [1632816]
- [pci] PCI: Add ACS Redirect disable quirk for Intel Sunrise Point (Myron Stowe) [1632816]
- [pci] PCI: Add device-specific ACS Redirect disable infrastructure (Myron Stowe) [1632816]
- [pci] PCI: Convert device-specific ACS quirks from NULL termination to ARRAY_SIZE (Myron Stowe) [1632816]
- [pci] PCI: Add "pci=disable_acs_redir=" parameter for peer-to-peer support (Myron Stowe) [1632816]
- [pci] PCI: Allow specifying devices using a base bus and path of devfns (Myron Stowe) [1632816]
- [pci] PCI: Make specifying PCI devices in kernel parameters reusable (Myron Stowe) [1632816]
- [pci] PCI: Hide ACS quirk declarations inside PCI core (Myron Stowe) [1632816]
- [pci] PCI: Document ACPI description of PCI host bridges (Myron Stowe) [1632816]
- [pci] PCI/MSI: Set IRQCHIP_ONESHOT_SAFE for PCI-MSI irqchips (Myron Stowe) [1632816]
- [pci] PCI: Limit config space size for Netronome NFP5000 (Myron Stowe) [1632816]
- [pci] PCI: Add PCI_DEVICE_DATA() macro to fully describe device ID entry (Myron Stowe) [1632816]
- [pci] PCI: Unify PCI and normal DMA direction definitions (Myron Stowe) [1632816]
- [pci] PCI: Use IRQF_ONESHOT if pci_request_irq() called with no handler (Myron Stowe) [1632816]
- [pci] PCI: Call dma_debug_add_bus() for pci_bus_type from PCI core (Myron Stowe) [1632816]
- [pci] PCI: Mark fall-through switch cases before enabling -Wimplicit-fallthrough (Myron Stowe) [1632816]

* Thu Oct 04 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-21.el8]
- [s390] s390/sclp: Allow to request adapter reset (Philipp Rudo) [1635273]
- [char] ipmi: Fix NULL pointer dereference in ssif_probe (Tony Camuso) [1635366]
- [char] ipmi: Fix I2C client removal in the SSIF driver (Tony Camuso) [1635366]
- [char] ipmi: kcs_bmc: don't change device name (Tony Camuso) [1635366]
- [kernel] timers: Clear timer_base::must_forward_clk with timer_base::lock held (Waiman Long) [1632820]
- [pci] switchtec: Fix Spectre v1 vulnerability (Waiman Long) [1632820]
- [kernel] cpu/hotplug: Prevent state corruption on error rollback (Waiman Long) [1632820]
- [kernel] cpu/hotplug: Adjust misplaced smb() in cpuhp_thread_fun() (Waiman Long) [1632820]
- [base] memory_hotplug: fix kernel_panic on offline page processing (Waiman Long) [1632820]
- [mm] mm/hugetlb: filter out hugetlb pages if HUGEPAGE migration is not supported (Waiman Long) [1632820]
- [lib] debugobjects: Make stack check warning more informative (Waiman Long) [1632820]
- [fs] fs/dcache.c: fix kmemcheck splat at take_dentry_name_snapshot() (Waiman Long) [1632820]
- [x86] x86/process: Don't mix user/kernel regs in 64bit __show_regs() (Waiman Long) [1632820]
- [x86] x86/dumpstack: Don't dump kernel memory based on usermode RIP (Waiman Long) [1632820]
- [x86] x86: Avoid pr_cont() in show_opcodes() (Waiman Long) [1632820]
- [x86] x86/entry/64: Wipe KASAN stack shadow before rewind_stack_do_exit() (Waiman Long) [1632820]
- [x86] x86/speculation/l1tf: Increase l1tf memory limit for Nehalem+ (Waiman Long) [1632820]
- [x86] x86/spectre: Add missing family 6 check to microcode check (Waiman Long) [1632820]
- [x86] x86/nmi: Fix NMI uaccess race against CR3 switching (Waiman Long) [1632820]
- [x86] x86/vdso: Fix lsl operand order (Waiman Long) [1632820]
- [x86] x86/vdso: Fix vDSO build if a retpoline is emitted (Waiman Long) [1632820]
- [x86] x86/speculation/l1tf: Suggest what to do on systems with too much RAM (Waiman Long) [1632820]
- [x86] x86/speculation/l1tf: Fix off-by-one error when warning that system has too much RAM (Waiman Long) [1632820]
- [x86] x86/speculation/l1tf: Fix overflow in l1tf_pfn_limit() on 32bit (Waiman Long) [1632820]
- [x86] x86/speculation/l1tf: Exempt zeroed PTEs from inversion (Waiman Long) [1632820]
- [x86] x86/mm/pti: Clear Global bit more aggressively (Waiman Long) [1632820]
- [x86] x86/paravirt: Fix spectre-v2 mitigations for paravirt guests (Waiman Long) [1632820]
- [target] scsi: target: iscsi: Use bin2hex instead of a re-implementation (Maurizio Lombardi) [1632184] {CVE-2018-14633}
- [target] scsi: target: iscsi: Use hex2bin instead of a re-implementation (Maurizio Lombardi) [1632184] {CVE-2018-14633}

* Wed Oct 03 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-20.el8]
- [netdrv] ibmvnic: Include missing return code checks in reset function (Steve Best) [1633553]
- [netdrv] ibmvnic: Update firmware error reporting with cause string (Steve Best) [1633553]
- [netdrv] ibmvnic: Remove code to request error information (Steve Best) [1633553]
- [s390] s390/qeth: remove duplicated carrier state tracking (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: clean up drop conditions for received cmds (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: re-indent qeth_check_ipa_data() (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: consume local address events (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove various redundant code (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove CARD_FROM_CDEV helper (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: pass card pointer in iob callback (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: re-use qeth_notify_skbs() (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove additional skb refcount (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: replace open-coded skb_queue_walk() (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: on gdev release, reset drvdata (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: fix discipline unload after setup error (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: use DEFINE_MUTEX for qeth_mod_mutex (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: convert layer attribute to enum (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: reduce 0-initializing when building IPA cmds (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: fine-tune spinlocks (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: fix typo in return value (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: invoke softirqs after napi_schedule() (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: uninstall IRQ handler on device removal (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove qeth_hdr_chk_and_bounce() (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: speed up TSO transmission (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: prepare for copy-free TSO transmission (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: check size of required HW header cache object (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: fix up protocol headers early (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: limit csum offload erratum to L3 devices (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove qeth_get_elements_no() (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove unused L3 xmit code (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: run non-offload L3 traffic over common xmit path (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: move L2 xmit code to core module (Hendrik Brueckner) [1633841]
- [s390] s390/qdio: reset old sbal_state flags (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: don't dump past end of unknown HW header (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: use vzalloc for QUERY OAT buffer (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: switch on SG by default for IQD devices (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: indicate error when netdev allocation fails (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: use true and false for boolean values (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: don't restrict qeth_card to DMA memory (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: clean up card initialization (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: do basic setup for data channel (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: use qeth_setup_ccw() to set up all CCWs (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: reduce hard-coded access to ccw channels (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: extract helper for MPC protocol type (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: speed up L2 IQD xmit (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: add support for constrained HW headers (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: merge linearize-check into HW header construction (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: add statistics for consumed buffer elements (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: use core MTU range checking (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: simplify max MTU handling (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: don't cache HW port number (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: allocate netdevice early (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove redundant netif_carrier_ok() checks (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: reset layer2 attribute on layer switch (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: fix race in used-buffer accounting (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: speed-up IPv4 OSA xmit (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: speed-up L3 IQD xmit (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: add a L3 xmit wrapper (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: increase GSO max size for eligible L3 devices (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: clean up exported symbols (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: consolidate ccwgroup driver definition (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: clean up Output Queue selection (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: fine-tune RX modesetting (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: remove unused buffer->aob pointer (Hendrik Brueckner) [1633841]
- [s390] s390/qeth: various buffer management cleanups (Hendrik Brueckner) [1633841]
- [powerpc] powerpc: Avoid code patching freed init sections (Steve Best) [1633545]
- [powerpc] powerpc/tm: Fix userspace r13 corruption (Steve Best) [1633543]
- [powerpc] powerpc/tm: Avoid possible userspace r1 corruption on reclaim (Steve Best) [1633543]
- [drm] drm/i915/cfl: Add a new CFL PCI ID (Rob Clark) [1626883]
- [drm] drm/i915/aml: Introducing Amber Lake platform (Rob Clark) [1626883]
- [drm] drm/i915/whl: Introducing Whiskey Lake platform (Rob Clark) [1626883]
- [char] ipmi: Move BT capabilities detection to the detect call (Frank Ramsay) [1618774]
- [char] ipmi: Rework SMI registration failure (Frank Ramsay) [1618774]

* Tue Oct 02 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-19.el8]
- [s390] s390: detect etoken facility (Thomas Huth) [1634069]
- [s390] s390/lib: use expoline for all bcr instructions (Thomas Huth) [1634069]
- [documentation] vm.txt: Adding 'nr_hugepages_mempolicy' parameter description (Prashant Dhamdhere) [1626547]

* Mon Oct 01 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-18.el8]
- [scsi] scsi: ipr: System hung while dlpar adding primary ipr adapter back (Steve Best) [1633217]
- [target] scsi: iscsi: target: Don't use stack buffer for scatterlist (Maurizio Lombardi) [1631342]
- [rpmspec] Forward port weak-modules support from RHEL 7 to RHEL 8 ("Herton R. Krzesinski") [1596884]
- [fs] xfs: Close race between direct IO and xfs_break_layouts() (Eric Sandeen) [1622191]
- [fs] xfs: remove unused iolock arg from xfs_break_dax_layouts (Eric Sandeen) [1622191]
- [fs] ext4: Close race between direct IO and ext4_break_layouts() (Eric Sandeen) [1616303]
- [fs] ext4: handle layout changes to pinned DAX mappings (Eric Sandeen) [1614154]
- [fs] dax: dax_layout_busy_page() warn on !exceptional (Eric Sandeen) [1614154]
- [fs] dax: mark tech preview (Eric Sandeen) [1627455]
- [mm] usercopy: Allow boot cmdline disabling of hardening (Christoph von Recklinghausen) [1589928]

* Thu Sep 27 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-17.el8]
- [s390] s390/crypto: Fix return code checking in cbc_paes_crypt() (Philipp Rudo) [1633266]
- [drm] amd/display/dc/basics/logger.c: fix build error with CONFIG_FORTIFY_SOURCE=y ("Herton R. Krzesinski") [1548068]
- [acpi] ACPICA: AML Parser: skip opcodes that open a scope upon parse failure (Jeremy Linton) [1609885]
- [acpi] ACPICA: ACPICA: add status check for acpi_hw_read before assigning return value (Jeremy Linton) [1609885]
- [acpi] ACPICA: AML Parser: ignore all exceptions resulting from incorrect AML during table load (Jeremy Linton) [1609885]
- [rpmspec] spec: Add missing BuildRequires for bpftool (Jiri Olsa) [1632756]
- [powerpc] KVM: PPC: Avoid marking DMA-mapped pages dirty in real mode (David Gibson) [1628412]
- [powerpc] powerpc/powernv/ioda: Allocate indirect TCE levels on demand (David Gibson) [1628412]
- [powerpc] powerpc/powernv: Rework TCE level allocation (David Gibson) [1628412]
- [powerpc] powerpc/powernv: Add indirect levels to it_userspace (David Gibson) [1628412]
- [powerpc] KVM: PPC: Make iommu_table::it_userspace big endian (David Gibson) [1628412]
- [powerpc] powerpc/powernv: Move TCE manupulation code to its own file (David Gibson) [1628412]
- [net] net_sched: fix NULL pointer dereference when delete tcindex filter (Andrea Claudi) [1627648]
- [net] net_sched: Fix missing res info when create new tc_index filter (Andrea Claudi) [1627648]
- [samples] samples/bpf: xdpsock: order memory on AArch64 (Jesper Brouer) [1615959]
- [samples] samples/bpf: xdp_redirect_cpu load balance like Suricata (Jesper Brouer) [1615959]
- [samples] samples/bpf: add Paul Hsieh's (LGPL 2.1) hash function SuperFastHash (Jesper Brouer) [1615959]
- [samples] samples/bpf: xdp_redirect_cpu handle parsing of double VLAN tagged packets (Jesper Brouer) [1615959]
- [samples] samples/bpf: all XDP samples should unload xdp/bpf prog on SIGTERM (Jesper Brouer) [1615959]
- [samples] samples/bpf: xdp_rxq_info action XDP_TX must adjust MAC-addrs (Jesper Brouer) [1615959]
- [samples] samples/bpf: extend xdp_rxq_info to read packet payload (Jesper Brouer) [1615959]
- [powerpc] KVM: PPC: Book3S HV: Use correct pagesize in kvm_unmap_radix() (David Gibson) [1625498]
- [net] igmp: fix incorrect unsolicit report count after link down and up (Hangbin Liu) [1625538]
- [net] igmp: fix incorrect unsolicit report count when join group (Hangbin Liu) [1625538]
- [netdrv] cxgb4: update 1.20.8.0 as the latest firmware supported (Arjun Vynipadath) [1622555]
- [virt] svm: nested virt support off by default (Bandan Das) [1571993]

* Wed Sep 26 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-16.el8]
- [powerpc] KVM: PPC: Book3S HV: Don't use compound_order to determine host mapping size (David Gibson) [1625860]
- [virt] arm64: KVM: Remove pgd_lock (Wei Huang) [1627474]
- [virt] KVM: Remove obsolete kvm_unmap_hva notifier backend (Wei Huang) [1627474]
- [virt] arm64: KVM: Only force FPEXC32_EL2.EN if trapping FPSIMD (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Clean dcache to PoC when changing PTE due to CoW (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Skip updating PTE entry if no change (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Skip updating PMD entry if no change (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Move DEBUG_SPINLOCK_BUG_ON to vgic.h (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Do not use spin_lock_irqsave/restore with irq disabled (Wei Huang) [1627474]
- [virt] KVM: arm: vgic-v3: Add support for ICC_SGI0R and ICC_ASGI1R accesses (Wei Huang) [1627474]
- [virt] KVM: arm64: vgic-v3: Add support for ICC_SGI0R_EL1 and ICC_ASGI1R_EL1 accesses (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic-v3: Add core support for Group0 SGIs (Wei Huang) [1627474]
- [virt] KVM: arm64: Remove non-existent AArch32 ICC_SGI1R encoding (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Fix lost IRQs from emulated physcial timer when blocked (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Fix potential loss of ptimer interrupts (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Fix possible spectre-v1 write in vgic_mmio_write_apr() (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Update documentation of the GIC devices wrt IIDR (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Let userspace opt-in to writable v2 IGROUPR (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Allow configuration of interrupt groups (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Return error on incompatible uaccess GICD_IIDR writes (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Permit uaccess writes to return errors (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Signal IRQs using their configured group (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Add group field to struct irq (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: GICv2 IGROUPR should read as zero (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Keep track of implementation revision (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic: Define GICD_IIDR fields for GICv2 and GIv3 (Wei Huang) [1627474]
- [virt] arm64: KVM: Cleanup tpidr_el2 init on non-VHE (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: vgic-debug: Show LPI status (Wei Huang) [1627474]
- [virt] KVM: arm64: vgic-its: Remove VLA usage (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Fix vgic init race (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Enable adaptative WFE trapping (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Remove unnecessary CMOs when creating HYP page tables (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Stop using the kernel's (pmd, pud, pgd)_populate helpers (Wei Huang) [1627474]
- [virt] KVM: arm/arm64: Consolidate page-table accessors (Wei Huang) [1627474]
- [virt] arm64: KVM: Avoid marking pages as XN in Stage-2 if CTR_EL0.DIC is set (Wei Huang) [1627474]
- [tools] radix tree test suite: Enable ubsan (Waiman Long) [1630244]
- [tools] radix tree test suite: Fix compilation (Waiman Long) [1630244]
- [block] blk-wbt: don't maintain inflight counts if disabled (Ming Lei) [1622790]
- [block] blk-wbt: fix has-sleeper queueing check (Ming Lei) [1622790]
- [block] blk-wbt: use wq_has_sleeper() for wq active check (Ming Lei) [1622790]
- [block] blk-wbt: move disable check into get_limit() (Ming Lei) [1622790]
- [block] block/DAC960.c: make some arrays static const, shrinks object (Ming Lei) [1622790]
- [block] blk-mq: sync the update nr_hw_queues with (Ming Lei) [1617959]
- [block] blk-mq: init hctx sched after update ctx and hctx mapping (Ming Lei) [1617959]
- [block] block: remove duplicate initialization (Ming Lei) [1622790]
- [block] tracing/blktrace: Fix to allow setting same value (Ming Lei) [1622790]
- [block] pktcdvd: fix setting of 'ret' error return for a few cases (Ming Lei) [1622790]
- [block] block: change return type to bool (Ming Lei) [1622790]
- [block] block, bfq: return nbytes and not zero from struct cftype (Ming Lei) [1622790]
- [block] block, bfq: improve code of bfq_bfqq_charge_time (Ming Lei) [1622790]
- [block] block, bfq: reduce write overcharge (Ming Lei) [1622790]
- [block] block, bfq: always update the budget of an entity when needed (Ming Lei) [1622790]
- [block] block, bfq: readd missing reset of parent-entity service (Ming Lei) [1622790]
- [block] block: don't warn for flush on read-only device (Ming Lei) [1622809]

* Tue Sep 25 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-15.el8]
- [kernel] locking/rwsem: Make owner store task pointer of last owning reader (Waiman Long) [1631842]
- [kernel] locking/rwsem: Exit read lock slowpath if queue empty & no writer (Waiman Long) [1631842]
- [x86] x86/microcode: Update the new microcode revision unconditionally (Prarit Bhargava) [1630931]
- [x86] x86/microcode: Make sure boot_cpu_data.microcode is up-to-date (Prarit Bhargava) [1630931]
- [arm64] arm64: tlb: Provide forward declaration of tlb_flush() before including tlb.h (Waiman Long) [1630521]
- [x86] x86/mm: Only use tlb_remove_table() for paravirt (Waiman Long) [1630521]
- [mm] mm: mmu_notifier fix for tlb_end_vma (Waiman Long) [1630521]
- [mm] mm/tlb, x86/mm: Support invalidating TLB caches for RCU_TABLE_FREE (Waiman Long) [1630521]
- [mm] mm/tlb: Remove tlb_remove_table() non-concurrent condition (Waiman Long) [1630521]
- [mm] mm: move tlb_table_flush to tlb_flush_mmu_free (Waiman Long) [1630521]
- [kernel] clocksource: Revert Remove kthread (Waiman Long) [1628402]
- [cpuidle] cpuidle: menu: Retain tick when shallow state is selected (Waiman Long) [1628402]
- [cpufreq] cpufreq: governor: Avoid accessing invalid governor_data (Waiman Long) [1628402]
- [cpuidle] cpuidle: menu: Handle stopped tick more aggressively (Waiman Long) [1628402]
- [kernel] sched: idle: Avoid retaining the tick when it has been stopped (Waiman Long) [1628402]
- [net] netfilter: xt_hashlimit: do not crash when reading proc file (Florian Westphal) [1630131]
- [x86] x86/boot/KASLR: Skip specified number of 1GB huge pages when doing physical randomization (KASLR) (Baoquan He) [1564824]
- [x86] x86/boot/KASLR: Add two new functions for 1GB huge pages handling (Baoquan He) [1564824]
- [mfd] mfd: intel-lpss: Add Ice Lake PCI IDs (Gopal Tiwari) [1483477]
- [mmc] mmc: sdhci-pci: Add support for Intel ICP (Gopal Tiwari) [1483496]

* Mon Sep 24 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-14.el8]
- [mm] mm: get rid of vmacache_flush_all() entirely (Waiman Long) [1631297] {CVE-2018-17182}
- [mm] mm, vmacache: hash addresses based on pmd (Waiman Long) [1631297] {CVE-2018-17182}
- [mm] mm: Allocate the mm_cpumask (mm->cpu_bitmap) dynamically based on nr_cpu_ids (Waiman Long) [1631297] {CVE-2018-17182}
- [infiniband] IB/hfi1: Invalid NUMA node information can cause a divide by zero (Alex Estrin) [1622222]
- [nvdimm] libnvdimm: Export max available extent (Jeff Moyer) [1627874]
- [nvdimm] libnvdimm: Use max contiguous area for namespace size (Jeff Moyer) [1627874]
- [netdrv] ice: Fix and update driver version string (Jonathan Toppins) [1611786]
- [netdrv] ice: Introduce SERVICE_DIS flag and service routine functions (Jonathan Toppins) [1611786]
- [netdrv] ice: Enable VSI Rx/Tx pruning only when VLAN 0 is active (Jonathan Toppins) [1611786]
- [netdrv] ice: Enable firmware logging during device initialization (Jonathan Toppins) [1611786]
- [netdrv] ice: Implement ice_bridge_getlink and ice_bridge_setlink (Jonathan Toppins) [1611786]
- [netdrv] ice: Add support for Tx hang, Tx timeout and malicious driver detection (Jonathan Toppins) [1611786]
- [netdrv] ice: Clean up register file (Jonathan Toppins) [1611786]
- [netdrv] ice: Implement handlers for ethtool PHY/link operations (Jonathan Toppins) [1611786]
- [netdrv] ice: Refactor VSI allocation, deletion and rebuild flow (Jonathan Toppins) [1611786]
- [netdrv] ice: Refactor switch rule management structures and functions (Jonathan Toppins) [1611786]
- [netdrv] ice: Code optimization for ice_fill_sw_rule() (Jonathan Toppins) [1611786]
- [netdrv] ice: Prevent control queue operations during reset (Jonathan Toppins) [1611786]
- [netdrv] ice: Update request resource command to latest specification (Jonathan Toppins) [1611786]
- [netdrv] ice: Updates to Tx scheduler code (Jonathan Toppins) [1611786]
- [netdrv] ice: Rework flex descriptor programming (Jonathan Toppins) [1611786]
- [netdrv] net/mlx5: Fix SQ offset in QPs with small RQ (Alaa Hleihel) [1623367]
- [x86] x86/spec_ctrl: Make IBRS code work with SSBD mitigation (Waiman Long) [1565180]
- [x86] x86/spec_ctrl: Auto-enable IBRS on Skylake (Waiman Long) [1565180]
- [x86] x86/spec_ctrl: Extend spectre_v2 boot option to support IBRS (Waiman Long) [1565180]
- [x86] x86/spec_ctrl: Boot time IBRS initialization (Waiman Long) [1565180]
- [x86] x86/spec_ctrl: Add IBRS code to the 64-bit assembly entry code (Waiman Long) [1565180]
- [x86] x86/cpufeatures: Increase NCAPINTS for future extension (Waiman Long) [1565180]
- [netdrv] ice: Trivial formatting fixes (Jonathan Toppins) [1611783]
- [netdrv] ice: Change struct members from bool to u8 (Jonathan Toppins) [1611783]
- [netdrv] ice: Fix potential return of uninitialized value (Jonathan Toppins) [1611783]
- [netdrv] ice: Fix a few null pointer dereference issues (Jonathan Toppins) [1611783]
- [netdrv] ice: Update to interrupts enabled in OICR (Jonathan Toppins) [1611783]
- [netdrv] ice: Set VLAN flags correctly (Jonathan Toppins) [1611783]
- [netdrv] ice: Use order_base_2 to calculate higher power of 2 (Jonathan Toppins) [1611783]
- [netdrv] ice: Fix bugs in control queue processing (Jonathan Toppins) [1611783]
- [netdrv] ice: Clean control queues only when they are initialized (Jonathan Toppins) [1611783]
- [netdrv] ice: Report stats for allocated queues via ethtool stats (Jonathan Toppins) [1611783]
- [netdrv] ice: Cleanup magic number (Jonathan Toppins) [1611783]
- [netdrv] ice: Remove unnecessary node owner check (Jonathan Toppins) [1611783]
- [netdrv] ice: Fix multiple static analyser warnings (Jonathan Toppins) [1611783]
- [virt] KVM: VMX: fixes for vmentry_l1d_flush module parameter (Waiman Long) [1616248] {CVE-2018-15572}
- [virt] KVM: x86: SVM: Call x86_spec_ctrl_set_guest/host() with interrupts disabled (Waiman Long) [1616248] {CVE-2018-15572}
- [virt] x86/kvm/vmx: Fix coding style in vmx_setup_l1d_flush() (Waiman Long) [1616248] {CVE-2018-15572}
- [x86] x86/speculation: Support Enhanced IBRS on future CPUs (Waiman Long) [1614144]
- [x86] x86/speculation: Protect against userspace-userspace spectreRSB (Waiman Long) [1616248] {CVE-2018-15572}
- [x86] x86/speculation: Remove SPECTRE_V2_IBRS in enum spectre_v2_mitigation (Waiman Long) [1616248] {CVE-2018-15572}
- [cpufreq] cpufreq: Fix a circular lock dependency problem (Waiman Long) [1599154]
- [kernel] cpu/hotplug: Add a cpus_read_trylock() function (Waiman Long) [1599154]
- [virt] xen/spinlock: Don't use pvqspinlock if only 1 vCPU (Waiman Long) [1618486]

* Thu Sep 20 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-13.el8]
- [mailbox] mailbox: PCC: handle parse error (David Arcari) [1630382]
- [hv] vmbus: don't return values for uninitalized channels (Vitaly Kuznetsov) [1617954]
- [mm] kernel/memremap, kasan: make ZONE_DEVICE with work with KASAN (Bill O'Donnell) [1629578]
- [mm] mm: fix BUG_ON() in vmf_insert_pfn_pud() from VM_MIXEDMAP removal (Jeff Moyer) [1622171]
- [mm] dax: remove VM_MIXEDMAP for fsdax and device dax (Jeff Moyer) [1622171]

* Wed Sep 19 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-12.el8]
- [i2c] i2c: i801: fix DNV's SMBCTRL register offset (David Arcari) [1628861]
- [fs] ceph: avoid a use-after-free in ceph_destroy_options() (Ilya Dryomov) [1629884]
- [fs] ceph: fix incorrect use of strncpy (Ilya Dryomov) [1629884]
- [block] rbd: support cloning across namespaces (Ilya Dryomov) [1629884]
- [block] rbd: factor out get_parent_info() (Ilya Dryomov) [1629884]
- [block] rbd: support for images within namespaces (Ilya Dryomov) [1629884]
- [block] rbd: pass rbd_spec into parse_rbd_opts_token() (Ilya Dryomov) [1629884]
- [net] libceph: weaken sizeof check in ceph_x_verify_authorizer_reply() (Ilya Dryomov) [1629884]
- [net] libceph: check authorizer reply/challenge length before reading (Ilya Dryomov) [1629884]
- [net] libceph: implement CEPHX_V2 calculation mode (Ilya Dryomov) [1629884]
- [net] libceph: add authorizer challenge (Ilya Dryomov) [1629884]
- [net] libceph: factor out encrypt_authorizer() (Ilya Dryomov) [1629884]
- [net] libceph: factor out __ceph_x_decrypt() (Ilya Dryomov) [1629884]
- [net] libceph: factor out __prepare_write_connect() (Ilya Dryomov) [1629884]
- [net] libceph: store ceph_auth_handshake pointer in ceph_connection (Ilya Dryomov) [1629884]
- [pci] PCI: pciehp: Deduplicate presence check on probe & resume (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Avoid implicit fallthroughs in switch statements (Myron Stowe) [1583983]
- [pci] PCI: Whitelist Thunderbolt ports for runtime D3 (Myron Stowe) [1583983]
- [pci] PCI: Whitelist native hotplug ports for runtime D3 (Myron Stowe) [1583983]
- [pci] PCI: sysfs: Resume to D0 on function reset (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Resume parent to D0 on config space access (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Resume to D0 on enable/disable (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Support interrupts sent from D3hot (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Obey compulsory command delay after resume (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Clear spurious events earlier on resume (Myron Stowe) [1583983]
- [pci] PCI: portdrv: Deduplicate PM callback iterator (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Avoid slot access during reset (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Always enable occupied slot on probe (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Become resilient to missed events (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Tolerate initially unstable link (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Declare pciehp_enable/disable_slot() static (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Drop enable/disable lock (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Enable/disable exclusively from IRQ thread (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Track enable/disable status (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Publish to user space last on probe (Myron Stowe) [1583983]
- [pci] PCI: hotplug: Demidlayer registration with the core (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Drop slot workqueue (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Handle events synchronously (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Stop blinking on slot enable failure (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Convert to threaded polling (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Convert to threaded IRQ (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Document struct slot and struct controller (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Declare pciehp_unconfigure_device() void (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Drop unnecessary NULL pointer check (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Fix unprotected list iteration in IRQ handler (Myron Stowe) [1583983]
- [pci] PCI: pciehp: Fix use-after-free on unplug (Myron Stowe) [1583983]
- [pci] PCI: hotplug: Don't leak pci_slot on registration failure (Myron Stowe) [1583983]
- [pci] PCI: hotplug: Delete skeleton driver (Myron Stowe) [1583983]
- [netdrv] be2net: Use Kconfig flag to support for enabling/disabling adapters (Petr Oros) [1611768]
- [acpi] ACPICA: Reference Counts: increase max to 0x4000 for large servers (Frank Ramsay) [1618760]

* Tue Sep 18 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-11.el8]
- [net] udp6: add missing checks on edumux packet processing (Paolo Abeni) [1625954]
- [net] udp4: fix IP_CMSG_CHECKSUM for connected sockets (Paolo Abeni) [1625954]
- [s390] s390/pci: fix out of bounds access during irq setup (Hendrik Brueckner) [1627462]
- [nvdimm] libnvdimm: fix ars_status output length calculation (Jeff Moyer) [1616307]

* Mon Sep 17 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-10.el8]
- [scsi] scsi: lpfc: Correct MDS diag and nvmet configuration (Dick Kennedy) [1628323]
- [iommu] iommu/arm-smmu: workaround DMA mode issues (Mark Salter) [1624077]
- [x86] x86/microcode: Allow late microcode loading with SMT disabled (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] tools headers: Synchronise x86 cpufeatures.h for L1TF additions (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/mm/kmmio: Make the tracer robust against L1TF (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/mm/pat: Make set_memory_np() L1TF safe (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Make pmd/pud_mknotpresent() invert (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Invert all not present mappings (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Fix SMT supported evaluation (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] KVM: VMX: Tell the nested hypervisor to skip L1D flush on vmentry (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation: Use ARCH_CAPABILITIES to skip L1D flush on vmentry (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation: Simplify sysfs report of VMX L1TF vulnerability (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] Documentation/l1tf: Remove Yonah processors from not vulnerable list (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Don't set l1tf_flush_l1d from vmx_handle_external_intr() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/irq: Let interrupt handlers set kvm_cpu_l1tf_flush_l1d (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86: Don't include linux/irq.h from asm/hardirq.h (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Introduce per-host-cpu analogue of l1tf_flush_l1d (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/irq: Demote irq_cpustat_t::__softirq_pending to u16 (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Move the l1tf_flush_l1d test to vmx_l1d_flush() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Replace 'vmx_l1d_flush_always' with 'vmx_l1d_flush_cond' (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Don't set l1tf_flush_l1d to true from vmx_l1d_flush() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: detect SMT disabled by BIOS (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] Documentation/l1tf: Fix typos (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Initialize the vmx_l1d_flush_pages' content (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Unbreak !__HAVE_ARCH_PFN_MODIFY_ALLOWED architectures (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] Documentation: Add section about CPU vulnerabilities (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/bugs, kvm: Introduce boot-time control of L1TF mitigations (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Set CPU_SMT_NOT_SUPPORTED early (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Expose SMT control init function (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/kvm: Allow runtime control of L1D flush (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/kvm: Serialize L1D flush parameter setter (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/kvm: Add static key for flush always (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/kvm: Move l1tf setup function (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/l1tf: Handle EPT disabled state proper (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/kvm: Drop L1TF MSR list approach (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/litf: Introduce vmx status variable (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Online siblings when SMT control is turned on (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Use MSR save list for IA32_FLUSH_CMD if required (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Extend add_atomic_switch_msr() to allow VMENTER only MSRs (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Separate the VMX AUTOLOAD guest/host number accounting (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Add find_msr() helper function (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Split the VMX MSR LOAD structures to have an host/guest numbers (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Add L1D flush logic (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Add L1D MSR based flush (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Add L1D flush algorithm (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM/VMX: Add module argument for L1TF mitigation (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/KVM: Warn user if KVM is loaded SMT and L1TF CPU bug being present (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Boot HT siblings at least once (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] Revert "x86/apic: Ignore secondary threads if nosmt=force" (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Fix up pte->pfn conversion for PAE (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Protect PAE swap entries against L1TF (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/CPU/AMD: Move TOPOEXT reenablement before reading smp_num_siblings (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpufeatures: Add detection of L1D cache flush support (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Extend 64bit swap file size limit (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/apic: Ignore secondary threads if nosmt=force (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpu/AMD: Evaluate smp_num_siblings early (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/CPU/AMD: Do not check CPUID max ext level before parsing SMP info (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpu/intel: Evaluate smp_num_siblings early (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpu/topology: Provide detect_extended_topology_early() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpu/common: Provide detect_ht_early() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpu/AMD: Remove the pointless detect_ht() call (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/cpu: Remove the pointless CPU printout (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Provide knobs to control SMT (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Split do_cpu_down() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] cpu/hotplug: Make bringup/teardown of smp threads symmetric (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/topology: Provide topology_smt_supported() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/smp: Provide topology_is_primary_thread() (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] sched/smt: Update sched_smt_present at runtime (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/bugs: Move the l1tf function and define pr_fmt properly (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Limit swap file size to MAX_PA/2 (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Disallow non privileged high MMIO PROT_NONE mappings (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Add sysfs reporting for l1tf (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Make sure the first page is always reserved (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Protect PROT_NONE PTEs against speculation (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Protect swap entries against L1TF (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Change order of offset/type in swap entry (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}
- [x86] x86/speculation/l1tf: Increase 32bit PAE __PHYSICAL_PAGE_SHIFT (Waiman Long) [1616046] {CVE-2018-3620 CVE-2018-3646}

* Thu Sep 13 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-9.el8]
- [pci] PCI/DPC: Remove indirection waiting for inactive link (Myron Stowe) [1485556]
- [pci] PCI/DPC: Use threaded IRQ for bottom half handling (Myron Stowe) [1485556]
- [pci] PCI/DPC: Print AER status in DPC event handling (Myron Stowe) [1485556]
- [pci] PCI/DPC: Remove rp_pio_status from dpc struct (Myron Stowe) [1485556]
- [pci] PCI/DPC: Defer event handling to work queue (Myron Stowe) [1485556]
- [pci] PCI/DPC: Leave interrupts enabled while handling event (Myron Stowe) [1485556]
- [net] net/mlx5e: Offload TC matching on tos/ttl for ip tunnels (Erez Alfasi) [1615121]
- [net] net/mlx5e: Support setup of tos and ttl for tunnel key TC action offload (Erez Alfasi) [1615121]
- [net] net/mlx5e: Use ttl from route lookup on tc encap offload only if needed (Erez Alfasi) [1615121]
- [net] net/sched: cls_flower: Support matching on ip tos and ttl for tunnels (Erez Alfasi) [1615121]
- [net] flow_dissector: Dissect tos and ttl from the tunnel info (Erez Alfasi) [1615121]
- [net] net/sched: tunnel_key: Allow to set tos and ttl for tc based ip tunnels (Erez Alfasi) [1615121]
- [net] net/sched: act_tunnel_key: disambiguate metadata dst error cases (Erez Alfasi) [1615121]
- [net] net/sched: add tunnel option support to act_tunnel_key (Erez Alfasi) [1615121]
- [iommu] iommu/amd: Add support for IOMMU XT mode (Suravee Suthikulpanit) [1504485]
- [iommu] iommu/amd: Add support for higher 64-bit IOMMU Control Register (Suravee Suthikulpanit) [1504485]
- [x86] x86: irq_remapping: Move irq remapping mode enum (Suravee Suthikulpanit) [1504485]
- [firmware] dcdbas: Add support for WSMT ACPI table (Charles Rose) [1502286]

* Wed Sep 12 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-8.el8]
- [documentation] scsi: documentation: add scsi_mod.use_blk_mq to scsi-parameters (Ewan Milne) [1600014]
- [scsi] scsi: core: Update SCSI_MQ_DEFAULT help text to match default (Ewan Milne) [1600014]
- [scsi] scsi: core: switch to scsi-mq by default (Ewan Milne) [1600014]
- [pci] PCI: Match Root Port's MPS to endpoint's MPSS as necessary (Myron Stowe) [1502324]
- [pci] PCI: Skip MPS logic for Virtual Functions (VFs) (Myron Stowe) [1502324]
- [pci] PCI: Check for PCIe Link downtraining (Myron Stowe) [1502324]
- [pci] PCI: Workaround IDT switch ACS Source Validation erratum (Myron Stowe) [1502324]
- [of] OF: Don't set default coherent DMA mask (Mark Salter) [1581822]
- [acpi] ACPI/IORT: Don't set default coherent DMA mask (Mark Salter) [1581822]
- [iommu] iommu/dma: Respect bus DMA limit for IOVAs (Mark Salter) [1581822]
- [of] of/device: Set bus DMA mask as appropriate (Mark Salter) [1581822]
- [acpi] ACPI/IORT: Set bus DMA mask as appropriate (Mark Salter) [1581822]
- [kernel] dma-mapping: Generalise dma_32bit_limit flag (Mark Salter) [1581822]
- [acpi] ACPI/IORT: Support address size limit for root complexes (Mark Salter) [1581822]
- [of] of/platform: Initialise default DMA masks (Mark Salter) [1581822]
- [net] Bluetooth: hidp: buffer overflow in hidp_process_report (Gopal Tiwari) [1623073] {CVE-2018-9363}
- [irqchip] irqchip/gic-v3-its: Reduce minimum LPI allocation to 1 for PCI devices (Mark Salter) [1550500]
- [irqchip] irqchip/gic-v3-its: Honor hypervisor enforced LPI range (Mark Salter) [1550500]
- [irqchip] irqchip/gic-v3: Expose GICD_TYPER in the rdist structure (Mark Salter) [1550500]
- [irqchip] irqchip/gic-v3-its: Drop chunk allocation compatibility (Mark Salter) [1550500]
- [irqchip] irqchip/gic-v3-its: Move minimum LPI requirements to individual busses (Mark Salter) [1550500]
- [irqchip] irqchip/gic-v3-its: Use full range of LPIs (Mark Salter) [1550500]
- [irqchip] irqchip/gic-v3-its: Refactor LPI allocator (Mark Salter) [1550500]

* Tue Sep 11 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-7.el8]
- [netdrv] hv_netvsc: Fix a deadlock by getting rtnl lock earlier in netvsc_probe() (Vitaly Kuznetsov) [1625609]
- [netdrv] hv_netvsc: ignore devices that are not PCI (Vitaly Kuznetsov) [1625609]
- [netdrv] hv/netvsc: Fix NULL dereference at single queue mode fallback (Vitaly Kuznetsov) [1625609]
- [netdrv] hv_netvsc: Add per-cpu ethtool stats for netvsc (Vitaly Kuznetsov) [1625609]
- [pci] PCI: shpchp: Separate existence of SHPC and permission to use it (Steve Best) [1622953]
- [powerpc] KVM: PPC: Book3S HV: Don't truncate HPTE index in xlate function (David Gibson) [1625513]
- [kernel] rh_kabi: Add macros to size and extend structs (Prarit Bhargava) [1564570]
- [pci] PCI: Remove unnecessary include of <linux/pci-aspm.h> (Myron Stowe) [1622672]
- [wireless] iwlwifi: Remove unnecessary include of <linux/pci-aspm.h> (Myron Stowe) [1622672]
- [wireless] ath9k: Remove unnecessary include of <linux/pci-aspm.h> (Myron Stowe) [1622672]
- [netdrv] igb: Remove unnecessary include of <linux/pci-aspm.h> (Myron Stowe) [1622672]
- [pci] PCI/ASPM: Convert to use sysfs_match_string() helper (Myron Stowe) [1622672]
- [virt] KVM: s390: Properly lock mm context allow_gmap_hpage_1m setting (Thomas Huth) [1623513]
- [virt] KVM: s390: vsie: copy wrapping keys to right place (Thomas Huth) [1623513]
- [virt] KVM: s390: Fix pfmf and conditional skey emulation (Thomas Huth) [1623513]
- [virt] KVM: s390: Fix storage attributes migration with memory slots (Thomas Huth) [1623513]
- [virt] KVM: s390: a utility function for migration (Thomas Huth) [1623513]

* Mon Sep 10 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-6.el8]
- [lib] vsprintf: Add command line option debug_boot_weak_hash (Prarit Bhargava) [1625687]
- [netdrv] i40e: Fix for Tx timeouts when interface is brought up if DCB is enabled (Stefan Assmann) [1616147]
- [misc] ocxl: Fix page fault handler in case of fault on dying process (Steve Best) [1624644]
- [edac] EDAC, sb_edac: Add support for systems with segmented PCI buses (Aristeu Rozanski) [1621849]
- [netdrv] xen-netfront: fix warn message as irq device name has '/' (Vitaly Kuznetsov) [1576160]
- [arm64] arm64, kaslr: export offset in VMCOREINFO ELF notes (Bhupesh Sharma) [1624246]
- [rpmspec] redhat: Move gfs2 and dlm out of kernel-modules-extra (Andrew Price) [1623511]
- [powerpc] powerpc/topology: Get topology for shared processors at boot (Steve Best) [1620039]
- [fs] gfs2: Don't set GFS2_RDF_UPTODATE when the lvb is updated (Robert S Peterson) [1622057]
- [fs] gfs2: improve debug information when lvb mismatches are found (Robert S Peterson) [1622057]
- [fs] gfs2: cleanup: call gfs2_rgrp_ondisk2lvb from gfs2_rgrp_out (Robert S Peterson) [1622057]
- [x86] Fix x86 32-bit invalid cpu boot failure message (Prarit Bhargava) [1571456]
- [net] net/ipv6: init ip6 anycast rt->dst.input as ip6_input (Hangbin Liu) [1615671]
- [pci] PCI/AER: Don't clear AER bits if error handling is Firmware-First (Myron Stowe) [1621933]
- [pci] PCI/AER: Remove duplicate PCI_EXP_AER_FLAGS definition (Myron Stowe) [1621933]
- [pci] PCI/portdrv: Remove pcie_portdrv_err_handler.slot_reset (Myron Stowe) [1621933]
- [pci] PCI/AER: Clear device status bits during ERR_COR handling (Myron Stowe) [1621933]
- [pci] PCI/AER: Clear device status bits during ERR_FATAL and ERR_NONFATAL (Myron Stowe) [1621933]
- [pci] PCI/AER: Remove ERR_FATAL code from ERR_NONFATAL path (Myron Stowe) [1621933]
- [pci] PCI/AER: Factor out ERR_NONFATAL status bit clearing (Myron Stowe) [1621933]
- [pci] PCI/AER: Clear only ERR_NONFATAL bits during non-fatal recovery (Myron Stowe) [1621933]
- [pci] PCI/AER: Clear only ERR_FATAL status bits during fatal recovery (Myron Stowe) [1621933]
- [pci] PCI/AER: Honor "pcie_ports=native" even if HEST sets FIRMWARE_FIRST (Myron Stowe) [1621933]
- [pci] PCI/AER: Add sysfs attributes for rootport cumulative stats (Myron Stowe) [1621933]
- [pci] PCI/AER: Add sysfs attributes to provide AER stats and breakdown (Myron Stowe) [1621933]
- [pci] PCI/AER: Define aer_stats structure for AER capable devices (Myron Stowe) [1621933]
- [pci] PCI/AER: Move internal declarations to drivers/pci/pci.h (Myron Stowe) [1621933]
- [pci] PCI/AER: Adopt lspci names for AER error decoding (Myron Stowe) [1621933]
- [pci] PCI/AER: Expose internal API for obtaining AER information (Myron Stowe) [1621933]
- [kernel] rcu: Make expedited GPs handle CPU 0 being offline (Gustavo Duarte) [1610262]
- [rpmspec] Generate BootLoaderSpec config fragments ("Herton R. Krzesinski") [1619766]

* Wed Aug 29 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-5.el8]
- [net] erspan: set erspan_ver to 1 by default when adding an erspan dev (Xin Long) [1619118]
- [hv] x86/hyper-v: Fix wrong merge conflict resolution (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Check for VP_INVAL in hyperv_flush_tlb_others() (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Check cpumask_to_vpset() return value in hyperv_flush_tlb_others_ex() (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Trace PV IPI send (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Use cheaper HVCALL_SEND_IPI hypercall when possible (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Use 'fast' hypercall for HVCALL_SEND_IPI (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Implement hv_do_fast_hypercall16 (Vitaly Kuznetsov) [1597652]
- [hv] x86/hyper-v: Use cheaper HVCALL_FLUSH_VIRTUAL_ADDRESS_(LIST, SPACE) hypercalls when possible (Vitaly Kuznetsov) [1597652]
- [netdrv] xen-netfront: fix queue name setting (Vitaly Kuznetsov) [1576160]
- [scsi] lfpc: add Lancer FCoE to the removed devices (Tomas Henzl) [1602033]
- [scsi] megaraid_sas: add removed id table (Tomas Henzl) [1602033]
- [scsi] aacraid: add removed id table (Tomas Henzl) [1602033]
- [scsi] qla4xxx: add removed id table (Tomas Henzl) [1602033]
- [scsi] lpfc: add removed id table (Tomas Henzl) [1602033]
- [scsi] qla2xxx: add removed id table (Tomas Henzl) [1602033]
- [scsi] mpt3sas: add removed id table (Tomas Henzl) [1602033]
- [scsi] be2iscsi: add removed id table (Tomas Henzl) [1602033]
- [scsi] rh_taint, pci : add information about removed hardware (Tomas Henzl) [1602033]
- [kernel] kernel: add SUPPORT_REMOVED kernel taint (Tomas Henzl) [1602033]
- [net] sunrpc: Change rpc_print_iostats to rpc_clnt_show_stats and handle rpc_clnt clones (Dave Wysochanski) [1610373]
- [net] sunrpc: Add _add_rpc_iostats() to add rpc_iostats metrics (Dave Wysochanski) [1610373]
- [net] sunrpc: add _print_rpc_iostats() to output metrics for one RPC op (Dave Wysochanski) [1610373]

* Mon Aug 27 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-4.el8]
- [net] xdp: exclude XDP from kABI guarantee (Jiri Benc) [1568551]
- [kernel] rh_kabi: introduce RH_KABI_EXCLUDE (Jiri Benc) [1568551]
- [powerpc] powerpc/powernv/pci: Work around races in PCI bridge enabling (Steve Best) [1620035]
- [block] blk-wbt: fix IO hang in wbt_wait() (Ming Lei) [1614198]
- [block] blkcg: Make blkg_root_lookup() work for queues in bypass mode (Ming Lei) [1614198]
- [block] null_blk: add lock drop/acquire annotation (Ming Lei) [1614198]
- [block] Blk-throttle: reduce tail io latency when iops limit is (Ming Lei) [1614198]
- [block] block: paride: pd: mark expected switch fall-throughs (Ming Lei) [1614198]
- [block] block: Ensure that a request queue is dissociated from the (Ming Lei) [1614198]
- [block] block: Introduce blk_exit_queue() (Ming Lei) [1614198]
- [block] blkcg: Introduce blkg_root_lookup() (Ming Lei) [1614198]
- [block] block: Remove two superfluous #include directives (Ming Lei) [1614198]
- [block] blk-mq: count the hctx as active before allocating tag (Ming Lei) [1614198]
- [block] block: bvec_nr_vecs() returns value for wrong slab (Ming Lei) [1614198]
- [block] drivers/block/drbd: remove the null check for (Ming Lei) [1614198]
- [block] drivers/block/aoe/aoedev: NULL check is not needed for (Ming Lei) [1614198]
- [block] drivers/block/mtip32xx: remove the null check for (Ming Lei) [1614198]
- [block] cfq: Suppress compiler warnings about comparisons (Ming Lei) [1614198]
- [block] cfq: Annotate fall-through in a switch statement (Ming Lei) [1614198]
- [block] blk-wbt: Avoid lock contention and thundering herd issue in (Ming Lei) [1590363]
- [block] target/loop: depend on SCSI (Ming Lei) [1614198]
- [block] xen-blkfront: use true and false for boolean values (Ming Lei) [1614198]
- [block] lightnvm: remove minor version check for 2.0 (Ming Lei) [1614198]
- [block] scsi: Check sense buffer size at build time (Ming Lei) [1614198]
- [block] libata-scsi: Move sense buffers onto stack (Ming Lei) [1614198]
- [block] cdrom: Use struct scsi_sense_hdr internally (Ming Lei) [1614198]
- [block] ide-cd: Remove redundant sense buffer (Ming Lei) [1614198]
- [block] block: Switch struct packet_command to use struct (Ming Lei) [1614198]
- [block] target: don't depend on SCSI (Ming Lei) [1614198]
- [block] scsi: build scsi_common.o for all scsi passthrough request (Ming Lei) [1614198]
- [block] scsi: cxlflash: Drop unused sense buffers (Ming Lei) [1614198]
- [block] ide-cd: Drop unused sense buffers (Ming Lei) [1614198]
- [block] blk-mq: fix updating tags depth (Ming Lei) [1611900]
- [block] block: really disable runtime-pm for blk-mq (Ming Lei) [1611902]
- [block] aoe: mark expected switch fall-through (Ming Lei) [1614198]
- [block] block: make iolatency avg_lat exponentially decay (Ming Lei) [1614198]
- [block] blk-cgroup: clear the throttle queue on fork (Ming Lei) [1614198]
- [block] blk-cgroup: hold the queue ref during throttling (Ming Lei) [1614198]
- [block] blk-iolatency: fix blkg leak in timer_fn (Ming Lei) [1614198]
- [block] block/bsg-lib: use PTR_ERR_OR_ZERO to simplify the flow path (Ming Lei) [1614198]
- [block] t10-pi: provide empty t10_pi_complete() for (Ming Lei) [1614198]
- [block] block: blk_init_allocated_queue() set q->fq as NULL in the (Ming Lei) [1614198]
- [block] nvme: use blk API to remap ref tags for IOs with metadata (Ming Lei) [1614198]
- [block] block: move dif_prepare/dif_complete functions to block layer (Ming Lei) [1614198]
- [block] block: move ref_tag calculation func to the block layer (Ming Lei) [1614198]
- [block] block: don't account for split bio's size in cgroup stats (Ming Lei) [1614198]
- [block] pktcdvd: Fix possible Spectre-v1 for pkt_devs (Ming Lei) [1614198]
- [block] partitions/aix: append null character to print data from disk (Ming Lei) [1614198]
- [block] partitions/aix: fix usage of uninitialized lv_info and lvname (Ming Lei) [1614198]
- [block] readahead: stricter check for bdi io_pages (Ming Lei) [1614198]
- [block] scsi: virtio_scsi: fix pi_bytes(out, in) on 4 KiB block size (Ming Lei) [1614198]
- [block] block: move bio_integrity_(intervals, bytes) into blkdev.h (Ming Lei) [1614198]
- [block] xen/blkfront: remove unused macros (Ming Lei) [1614198]
- [block] block: allow max_discard_segments to be stacked (Ming Lei) [1614198]
- [block] block: unexport bio_clone_bioset (Ming Lei) [1614198]
- [block] md: remove a bogus comment (Ming Lei) [1614198]
- [block] block: remove bio_clone_kmalloc (Ming Lei) [1614198]
- [block] exofs: use bio_clone_fast in _write_mirror (Ming Lei) [1614198]
- [block] bcache: don't clone bio in bch_data_verify (Ming Lei) [1614198]
- [block] block: bio_set_pages_dirty can't see NULL bv_page in a valid (Ming Lei) [1614198]
- [block] block: simplify bio_check_pages_dirty (Ming Lei) [1614198]
- [block] block: Rename the null_blk_mod kernel module back into (Ming Lei) [1614198]
- [block] blk-mq: fail the request in case issue failure (Ming Lei) [1614305]
- [block] blk-rq-qos: make depth comparisons unsigned (Ming Lei) [1614198]
- [block] blkcg: Track DISCARD statistics and output them in cgroup (Ming Lei) [1614198]
- [block] block: Track DISCARD statistics and output them in stat and (Ming Lei) [1614198]
- [block] block: Add and use op_stat_group() for indexing disk_stat (Ming Lei) [1614198]
- [block] block: Define and use STAT_READ and STAT_WRITE (Ming Lei) [1614198]
- [block] block: Add part_stat_read_accum to read across field entries (Ming Lei) [1614198]
- [block] block: make bdev_ops->rw_page() take a REQ_OP instead of bool (Ming Lei) [1614198]
- [block] pktcdvd: remove assignment in if condition (Ming Lei) [1614198]
- [block] blk-mq: issue directly if hw queue isn't busy in case of (Ming Lei) [1614305]
- [block] blk-iolatency: truncate our current time (Ming Lei) [1614198]
- [block] blk-iolatency: don't change the latency window (Ming Lei) [1614198]
- [block] block: remove blkdev_entry_to_request() macro (Ming Lei) [1614198]
- [block] block: skd: Use pad printk format for dma_addr_t values (Ming Lei) [1614198]
- [block] bsg: remove read/write support (Ming Lei) [1614198]
- [block] blk-iolatency: fix max_depth comparisons (Ming Lei) [1614198]
- [block] block: iolatency: avoid 64-bit division (Ming Lei) [1614198]
- [block] block/DAC960.c: fix defined but not used build warnings (Ming Lei) [1614198]
- [block] null_blk: add zone support (Ming Lei) [1614198]
- [block] null_blk: move shared definitions to header file (Ming Lei) [1614198]
- [block] block: Add default switch case to blk_pm_allow_request() to (Ming Lei) [1614198]
- [block] block: fix infinite loop if the device loses discard (Ming Lei) [1614198]
- [block] block, mm: remove unnecessary __GFP_HIGH flag (Ming Lei) [1614198]
- [block] null_blk: remove NULLB_DEV_FL_CONFIGURED on turning off nullb (Ming Lei) [1614198]
- [block] mm: skip readahead if the cgroup is congested (Ming Lei) [1614198]
- [block] Documentation: add a doc for blk-iolatency (Ming Lei) [1614198]
- [block] block: introduce blk-iolatency io controller (Ming Lei) [1614198]
- [block] rq-qos: introduce dio_bio callback (Ming Lei) [1614198]
- [block] block: remove external dependency on wbt_flags (Ming Lei) [1614198]
- [block] blk-rq-qos: refactor out common elements of blk-wbt (Ming Lei) [1614198]
- [block] blk-stat: export helpers for modifying blk_rq_stat (Ming Lei) [1614198]
- [block] memcontrol: schedule throttling if we are congested (Ming Lei) [1614198]
- [block] blkcg: add generic throttling mechanism (Ming Lei) [1614198]
- [block] swap, blkcg: issue swap io with the appropriate context (Ming Lei) [1614198]
- [block] blk: introduce REQ_SWAP (Ming Lei) [1614198]
- [block] blk-cgroup: allow controllers to output their own stats (Ming Lei) [1614198]
- [block] block: introduce bio_issue_as_root_blkg (Ming Lei) [1614198]
- [block] block: add bi_blkg to the bio for cgroups (Ming Lei) [1614198]
- [block] blk-mq: dequeue request one by one from sw queue if hctx is (Ming Lei) [1614305]
- [block] block/loop: mark expected switch fall-through (Ming Lei) [1614198]
- [block] drbd: mark expected switch fall-throughs (Ming Lei) [1614198]
- [block] blk-mq: only attempt to merge bio if there is rq in sw queue (Ming Lei) [1614305]
- [block] blk-mq: use list_splice_tail_init() to insert requests (Ming Lei) [1614305]
- [block] blk-mq: fix typo in a function comment (Ming Lei) [1614198]
- [block] blk-mq: code clean-up by adding an API to clear set->mq_map (Ming Lei) [1614198]
- [block] paride: remove redundant variable n (Ming Lei) [1614198]
- [block] partitions/ldm: remove redundant pointer dgrp (Ming Lei) [1614198]
- [block] loop: remove redundant pointer inode (Ming Lei) [1614198]
- [block] block/floppy: remove redundant variable dflags (Ming Lei) [1614198]
- [block] Block: blk-throttle: set low_valid immediately once one (Ming Lei) [1614198]
- [block] Blktrace: bail out early if block debugfs is not configured (Ming Lei) [1614198]
- [block] block: Document how blk_update_request() handles (Ming Lei) [1614198]
- [block] drbd: Do not redefine __must_hold() (Ming Lei) [1614198]
- [block] blk-mq: avoid to synchronize rcu inside blk_cleanup_queue() (Ming Lei) [1597067]
- [block] blk-mq: remove synchronize_rcu() from (Ming Lei) [1597067]
- [block] blk-mq: introduce new lock for protecting hctx->dispatch_wait (Ming Lei) [1597067]
- [block] blk-mq: don't pass **hctx to blk_mq_mark_tag_wait() (Ming Lei) [1597067]
- [block] blk-mq: cleanup blk_mq_get_driver_tag() (Ming Lei) [1597067]
- [block] block, bfq: give a better name to bfq_bfqq_may_idle (Ming Lei) [1614198]
- [block] block, bfq: fix service being wrongly set to zero in case of (Ming Lei) [1614198]
- [block] block, bfq: do not expire a queue that will deserve dispatch (Ming Lei) [1614198]
- [block] block, bfq: add/remove entity weights correctly (Ming Lei) [1614198]
- [block] block: Make struct request_queue smaller for (Ming Lei) [1614198]
- [block] block: Inline blk_queue_nr_zones() (Ming Lei) [1614198]
- [block] block: Remove bdev_nr_zones() (Ming Lei) [1614198]
- [block] include/uapi/linux/blkzoned.h: Remove a superfluous __packed (Ming Lei) [1614198]
- [block] block: Remove a superfluous cast from blkdev_report_zones() (Ming Lei) [1614198]

* Fri Aug 24 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-3.el8]
- [net] tls: mark as Tech Preview (Sabrina Dubroca) [1570255]
- [pci] PCI/VPD: Check for VPD access completion before checking for timeout (Myron Stowe) [1618820]
- [rpmspec] redhat: remove bootwrapper subpackage (Gustavo Duarte) [1578399]
- [virt] kvm: x86: Set highest physical address bits in non-present/reserved SPTEs (Paolo Bonzini) [1614808]
- [virt] KVM/x86: Use CC_SET()/CC_OUT in arch/x86/kvm/vmx.c (Paolo Bonzini) [1614808]
- [virt] KVM: X86: Implement PV IPIs in linux guest (Paolo Bonzini) [1614808]
- [virt] KVM: X86: Add kvm hypervisor init time platform setup callback (Paolo Bonzini) [1614808]
- [virt] KVM: X86: Implement "send IPI" hypercall (Paolo Bonzini) [1614808]
- [virt] KVM/x86: Move X86_CR4_OSXSAVE check into kvm_valid_sregs() (Paolo Bonzini) [1614808]
- [virt] KVM: x86: Skip pae_root shadow allocation if tdp enabled (Paolo Bonzini) [1614808]
- [virt] KVM/MMU: Combine flushing remote tlb in mmu_set_spte() (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: skip VMWRITE of HOST_(FS, GS)_BASE when possible (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: skip VMWRITE of HOST_(FS, GS)_SEL when possible (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: always initialize HOST_(FS, GS)_BASE to zero during setup (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: move struct host_state usage to struct loaded_vmcs (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: compute need to reload FS/GS/LDT on demand (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: remove a misleading comment regarding vmcs02 fields (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: rename __vmx_load_host_state() and vmx_save_host_state() (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: add dedicated utility to access guest's kernel_gs_base (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: track host_state.loaded using a loaded_vmcs pointer (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: refactor segmentation code in vmx_save_host_state() (Paolo Bonzini) [1614808]
- [virt] kvm: nVMX: Fix fault priority for VMX operations (Paolo Bonzini) [1614808]
- [virt] kvm: nVMX: Fix fault vector for VMX operation at CPL > 0 (Paolo Bonzini) [1614808]
- [virt] KVM: try __get_user_pages_fast even if not in atomic context (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: Add tlb_remote_flush callback support (Paolo Bonzini) [1614808]
- [virt] KVM: x86: Add tlb remote flush callback in kvm_x86_ops (Paolo Bonzini) [1614808]
- [virt] X86/Hyper-V: Add hyperv_nested_flush_guest_mapping ftrace support (Paolo Bonzini) [1614808]
- [virt] X86/Hyper-V: Add flush HvFlushGuestPhysicalAddressSpace hypercall support (Paolo Bonzini) [1614808]
- [virt] x86/kvm: Don't use pvqspinlock code if only 1 vCPU (Paolo Bonzini) [1614808]
- [virt] KVM/MMU: Simplify __kvm_sync_page() function (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Remove CR3_PCID_INVD flag (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Add multi-entry LRU cache for previous CR3s (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Flush only affected TLB entries in kvm_mmu_invlpg* (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Skip shadow page resync on CR3 switch when indicated by guest (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Support selectively freeing either current or previous MMU root (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Add a root_hpa parameter to kvm_mmu->invlpg() (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Skip TLB flush on fast CR3 switch when indicated by guest (Paolo Bonzini) [1614808]
- [virt] kvm: vmx: Support INVPCID in shadow paging mode (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Propagate guest PCIDs to host PCIDs (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Add ability to skip TLB flush when switching CR3 (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Use fast CR3 switch for nested VMX (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Support resetting the MMU context without resetting roots (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Add support for fast CR3 switch across different MMU modes (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Introduce KVM_REQ_LOAD_CR3 (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Introduce kvm_mmu_calc_root_page_role() (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Add fast CR3 switch code path (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Avoid taking MMU lock in kvm_mmu_sync_roots if no sync is needed (Paolo Bonzini) [1614808]
- [virt] kvm: x86: Make sync_page() flush remote TLBs once only (Paolo Bonzini) [1614808]
- [virt] KVM: MMU: drop vcpu param in gpte_access (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Separate logic allocating shadow vmcs to a function (Paolo Bonzini) [1614808]
- [virt] KVM: VMX: Mark vmcs header as shadow in case alloc_vmcs_cpu() allocate shadow vmcs (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Expose VMCS shadowing to L1 guest (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Do not forward VMREAD/VMWRITE VMExits to L1 if required so by vmcs12 vmread/vmwrite bitmaps (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: vmread/vmwrite: Use shadow vmcs12 if running L2 (Paolo Bonzini) [1614808]
- [virt] KVM: selftests: add tests for shadow VMCS save/restore (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: include shadow vmcs12 in nested state (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Cache shadow vmcs12 on VMEntry and flush to memory on VMExit (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Verify VMCS shadowing VMCS link pointer (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Verify VMCS shadowing controls (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Introduce nested_cpu_has_shadow_vmcs() (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Fail VMLAUNCH and VMRESUME on shadow VMCS (Paolo Bonzini) [1614808]
- [virt] KVM: nVMX: Allow VMPTRLD for shadow VMCS if vCPU supports VMCS shadowing (Paolo Bonzini) [1614808]
- [virt] KVM: VMX: Change vmcs12(read, write)_any() to receive vmcs12 as parameter (Paolo Bonzini) [1614808]
- [virt] KVM: VMX: Create struct for VMCS header (Paolo Bonzini) [1614808]
- [virt] kvm: selftests: add test for nested state save/restore (Paolo Bonzini) [1614808]
- [virt] kvm: nVMX: Introduce KVM_CAP_NESTED_STATE (Paolo Bonzini) [1614808]
- [virt] KVM: x86: do not load vmcs12 pages while still in SMM (Paolo Bonzini) [1614808]
- [virt] kvm: selftests: add basic test for state save and restore (Paolo Bonzini) [1614808]
- [virt] kvm: selftests: ensure vcpu file is released (Paolo Bonzini) [1614808]
- [virt] kvm: selftests: actually use all of lib/vmx.c (Paolo Bonzini) [1614808]
- [virt] kvm: selftests: create a GDT and TSS (Paolo Bonzini) [1614808]
- [virt] KVM: x86: ensure all MSRs can always be KVM_GET/SET_MSR'd (Paolo Bonzini) [1614808]
- [virt] KVM: vmx: remove save/restore of host BNDCGFS MSR (Paolo Bonzini) [1614808]
- [virt] KVM: Switch 'requests' to be 64-bit (explicitly) (Paolo Bonzini) [1614808]
- [virt] kvm: selftests: add cr4_cpuid_sync_test (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Book3S HV: Read kvm->arch.emul_smt_mode under kvm->lock (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Book3S HV: Allow creating max number of VCPUs on POWER9 (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Book3S HV: Pack VCORE IDs to access full VCPU ID space (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Book3S HV: Fix constant size warning (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Book3S HV: Add of_node_put() in success path (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Book3S: Fix matching of hardware and emulated TCE tables (Paolo Bonzini) [1614808]
- [virt] KVM: PPC: Remove mmio_vsx_tx_sx_enabled in KVM MMIO emulation (Paolo Bonzini) [1614808]

* Fri Aug 17 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-2.el8]
- [net] tcp: Add tcp_clamp_rto_to_user_timeout() helper to improve accuracy (Michael Cambria) [1605024]
- [net] tcp: Add tcp_retransmit_stamp() helper routine (Michael Cambria) [1605024]
- [net] tcp: convert icsk_user_timeout from jiffies to msecs (Michael Cambria) [1605024]
- [kernel] Revert sched/fair: Consider SD_NUMA when selecting the most idle group to schedule on (Lauro Ramos Venancio) [1585746]
- [kernel] redhat: makefile: adjust KBUILD_CFLAGS to reflect kernel.spec for powerpc builds (Gustavo Duarte) [1582568]
- [rpmspec] redhat: spec: build ppc64le kernel with -O3 (Gustavo Duarte) [1582568]
- [scsi] scsi: csiostor: update csio_get_flash_params() (Arjun Vynipadath) [1503574]
- [scsi] csiostor: Add a soft dep on cxgb4 driver (Arjun Vynipadath) [1503574]
- [firmware] dell_rbu: make firmware payload memory uncachable (Charles Rose) [1584401]

* Mon Aug 13 2018 Herton R. Krzesinski <herton@redhat.com> [4.18.0-1.el8]
- [scsi] scsi: lpfc: update driver version to 12.0.0.6 (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Remove lpfc_enable_pbde as module parameter (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Correct LCB ACCept payload (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Limit tracking of tgt queue depth in fast path (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Fix driver crash when re-registering NVME rports (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Fix list corruption on the completion queue (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Fix sysfs Speed value on CNA ports (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: Fix ELS abort on SLI-3 adapters (Dick Kennedy) [1613913]
- [scsi] scsi: lpfc: remove null check on nvmebuf (Dick Kennedy) [1613913]
- [arm64] arm64: fix ACPI dependencies (Bhupesh Sharma) [1556832]
- [arm64] arm64: acpi: fix alignment fault in accessing ACPI (Bhupesh Sharma) [1556832]
- [firmware] efi/arm: map UEFI memory map even w/o runtime services enabled (Bhupesh Sharma) [1556832]
- [firmware] efi/arm: preserve early mapping of UEFI memory map longer for BGRT (Bhupesh Sharma) [1556832]
- [acpi] drivers: acpi: add dependency of EFI for arm64 (Bhupesh Sharma) [1556832]
- [arm64] arm64: export memblock_reserve()d regions via /proc/iomem (Bhupesh Sharma) [1556832]
- [arm64] arm64: kconfig: Ensure spinlock fastpaths are inlined if !PREEMPT (Waiman Long) [1607924]
- [arm64] arm64: locking: Replace ticket lock implementation with qspinlock (Waiman Long) [1607924]
- [arm64] arm64: barrier: Implement smp_cond_load_relaxed (Waiman Long) [1607924]
- [scsi] scsi: lpfc: Revise copyright for new company language (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: update driver version to 12.0.0.5 (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: devloss timeout race condition caused null pointer reference (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Fix NVME Target crash in defer rcv logic (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Support duration field in Link Cable Beacon V1 command (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Make PBDE optimizations configurable (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Fix abort error path for NVMET (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Fix panic if driver unloaded when port is offline (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Fix driver not setting dpp bits correctly in doorbell word (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: Add Buffer overflow check, when nvme_info larger than PAGE_SIZE (Dick Kennedy) [1600946]
- [scsi] scsi: lpfc: use monotonic timestamps for statistics (Dick Kennedy) [1600946]
- [x86] mark intel knights landing and knights mill unsupported (David Arcari) [1610493]
- [netdrv] igb: Remove superfluous reset to PHY and page 0 selection (Corinna Vinschen) [1612824]
- [tools] selftests/powerpc: Fix ptrace-pkey for default execute permission change (Steve Best) [1498799]
- [tools] selftests/powerpc: Fix core-pkey for default execute permission change (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: make protection key 0 less special (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: Preallocate execute-only key (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: Fix calculation of total pkeys (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: Save the pkey registers before fork (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: key allocation/deallocation must not change pkey registers (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: Deny read/write/execute by default (Steve Best) [1498799]
- [powerpc] powerpc/pkeys: Give all threads control of their key permissions (Steve Best) [1498799]
- [s390] KVM: s390: Add huge page enablement control (David Hildenbrand) [1508102]
- [s390] s390/mm: Add huge page gmap linking support (David Hildenbrand) [1508102]
- [s390] s390/mm: hugetlb pages within a gmap can not be freed (David Hildenbrand) [1508102]
- [s390] KVM: s390: Beautify skey enable check (David Hildenbrand) [1508102]
- [s390] KVM: s390: Add skey emulation fault handling (David Hildenbrand) [1508102]
- [s390] s390/mm: Add huge pmd storage key handling (David Hildenbrand) [1508102]
- [s390] s390/mm: Clear skeys for newly mapped huge guest pmds (David Hildenbrand) [1508102]
- [s390] s390/mm: Clear huge page storage keys on enable_skey (David Hildenbrand) [1508102]
- [s390] s390/mm: Add huge page dirty sync support (David Hildenbrand) [1508102]
- [s390] s390/mm: Add gmap pmd invalidation and clearing (David Hildenbrand) [1508102]
- [s390] s390/mm: Add gmap pmd notification bit setting (David Hildenbrand) [1508102]
- [s390] s390/mm: Add gmap pmd linking (David Hildenbrand) [1508102]
- [s390] s390/mm: Abstract gmap notify bit setting (David Hildenbrand) [1508102]
- [s390] s390/mm: Make gmap_protect_range more modular (David Hildenbrand) [1508102]
- [s390] KVM: s390: Replace clear_user with kvm_clear_guest (David Hildenbrand) [1508102]
- [hwmon] hwmon: (ibmpowernv) Add attributes to enable/disable sensor groups (Steve Best) [1524684]
- [powerpc] powerpc/powernv: Add support to enable sensor groups (Steve Best) [1524684]
- [net] net/smc: improve delete link processing (Hendrik Brueckner) [1548452]
- [net] net/smc: provide fallback reason code (Hendrik Brueckner) [1548452]
- [net] net/smc: use correct vlan gid of RoCE device (Hendrik Brueckner) [1548452]
- [net] net/smc: fewer parameters for smc_llc_send_confirm_link() (Hendrik Brueckner) [1548452]
- [net] net/smc: remove local variable page in smc_rx_splice() (Hendrik Brueckner) [1548452]
- [net] net/smc: use DECLARE_BITMAP for rtokens_used_mask (Hendrik Brueckner) [1548452]
- [net] net/smc: add function to get link group from link (Hendrik Brueckner) [1548452]
- [net] net/smc: eliminate cursor read and write calls (Hendrik Brueckner) [1548452]
- [net] net/smc: provide smc mode in smc_diag.c (Hendrik Brueckner) [1548452]
- [s390] s390/ism: add device driver for internal shared memory (Hendrik Brueckner) [1548452]
- [net] net/smc: add SMC-D diag support (Hendrik Brueckner) [1548452]
- [net] net/smc: add SMC-D support in af_smc (Hendrik Brueckner) [1548452]
- [net] net/smc: add SMC-D support in data transfer (Hendrik Brueckner) [1548452]
- [net] net/smc: add SMC-D support in CLC messages (Hendrik Brueckner) [1548452]
- [net] net/smc: add pnetid support for SMC-D and ISM (Hendrik Brueckner) [1548452]
- [net] net/smc: add base infrastructure for SMC-D and ISM (Hendrik Brueckner) [1548452]
- [net] net/smc: add pnetid support (Hendrik Brueckner) [1548452]
- [net] net/smc: determine port attributes independent from pnet table (Hendrik Brueckner) [1548452]
- [x86] mark whiskey-lake processor supported (David Arcari) [1609604]
- [s390] KVM: s390: add etoken support for guests (Thomas Huth) [1612110]
- [char] ipmi: do not configure ipmi for HPE m400 (Tony Camuso) [1583537]
- [scsi] scsi: ipr: Format HCAM overlay ID 0x41 (Steve Best) [1498222]
- [x86] x86/stacktrace: Enable HAVE_RELIABLE_STACKTRACE for the ORC unwinder (Joe Lawrence) [1587952]
- [x86] x86/unwind/orc: Detect the end of the stack (Joe Lawrence) [1587952]
- [x86] x86/stacktrace: Do not fail for ORC with regs on stack (Joe Lawrence) [1587952]
- [x86] x86/stacktrace: Clarify the reliable success paths (Joe Lawrence) [1587952]
- [x86] x86/stacktrace: Remove STACKTRACE_DUMP_ONCE (Joe Lawrence) [1587952]
- [x86] x86/stacktrace: Do not unwind after user regs (Joe Lawrence) [1587952]
- [infiniband] IB/rxe: Mark Soft-RoCE Transport driver as tech-preview (Don Dutile) [1605216]
- [scsi] scsi: smartpqi: bump driver version to 1.1.4-130 (Don Brace) [1503736]
- [scsi] scsi: smartpqi: fix critical ARM issue reading PQI index registers (Don Brace) [1503736]
- [scsi] scsi: smartpqi: add inspur advantech ids (Don Brace) [1503736]
- [scsi] scsi: smartpqi: improve error checking for sync requests (Don Brace) [1503736]
- [scsi] scsi: smartpqi: improve handling for sync requests (Don Brace) [1503736]
- [netdrv] ice: mark driver as tech-preview (Jonathan Toppins) [1495347]
- [init] init/Kconfig: remove EXPERT from CHECKPOINT_RESTORE (Adrian Reber) [1568995 1557617 1525389]
- [scsi] be2iscsi: remove BE3 family support (Maurizio Lombardi) [1598366]
- [x86] update rh_check_supported processor list (David Arcari) [1595918]
- [kernel] kABI: Add generic kABI macros to use for kABI workarounds (Myron Stowe) [1546831]
- [pci] add pci_hw_vendor_status() (Maurizio Lombardi) [1590829]
- [ata] ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1563590]
- [pci] Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1563590]
- [kernel] bpf: set default values for bpf_jit_harden and bpf_jit_kallsyms (Eugene Syromiatnikov) [1569061]
- [kernel] bpf: Add tech preview taint for syscall (Eugene Syromiatnikov) [1559877]
- [kernel] bpf: set unprivileged_bpf_disabled to 1 by default, add a boot parameter (Eugene Syromiatnikov) [1561171]
- [kernel] add Red Hat-specific taint flags (Eugene Syromiatnikov) [1559877]
- [tools] perf tests: Add Python 3 support to attr.py ("Herton R. Krzesinski") [1561505]
- [tools] perf scripts python: Add Python 3 support to stat-cpi.py ("Herton R. Krzesinski") [1561505]
- [kernel] kdump: fix a grammar issue in a kernel message (Dave Young) [1507353]
- [scripts] tags.sh: Ignore redhat/rpm (Prarit Bhargava) [1582586]
- [kernel] put RHEL info into generated headers (Prarit Bhargava) [1544999]
- [kernel] kdump: add support for crashkernel=auto (Dave Young) [1507353]
- [kernel] kdump: round up the total memory size to 128M for crashkernel reservation (Dave Young) [1507353]
- [arm64] acpi: prefer booting with ACPI over DTS (Mark Salter) [1576869]
- [acpi] aarch64: acpi scan: Fix regression related to X-Gene UARTs (Mark Salter) [1519554]
- [acpi] ACPI / irq: Workaround firmware issue on X-Gene based m400 (Mark Salter) [1519554]
- [x86] add rh_check_supported (David Arcari) [1565717]
- [scsi] qla2xxx: Remove PCI IDs of deprecated adapter (Himanshu Madhani) [1572233]
- [scsi] be2iscsi: remove unsupported device IDs (Chris Leech) [1574502]
- [scsi] Removing Obsolete hba pci-ids from rhel8 (Dick Kennedy) [1572321]
- [scsi] hpsa: modify hpsa driver version (Joseph Szczypek) [1471185]
- [scsi] hpsa: remove old cciss-based smartarray pci ids (Joseph Szczypek) [1471185]
- [kernel] rh_taint: add support for marking driver as unsupported (Jonathan Toppins) [1565704]
- [kernel] rh_taint: add support (David Arcari) [1565704]
- [scsi] qla4xxx: Remove deprecated PCI IDs from RHEL 8 (Chad Dupuis) [1518874]
- [scsi] aacraid: Remove depreciated device and vendor PCI id's (Raghava Aditya Renukunta) [1495307]
- [scsi] megaraid_sas: remove deprecated pci-ids (Tomas Henzl) [1509329]
- [scsi] mpt*: remove certain deprecated pci-ids (Tomas Henzl) [1511953]
- [kernel] modules: add rhelversion MODULE_INFO tag (Prarit Bhargava) [1544999]
- [acpi] ACPI: APEI: arm64: Ignore broken HPE moonshot APEI support (Al Stone) [1518076]
- [rpmspec] compute content hash for kernel-headers (Rafael Aquini) [1613003]
- [rpmspec] compress modules on all architectures ("Herton R. Krzesinski") [1614556]
- [rpmspec] add gcov rpm packaging support (Jan Stancek) [1601733]
- [rpmspec] don't ship spdxcheck.py (Jakub Racek)
- [rpmspec] clean stray bpf files (Jakub Racek) [1593309]
- [rpmspec] Copy symvers.gz to /lib/modules (Eugene Syromiatnikov) [1609695]
- [rpmspec] Add kabi-dup related code into specfile (Petr Oros) [1585672]
- [rpmspec] kernel spec: Add and enable kabi check (Petr Oros) [1585672]
- [rpmspec] Enable warning checks for configs in rpm build (Prarit Bhargava) [1589858]
- [rpmspec] remove workaround for rst2man-3 from python3-docutils ("Herton R. Krzesinski") [1602148]
- [rpmspec] fix dist tag used for hardlink in kernel-devel post ("Herton R. Krzesinski") [1596397]
- [scripts] get_maintainer.pl: Add optional .get_maintainer.MAINTAINERS override (Prarit Bhargava) [1595727]
- [rpmspec] drop kernel package dependency on python2 ("Herton R. Krzesinski") [1561505]
- [kernel] Makefile: Move RHEL definitions down (Jakub Racek) [1576568]
- [rpmspec] eBPF: Add bpftool package to spec file (Jerome Marchand) [1559607]
- [rpmspec] fix conflicts with COPYING file while installing newer 4.17 kernel ("Herton R. Krzesinski") [1579563]
- [rpmspec] do not build kernel meta-package on noarch ("Herton R. Krzesinski") [1579512]
- [rpmspec] kernel spec: remove copy of arch/x86/purgatory/sha256.* ("Herton R. Krzesinski")
- [rpmspec] spec: Add new arch/powerpc/kernel/module.lds file to kernel-devel rpm (Steve Best) [1572553]
- [rpmspec] kernel spec: fix recent build errors from brp-mangle-shebangs ("Herton R. Krzesinski") [1575966]
- [rpmspec] Add i386 to ExclusiveArch to fix noarch package build ("Herton R. Krzesinski") [1575152]
- [rpmspec] Build kernel-abi-whitelists package (Petr Oros) [1571189]
- [rpmspec] kernel spec: build bzImage for s390 (Hendrik Brueckner) [1570041]
- [rpmspec] kernel spec: arm64: package module.lds in kernel-devel (Mark Salter) [1569014]
- [rpmspec] Re-enable debuginfo packages and fix build with current dist tag ("Herton R. Krzesinski") [1568901]
- [rpmspec] kernel spec: build kernel-debug on all architectures ("Herton R. Krzesinski") [1567367]
- [rpmspec] don't build kernel meta-package if we are only building kernel headers ("Herton R. Krzesinski")
- [rpmspec] remove use_vdso macro ("Herton R. Krzesinski")
- [rpmspec] build perf and tools man pages instead of relying on a separate tarball ("Herton R. Krzesinski")
- [rpmspec] disable debug build if arch is in nobuildarches list ("Herton R. Krzesinski")
- [rpmspec] remove fedora changelog from spec file ("Herton R. Krzesinski")
- [rpmspec] only support ppc64le builds ("Herton R. Krzesinski")
- [rpmspec] remove x86 32-bit package support ("Herton R. Krzesinski")
- [rpmspec] remove arm 32-bit package support ("Herton R. Krzesinski")
- [rpmspec] remove configuration generation support from kernel spec file ("Herton R. Krzesinski")
- [rpmspec] remove broken out patches from kernel spec file ("Herton R. Krzesinski")
- [rpmspec] import kernel spec from rhel8 bootstrap dist-git ("Herton R. Krzesinski")

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
