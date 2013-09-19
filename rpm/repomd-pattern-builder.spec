# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.25
# 

Name:       repomd-pattern-builder

# >> macros
# << macros

Summary:    Scripts to build patterns for the rpm repository.
Version:    0.3
Release:    1
Group:      Software Management/Package Manager
License:    GPLv2
URL:        https://gitorious.org/meego-developer-edition-for-n900/repomd-pattern-builder
Source0:    %{name}-%{version}.tar.xz
Source100:  repomd-pattern-builder.yaml
Requires:   python
Requires:   python-yaml
Requires:   python-lxml
Requires:   /usr/bin/xmllint

%description
Script that converts .yaml structures to suitable rpm patterns and package groups.


%package tests
Summary:    tests for %{name}
Group:      QA/Tests
Requires:   %{name} = %{version}-%{release}
Requires:   diffutils

%description tests
%{summary}.



%prep
%setup -q -n %{name}-%{version}

# >> setup
# << setup

%build
# >> build pre
# << build pre



# >> build post
# << build post

%install
rm -rf %{buildroot}
# >> install pre
%make_install
# << install pre

# >> install post
# << install post


%files
%defattr(-,root,root,-)
# >> files
%{_bindir}/%{name}.py
# << files

%files tests
%defattr(-,root,root,-)
# >> files tests
/opt/tests/repomd-pattern-builder/tests.xml
/opt/tests/repomd-pattern-builder/data/*
# << files tests
