# Share docs between packages for multiple python versions
%global _docdir_fmt %{name}

Summary:	Cryptography library for Python
Name:		python-crypto
Version:	2.6.1
Release:	31
# Mostly Public Domain apart from parts of HMAC.py and setup.py, which are Python
License:	Public Domain and Python
URL:		http://www.pycrypto.org/
Source0:	http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-%{version}.tar.gz
Patch0:		python-crypto-2.4-optflags.patch
Patch1:		python-crypto-2.4-fix-pubkey-size-divisions.patch
Patch2:		pycrypto-2.6.1-CVE-2013-7459.patch
Patch3:		pycrypto-2.6.1-unbundle-libtomcrypt.patch
Patch4:		python-crypto-2.6.1-link.patch
Patch5:		pycrypto-2.6.1-CVE-2018-6594.patch
Patch6:		pycrypto-2.6.1-use-os-random.patch
Patch7:		pycrypto-2.6.1-drop-py2.1-support.patch
Patch8:   python-crypto-2.6.1-python3.11.patch
BuildRequires:	coreutils
BuildRequires:	findutils
BuildRequires:	pkgconfig(gmp)
BuildRequires:	pkgconfig(libtomcrypt)
BuildRequires:	pkgconfig(python3)
BuildRequires:	%{_bindir}/2to3
%rename python3-crypto

%description
PyCrypto is a collection of both secure hash functions (such as MD5 and
SHA), and various encryption algorithms (AES, DES, RSA, ElGamal, etc.).

%prep
%setup -n pycrypto-%{version} -q

# Use distribution compiler flags rather than upstream's
%patch0 -p1

# Fix divisions within benchmarking suite:
%patch1 -p1

# AES.new with invalid parameter crashes python
# https://github.com/dlitz/pycrypto/issues/176
# CVE-2013-7459
%patch2 -p1

# Unbundle libtomcrypt (#1087557)
rm -rf src/libtom
%patch3

# log() not available in libgmp, need libm too
%patch4

# When creating ElGamal keys, the generator wasn't a square residue: ElGamal
# encryption done with those keys cannot be secure under the DDH assumption
# https://bugzilla.redhat.com/show_bug.cgi?id=1542313 (CVE-2018-6594)
# https://github.com/TElgamal/attack-on-pycrypto-elgamal
# https://github.com/Legrandin/pycryptodome/issues/90
# https://github.com/dlitz/pycrypto/issues/253
# Patch based on this commit from cryptodome:
# https://github.com/Legrandin/pycryptodome/commit/99c27a3b
# Converted to pull request for pycrypto:
# https://github.com/dlitz/pycrypto/pull/256
%patch5

# Replace the user-space RNG with a thin wrapper to os.urandom
# Based on https://github.com/Legrandin/pycryptodome/commit/afd6328f
# Fixes compatibility with Python 3.8 (#1718332)
%patch6

# We already require Python 2.4 or later, so drop support for Python 2.1
# in the code
%patch7

%patch8

# setup.py doesn't run 2to3 on pct-speedtest.py
cp pct-speedtest.py pct-speedtest3.py
2to3 -wn pct-speedtest3.py

%build
%global optflags %{optflags} -fno-strict-aliasing
%py3_build

%install
%py3_install

# Remove group write permissions on shared objects
find %{buildroot}%{python_sitearch} -name '*.so' -exec chmod -c g-w {} \;

# Benchmark
PYTHONPATH=%{buildroot}%{python3_sitearch} python pct-speedtest3.py

%files
%license COPYRIGHT LEGAL/
%doc README TODO ACKS ChangeLog Doc/
%{python_sitearch}/Crypto/
%{python_sitearch}/pycrypto-%{version}-py3.*.egg-info
