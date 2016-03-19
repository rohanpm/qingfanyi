Name:    qt-at-spi
Version: 0.4.0
Release: 1%{?dist}
Summary: Qt plugin that bridges Qt's accessibility API to AT-SPI2 

License: LGPLv2+
URL:     https://github.com/KDE/qtatspi
Source0: %{name}-%{version}.tar.gz

# https://git.reviewboard.kde.org/r/127429/
Patch1: 0001-Fix-compile.patch

# https://git.reviewboard.kde.org/r/127430/
Patch2: 0002-Fix-signature-of-getRangeExtents.patch

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires: pkgconfig(atspi-2)
BuildRequires: pkgconfig(QtDBus) >= 4.8.0
BuildRequires: pkgconfig(QtGui) pkgconfig(QtXml)
BuildRequires: cmake
BuildRequires: kdelibs-devel

%{?_qt4:Requires: %{_qt4}%{?_isa} >= %{_qt4_version}}

%description
This is a Qt plugin that bridges Qt's accessibility API to AT-SPI2.
With recent versions of AT-SPI2 this should make Qt applications accessible
with the help of tools such as Gnome's Orca screen-reader.

%package doc
Summary: Documentation for %{name}
BuildArch: noarch
%description doc
%{summary}.


%prep
%setup -q -n qtatspi-%{version}
%patch1 -p1
%patch2 -p1


%build
%cmake .
make %{?_smp_mflags}

# build docs
pushd doc
qdoc3 qatspi.qdocconf
popd


%install
make install DESTDIR=%{buildroot}


%files
%doc LICENSE README
%dir %{_qt4_plugindir}/accessiblebridge/
%{_qt4_plugindir}/accessiblebridge/libqspiaccessiblebridge.so

%files doc
# install these under %{_qt4_docdir}? --rex
%doc doc/html/*


%changelog
* Sun Mar 19 2016 Rohan McGovern <rohan@mcgovern.id.au> - 0.4.0-1
- 0.4.0, with patches to fix character/range extents

* Wed Feb 03 2016 Rex Dieter <rdieter@fedoraproject.org> - 0.3.1-10
- use %%qmake_qt4 macro to ensure proper build flags

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 0.3.1-8
- Rebuilt for GCC 5 C++11 ABI change

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Nov 15 2012 Rex Dieter <rdieter@fedoraproject.org> 0.3.1-3
- include sample qt-at-spi.sh shell fragment

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 16 2012 Jaroslav Reznik <jreznik@redhat.com> 0.3.1-1
- 0.3.1, fixes accessing invalid objects

* Thu Apr 12 2012 Rex Dieter <rdieter@fedoraproject.org> 0.3.0-1
- 0.3.0

* Tue Apr 03 2012 Rex Dieter <rdieter@fedoraproject.org> 0.2-2
- License: LGPLv2+
- -doc subpkg

* Wed Mar 14 2012 Rex Dieter <rdieter@fedoraproject.org> 0.2-1
- 0.2

* Thu Jan 05 2012 Rex Dieter <rdieter@fedoraproject.org> 0.1.1-1
- 0.1.1

* Tue Nov 15 2011 Rex Dieter <rdieter@fedoraproject.org> 0.1-1
- 0.1 release

* Tue Oct 25 2011 Rex Dieter <rdieter@fedoraproject.org> 0.0-0.1.20111025
- first try


