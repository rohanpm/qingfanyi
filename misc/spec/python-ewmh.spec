%global srcname ewmh
%global sum python implementation of Extended Window Manager Hints, based on Xlib
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

Name:           python-%{srcname}
Version:        0.1.3
Release:        2%{?dist}
Summary:        %{sum}

License:        LGPLv3+
URL:            http://pypi.python.org/pypi/%{srcname}
Source0:        http://pypi.python.org/packages/source/m/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

%description
An implementation of EWMH (Extended Window Manager Hints) for python, based on Xlib.

It allows EWMH-compliant window managers (most modern WMs) to be queried and controlled.

%package -n python2-%{srcname}
Summary:        %{sum}
Requires:       python-xlib
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
An implementation of EWMH (Extended Window Manager Hints) for python, based on Xlib.

It allows EWMH-compliant window managers (most modern WMs) to be queried and controlled.

%prep
%autosetup -n %{srcname}-%{version}

%build
%py2_build

%install
%py2_install

%check
%{__python2} setup.py test

%files -n python2-%{srcname}
%license LICENSE.txt
%doc README.rst
%{python2_sitelib}/*

%changelog
