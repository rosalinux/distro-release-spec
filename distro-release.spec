# Please update release notes:
# make -C SOURCES release-notes.{html,txt}
#

%{python:import distro}
%define am_i_cooker 1
%if %am_i_cooker
%define distrib Cooker
%else
%define distrib Official
%endif
%define version 2013.0
%if "%{disttag}" == "omv"
%define distname Beta (Oxygen)
%else
%define distname Beta (Twelve Angry Penguins)
%endif
%define _distribution %(echo %{distribution} | tr A-Z a-z |sed -e 's#[ /()!?]#_#g')

%define product_vendor %{vendor}
%define product_distribution %{distribution}
%define product_type Basic
%define product_version %{version}
%if %am_i_cooker
%define product_branch Devel
%else
%define product_branch Official
%endif
%define product_release 1
%define product_arch %{_target_cpu}

%define product_id_base vendor=%product_vendor,distribution=%product_distribution,type=%product_type,version=%product_version,branch=%product_branch,release=%product_release,arch=%product_arch

%if %am_i_cooker
    %define unstable %%_with_unstable --with-unstable
%endif

# The mandriva release, what is written on box
%define mandriva_release %{version}

# The mandriva branch: Cooker, Community or Official
%define mandriva_branch %{distrib}

# The mandriva arch, notice: using %_target_cpu is bad
# elsewhere because this depend of the config of the packager
# _target_cpu => package build for
# mandriva_arch => the distribution we are using
%define mandriva_arch %{_target_cpu}

# To be coherent with %mandriva_arch I provide os too
# be I wonder it will be linux for a long time
%define mandriva_os %{_target_os}

%define realversion %{version}
%define mdkver %(echo %{version} | sed 's/\\.//')0

Summary:	%{distribution} release file
Name:		distro-release
Version:	2013.0
Release:	0.15
Epoch:		1
License:	GPLv2+
URL:		%{disturl}
Group:		System/Configuration/Other
Source0:	%{name}.tar.xz
Source3:	CREDITS
# edited lynx -dump of wiki:
Source4:	release-notes.txt
Source5:	release-notes.html

%description
%{distribution} release file.

%package	common
Summary:	%{distribution} release common files
Group:		System/Configuration/Other
Conflicts:	%{name} < %{version}-%{release}
Obsoletes:	mandriva-release-Discovery
Obsoletes:	mandriva-release-Powerpack+
Obsoletes:	%{name} < %{version}-%{release}
Obsoletes:	rawhide-release
Obsoletes:	redhat-release
Obsoletes:	mandrake-release
Obsoletes:	mandrakelinux-release
%rename		rosa-release-common
%rename		mandriva-release-common
%rename		opemandriva-release-common
%rename		mandriva-release-Free
%rename		mandriva-release-One
%rename		mandriva-release-Powerpack
%rename		mandriva-release-Mini
%rename		openmandriva-release-Free
%rename		openmandriva-release-One
%rename		openmandriva-release-Powerpack
%rename		openmandriva-release-Mini
# (tpg) older releases provides %{_sysconfdir}/os-release
Conflicts:	systemd < 37-5
Requires:	lsb-release

# cf mdvbz#32631
Provides:	arch(%_target_cpu)
Provides:	%arch_tagged %{_vendor}-release-common

%description	common
Common files for %{distribution} release packages.



%{python:distro.release_package("Moondrake")}
%{python:distro.release_package("OpenMandriva")}

%prep
%setup -q -n %{name}


cp -a %{SOURCE3} CREDITS
cp -a %{SOURCE4} release-notes.txt
cp -a %{SOURCE5} release-notes.html

cat > README.urpmi << EOF
This is %{distribution} %{version}

You can find the release notes in %{_docdir}/%{name}-common/release-notes.txt

or on the web at http://wiki.%{_vendor}.com/en/%{version}_Notes
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


echo "Moondrake GNU/Linux release %{realversion} %{distname} for %{_target_cpu}" > %{buildroot}%{_sysconfdir}/moondrake-release
echo "OpenMandriva LX release %{realversion} %{distname} for %{_target_cpu}" > %{buildroot}%{_sysconfdir}/openmandriva-release
ln -sf release %{buildroot}%{_sysconfdir}/mandriva-release
ln -sf release %{buildroot}%{_sysconfdir}/redhat-release
ln -sf release %{buildroot}%{_sysconfdir}/mandrake-release
ln -sf release %{buildroot}%{_sysconfdir}/mandriva-release
ln -sf release %{buildroot}%{_sysconfdir}/mandrakelinux-release
ln -sf release %{buildroot}%{_sysconfdir}/rosa-release
ln -sf release %{buildroot}%{_sysconfdir}/system-release

echo "%{version}.0 %{release} %{distname}" > %{buildroot}%{_sysconfdir}/version

# (tpg) follow standard specifications http://0pointer.de/blog/projects/os-release
cat > %{buildroot}%{_sysconfdir}/os-release << EOF
NAME="%{distribution}"
VERSION="%{realversion} %{distname}"
ID=%{_vendor}
VERSION_ID=%{realversion}
PRETTY_NAME="%{distribution} %{realversion} %{distname}"
ANSI_COLOR="1;43"
CPE_NAME="cpe:/o:%{_vendor}:%{_distribution}:%{realversion}"
HOME_URL="%{disturl}"
BUG_REPORT_URL="%{bugurl}"
EOF

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

%{python:distro.release_install("Moondrake GNU/Linux", "Moondrake", "Moondrake")}
%{python:distro.release_install("OpenMandriva LX", "OpenMandriva", "OpenMandriva")}


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

%files common
%doc CREDITS distro.txt README.urpmi release-notes.*
%ghost %{_sysconfdir}/product.id
%{_sysconfdir}/*-release
%{_sysconfdir}/version
%{_sysconfdir}/profile.d/10distro-release.sh
%{_sysconfdir}/profile.d/10distro-release.csh
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/system
