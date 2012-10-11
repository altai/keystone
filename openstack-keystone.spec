%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%global with_doc 0
%global prj keystone
%global short_name openstack-keystone
%global os_release essex
%define mod_name keystone
%define py_puresitedir  %{python_sitelib}

Name:           openstack-%{prj}-%{os_release}
Epoch:          1
Release:        1 
Version:        2012.1
Url:            http://www.openstack.org
Summary:        Openstack Identity Service ESSEX
License:        Apache 2.0
Vendor:         Grid Dynamics Consulting Services, Inc.
Group:          Applications/System
Source0:        %{name}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel python-setuptools
%if 0%{?with_doc}
BuildRequires:  python-sphinx >= 0.6.0 make
%endif
BuildArch:      noarch

Conflicts:      %{short_name}
Requires:       start-stop-daemon
Requires:       python-keystone-%{os_release} = %{epoch}:%{version}-%{release}

%description
Authentication service - proposed for OpenStack.


%if 0%{?with_doc}

%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{epoch}:%{version}-%{release}


%description doc
Documentation for %{name}.

%endif

%package -n     python-keystone-%{os_release}
Summary:        Keystone Python libraries
Group:          Development/Languages/Python

Requires:       python-eventlet 
Requires:       python-lxml 
Requires:       python-paste 
Requires:       python-sqlalchemy 
Requires:       python-routes 
Requires:       python-httplib2 
Requires:       python-paste-deploy >= 1.5.0
Requires:       start-stop-daemon 
Requires:       python-webob 
Requires:       python-setuptools 
Requires:       python-passlib
Requires:       python-sqlalchemy-migrate
Requires:       python-keystone-%{os_release}

%description -n  python-keystone-%{os_release}
This package contains the %{name} Python library.

%prep
%setup -q -n %{name}-%{version}


%build
python setup.py build


%install
%__rm -rf %{buildroot}

%if 0%{?with_doc}
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc
sphinx-build -b html source build/html
popd

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

python setup.py install --prefix=%{_prefix} --root=%{buildroot}
#mv %{buildroot}/usr/bin/keystone{,-combined}

install -d -m 755 %{buildroot}%{_sysconfdir}/%{prj}
install -m 644 etc/* %{buildroot}%{_sysconfdir}/%{prj}
#install -m 644 examples/paste/nova-api-paste.ini %{buildroot}%{_sysconfdir}/%{prj}

install -d -m 755 %{buildroot}%{_sharedstatedir}/%{prj}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{prj}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{prj}

install -p -D -m 755 redhat/keystone.init %{buildroot}%{_initrddir}/keystone

%__rm -rf %{buildroot}%{py_puresitedir}/{doc,tools}


%clean
%__rm -rf %{buildroot}


%pre
getent passwd keystone >/dev/null || \
useradd -r -g nobody -G nobody -d %{_sharedstatedir}/%{prj} -s /sbin/nologin \
-c "OpenStack Keystone Daemon" %{prj}
exit 0


%preun
if [ $1 = 0 ] ; then
    /sbin/service %{prj} stop
    /sbin/chkconfig --del %{prj}
fi


%files
%defattr(-,root,root,-)
%doc README.rst HACKING.rst LICENSE
%{_usr}/bin/*
%config(noreplace) %{_sysconfdir}/%{prj}
%dir %attr(0755, keystone, nobody) %{_sharedstatedir}/%{prj}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/log/%{prj}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/run/%{prj}
%{_sysconfdir}/rc.d/init.d/*

%if 0%{?with_doc}
%files doc
%defattr(-,root,root,-)
%doc doc
%endif

%files -n python-keystone-%{os_release}
%defattr(-,root,root,-)
%doc LICENSE
%{py_puresitedir}/%{mod_name}*


%changelog
* Mon Mar  26 2012 Pavel Shkitin <pshkitin@griddynamics.com> - 2012.1
- Ported keystone on the essex-rc1 release

* Thu Mar  6 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 2011.3
- Separated keystone libraries of the others
