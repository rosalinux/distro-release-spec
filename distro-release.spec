# Please update release notes:
# make -C SOURCES release-notes.{html,txt}
#

%{python:import sys; sys.path.append(rpm.expandMacro("%{_sourcedir}"))}
%{python:import distro}
%define am_i_cooker 0
%if %am_i_cooker
%define distrib Cooker
%else
%define distrib Official
%endif
%define _distribution %(echo %{distribution} | tr A-Z a-z |sed -e 's#[ /()!?]#_#g')
%define product_type Basic
%if %am_i_cooker
%define product_branch Devel
%else
%define product_branch Official
%endif
%define product_release 1
%define product_arch %{_target_cpu}

# The Distribution release, what is written on box
%define distro_release %{version}

# The distro branch: Cooker, Community or Official
%define distro_branch %{distrib}

# The distro arch, notice: using %_target_cpu is bad
# elsewhere because this depend of the config of the packager
# _target_cpu => package build for
# distro_arch => the distribution we are using
%define distro_arch %{_target_cpu}

%define major %(printf %u 0%(echo %{version}|cut -d. -f1))
%define minor %(printf %u 0%(echo %{version}|cut -d. -f2))
%define subminor %(printf %u 0%(echo %{version}|cut -d. -f3))
%define mdkver %(echo $((%{major}*1000000+%{minor}*1000+%{subminor})))

Summary:	%{distribution} release file
Name:		distro-release
# Ugly, but needed for 2015.0 -> 3.0 transition
Epoch:		2
Version:	3.0
DistEpoch:	2015.0
Release:	9
License:	GPLv2+
URL:		%{disturl}
Group:		System/Configuration/Other
Source0:	%{name}.tar.xz
Source1:	distro.py
Source2:	%{name}.rpmlintrc
Source3:	CREDITS
# edited lynx -dump of wiki:
Source4:	release-notes.txt
# raw output of lynx -source of wiki:
Source5:	release-notes.html

%description
%{distribution} release file.

%package	common
Summary:	%{distribution} release common files
Group:		System/Configuration/Other
%rename		rosa-release-common
%rename		mandriva-release-common
%rename		opemandriva-release-common
%rename		moondrake-release-common
%rename		mandriva-release
%rename		mandriva-release-Free
%rename		mandriva-release-One
%rename		mandriva-release-Powerpack
%rename		mandriva-release-Mini
# (tpg) older releases provides %{_sysconfdir}/os-release
Conflicts:	systemd < 37-5
Requires:	lsb-release
Requires(pre):	util-linux
# (cb) attempt workaround to prevent problems with chroot ordering
Requires(pre):	bash

# cf mdvbz#32631
Provides:	arch(%{_target_cpu})
Provides:	%{arch_tagged distro-release-common}

# (tpg) get rid of it
Obsoletes:	distro-release-Moondrake

%description	common
Common files for %{distribution} release packages.

# build release flavour rpm
%{python:distro.release_package("OpenMandriva Lx", "OpenMandriva", Prio=12)}

%prep
%setup -q -n %{name}
cp -a %{SOURCE3} CREDITS
cp -a %{SOURCE4} release-notes.txt
cp -a %{SOURCE5} release-notes.html

cat > README.urpmi << EOF
This is %{distribution} %{version}

You can find the release notes in %{_docdir}/%{name}-common/release-notes.txt

or on the web at %{disturl}
EOF

# check that CREDITS file is in UTF-8, fail otherwise
if iconv -f utf-8 -t utf-8 < CREDITS > /dev/null
then
	true
else
	echo "the CREDITS file *MUST* be encoded in UTF-8"
	echo "please fix it before continuing"
	false
fi

%install
mkdir -p %{buildroot}%{_sysconfdir}
touch %{buildroot}%{_sysconfdir}/product.id
touch %{buildroot}%{_sysconfdir}/os-release
touch %{buildroot}%{_sysconfdir}/release
touch %{buildroot}%{_sysconfdir}/version

ln -sf release %{buildroot}%{_sysconfdir}/mandriva-release
ln -sf release %{buildroot}%{_sysconfdir}/redhat-release
ln -sf release %{buildroot}%{_sysconfdir}/mandrake-release
ln -sf release %{buildroot}%{_sysconfdir}/mandriva-release
ln -sf release %{buildroot}%{_sysconfdir}/mandrakelinux-release
ln -sf release %{buildroot}%{_sysconfdir}/rosa-release
ln -sf release %{buildroot}%{_sysconfdir}/system-release

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat > %{buildroot}%{_sysconfdir}/profile.d/10distro-release.csh << EOF
if ( -r %{_sysconfdir}/sysconfig/system ) then
    eval `sed 's|^#.*||' %{_sysconfdir}/sysconfig/system | sed 's|\([^=]*\)=\([^=]*\)|set \1=\2|g' | sed 's|$|;|' `
    setenv META_CLASS $META_CLASS
else
    setenv META_CLASS unknown
endif
EOF

cat > %{buildroot}%{_sysconfdir}/profile.d/10distro-release.sh << EOF
if [ -r %{_sysconfdir}/sysconfig/system ]; then
    . %{_sysconfdir}/sysconfig/system
    export META_CLASS
else
    export META_CLASS=unknown
fi
EOF

# (tpg) use codename from here https://wiki.openmandriva.org/en/Codename
%{python:distro.release_install("OpenMandriva Lx", "OpenMandriva", "OpenMandriva", "(Einsteinium)", "http://openmandriva.org", "https://issues.openmandriva.org", "omv", ansiColor="1;43")}

%check
%if %{am_i_cooker}
case %{release} in
    0.*) ;;
    *)
    echo "Cooker distro should have this package with release < %{mkrel 1}"
    exit 1
    ;;
esac
%endif

%pre common
if [ $1 -ge 2 ]; then
    [ -f %{_sysconfdir}/product.id ] && rm %{_sysconfdir}/product.id
    [ -f %{_sysconfdir}/os-release ] && rm %{_sysconfdir}/os-release
    [ -f %{_sysconfdir}/release ] && rm %{_sysconfdir}/release
    [ -f %{_sysconfdir}/version ] && rm %{_sysconfdir}/version
    exit 0
fi

%files common
%doc CREDITS distro.txt README.urpmi release-notes.*
%ghost %{_sysconfdir}/product.id
%ghost %{_sysconfdir}/os-release
%ghost %{_sysconfdir}/release
%ghost %{_sysconfdir}/version
%{_sysconfdir}/redhat-release
%{_sysconfdir}/mandrake-release
%{_sysconfdir}/mandriva-release
%{_sysconfdir}/mandrakelinux-release
%{_sysconfdir}/rosa-release
%{_sysconfdir}/system-release
%{_sysconfdir}/profile.d/10distro-release.sh
%{_sysconfdir}/profile.d/10distro-release.csh
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/system
