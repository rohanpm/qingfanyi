%global srcname qingfanyi
%global sum Interactive Chinese to English dictionary lookup tool
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

Name:           qingfanyi
Version:        1.2.1
Release:        1%{?dist}
Summary:        %{sum}

License:        GPLv3+
URL:            https://github.com/rohanpm/%{srcname}
Source0:        https://github.com/rohanpm/%{srcname}/archive/v%{version}.tar.gz

BuildRequires: python3-pyatspi
BuildRequires: python3-gobject-base
BuildRequires: python3-marisa
BuildRequires: keybinder3

Requires: python3-pyatspi
Requires: python3-gobject-base
Requires: python3-marisa
Requires: keybinder3

%description
An interactive Chinese to English dictionary lookup tool.

It uses accessibility support to extract Chinese text from the active window and
provide Chinese translations in a popup.

%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build

%check
%{__python3} -m pytest -v

%install
%py3_install

%files
%license LICENSE.GPL
%doc README.md
%{python3_sitelib}/qingfanyi/
%{python3_sitelib}/qingfanyi-*.egg-info/
/usr/bin/qfy

%changelog
* Sun Apr 10 2016 Rohan McGovern - 1.2.1-1
- Version 1.2.1
- [issue #22] fix wrapping problem in keyboard navigation

* Sun Apr 3 2016 Rohan McGovern <rohan@mcgovern.id.au> - 1.2.0-1
- Version 1.2.0

* Sun Mar 20 2016 Rohan McGovern <rohan@mcgovern.id.au> - 1.1.0-1
- Version 1.1.0
