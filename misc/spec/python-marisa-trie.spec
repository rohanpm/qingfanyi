%global srcname marisa-trie
%global sum Static memory-efficient & fast Trie-like structures for Python (based on marisa-trie C++ library)

Name:           python-%{srcname}
Version:        0.7.2
Release:        1%{?dist}
Summary:        %{sum}

License:        MIT
URL:            http://pypi.python.org/pypi/%{srcname}
Source0:        http://pypi.python.org/packages/source/m/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

%description
Static memory-efficient Trie-like structures for Python (2.x and 3.x).

String data in a MARISA-trie may take up to 50x-100x less memory than in a standard Python
dict; the raw lookup speed is comparable; trie also provides fast advanced methods like
prefix search.

Based on marisa-trie C++ library.

%package -n python2-%{srcname}
Summary:        %{sum}
%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
Static memory-efficient Trie-like structures for Python (2.x and 3.x).

String data in a MARISA-trie may take up to 50x-100x less memory than in a standard Python
dict; the raw lookup speed is comparable; trie also provides fast advanced methods like
prefix search.

Based on marisa-trie C++ library.

%prep
%autosetup -n %{srcname}-%{version}

%build
%py2_build

%install
%py2_install

%check
%{__python2} setup.py test

%files -n python2-%{srcname}
%license LICENSE
%doc README.rst
%{python2_sitearch}/*

%changelog
