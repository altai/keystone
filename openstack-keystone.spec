%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%global with_doc 0
%global prj keystone
%define mod_name keystone
%define py_puresitedir  %{python_sitelib}

Name:           openstack-keystone
Epoch:          1
Version:        2012.1
Release:        1
Url:            http://www.openstack.org
Summary:        Openstack Identity Service
License:        Apache 2.0
Vendor:         Grid Dynamics Consulting Services, Inc.
Group:          Applications/System

Source0:          %{name}-%{version}.tar.gz

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}

BuildArch:        noarch
BuildRequires:    python-devel
BuildRequires:    python-setuptools
BuildRequires:    intltool

Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils
Requires:         python-%{prj} = %{epoch}:%{version}-%{release}
Requires:         start-stop-daemon

Obsoletes:        %{name}-essex

%description
Keystone is a Python implementation of the OpenStack
(http://www.openstack.org) identity service API.

This package contains the Keystone daemon.


%if 0%{?with_doc}

%package doc
Summary:          Documentation for %{name}
Group:            Documentation
Requires:         %{name} = %{epoch}:%{version}-%{release}
Obsoletes:        %{name}-essex-doc

%description doc
Keystone is a Python implementation of the OpenStack
(http://www.openstack.org) identity service API.

This package contains documentation for Keystone.

%endif


%package -n     python-keystone
Summary:        Keystone Python libraries
Group:          Development/Languages/Python

Requires:         PyPAM
Requires:         python-webob==1.0.8
Requires:         python-eventlet
Requires:         python-greenlet
Requires:         python-paste-deploy
Requires:         python-paste
Requires:         python-routes
Requires:         python-sqlalchemy
Requires:         python-migrate
Requires:         python-passlib
Requires:         python-lxml

Obsoletes:        python-keystone-essex

%description -n  python-keystone
Keystone is a Python implementation of the OpenStack
(http://www.openstack.org) identity service API.

This package contains the Keystone Python library.

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

%files -n python-keystone
%defattr(-,root,root,-)
%doc LICENSE
%{py_puresitedir}/%{mod_name}*


%changelog
* Mon Oct 15 2012 Alessio Ababilov <aababilov@griddynamics.com> - 2011.3
- Cleanup the spec

* Mon Mar  26 2012 Pavel Shkitin <pshkitin@griddynamics.com> - 2012.1
- Ported keystone on the essex-rc1 release

* Thu Mar  6 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 2011.3
- Separated keystone libraries of the others
