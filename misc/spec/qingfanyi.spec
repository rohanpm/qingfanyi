%global srcname qingfanyi
%global sum Interactive Chinese to English dictionary lookup tool
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

Name:           qingfanyi
Version:        1.1.0
Release:        1%{?dist}
Summary:        %{sum}

License:        GPLv3+
URL:            https://github.com/rohanpm/%{srcname}
Source0:        http://example.com/%{srcname}-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

Requires:       python2-ewmh
Requires:       python2-marisa-trie
Requires:       pyatspi
Requires:       pygobject3-base

%description
An interactive Chinese to English dictionary lookup tool.

It uses accessibility support to extract Chinese text from the active window and
provide Chinese translations in a popup.

%prep
%autosetup -n %{srcname}-%{version}

%build
%py2_build

%install
%py2_install

%files
%license LICENSE.GPL
%doc README.md
%{python2_sitelib}/*
/usr/bin/qfy

%changelog
* Sun Mar 20 2016 Rohan McGovern <rohan@mcgovern.id.au> - 1.1.0-1
- Version 1.1.0
