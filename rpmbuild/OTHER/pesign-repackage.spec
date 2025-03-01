#!/bin/bash
# This specfile unpacks the original RPMs, runs pesign-gen-repackage-spec
# to create a second repackage specfile, and runs another rpmbuild to
# actually do the repackaging.
# 
# Copyright (c) 2013 SUSE Linux Products GmbH, Nuernberg, Germany.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA

# Do not generate any debug packages from the repackage specfile
%undefine _build_create_debug

Name:           pesign-repackage
Version:        1.0
Release:        1
BuildRequires:  openssl mozilla-nss-tools
%ifarch %ix86 x86_64 ia64
BuildRequires:  pesign
%endif
License:        GPL-2.0
Group:          Development/Tools/Other
Summary:        Spec file to rebuild RPMs with signatures
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%description
Rebuilds RPMs with signatures

%prep
%setup -c -T

%build

%install

# avoid loops
export BRP_PESIGN_FILES=""

pushd %buildroot
disturl=
rpms=()
for rpm in %_sourcedir/*.rpm; do
	case "$rpm" in
	*.src.rpm | *.nosrc.rpm)
		cp "$rpm" %_srcrpmdir/
		continue
		;;
	# Do not repackage debuginfo packages (bnc#806637)
	*-debuginfo-*.rpm | *-debugsource-*.rpm)
		mkdir -p "%_topdir/OTHER"
		cp "$rpm" "$_"
		continue
		;;
	esac
	# do not repackage baselibs packages
	# FIXME: needs more generic test (if architecture has different
	# bitness => skip)
	case "$(rpm -qp --qf '%%{name}/%%{arch}' "$rpm")" in
	*-32bit/x86_64 | *-32bit/s390x | *-32bit/ppc64 | \
	*-64bit/ppc | *-x86/ia64)
		mkdir -p "%_topdir/OTHER"
		cp "$rpm" "$_"
		continue
	esac
	rpm2cpio "$rpm" | cpio -idm
	d=$(rpm -qp --qf '%%{disturl}' "$rpm")
	if test -z "$disturl"; then
		disturl=$d
	fi
	if test "$disturl" != "$d"; then
		echo "Error: packages have different disturl: $d vs $disturl"
		exit 1
	fi
	rpms=("${rpms[@]}" "$rpm")
done
popd
# Copy files other than the meta files and RPMs to %_topdir/OTHER
OTHER_FILES=`find %_sourcedir/ -maxdepth 1 -type f \
	-not -regex '.*\.\(rpm\|spec\|rsasign\|sig\|crt\)' \
	-not -name "_buildenv" \
	-not -name "_statistics" \
	-not -name "logfile" \
	-not -name "meta" \
	-print`
for file in $OTHER_FILES; do
	if test -e "$file"; then
		mkdir -p "%_topdir/OTHER"
		cp "$file" "$_"
	fi
done
mkdir rsasigned
pushd rsasigned
cpio -idm <%_sourcedir/gnome-shell-suseprime-switcher.cpio.rsasign.sig
cat >cert.crt <<EOF
EOF
if test "$(wc -l <cert.crt)" -le 1 -a -s %_sourcedir/_projectcert.crt ; then
	cp %_sourcedir/_projectcert.crt cert.crt
fi
if test "$(wc -l <cert.crt)" -gt 1; then
	openssl x509 -inform PEM -in cert.crt -outform DER -out cert.x509
	cert=cert.x509
else
	echo "warning: No buildservice project certificate found, add"
	echo "warning: # needssslcertforbuild to the specfile"
	echo "warning: Using /usr/lib/rpm/pesign/pesign-cert.x509 as fallback"
	cert=/usr/lib/rpm/pesign/pesign-cert.x509
fi
mkdir nss-db
nss_db=$PWD/nss-db
echo foofoofoo > "$nss_db/passwd"
certutil -N -d "$nss_db" -f "$nss_db/passwd"
certutil -A -d "$nss_db" -f "$nss_db/passwd" -n cert -t CT,CT,CT -i "$cert"

sigs=($(find -type f -name '*.sig' -printf '%%P\n'))
for sig in "${sigs[@]}"; do
	f=%buildroot/${sig%.sig}
	case "/$sig" in
	*.ko.sig)
		/usr/lib/rpm/pesign/kernel-sign-file -i pkcs7 -s "$sig" sha256 "$cert" "$f"
		;;
	/boot/* | *.efi.sig | */lib/modules/*/vmlinu[xz].sig | */lib/modules/*/[Ii]mage.sig | */lib/modules/*/z[Ii]mage.sig)
%ifarch %ix86 x86_64 aarch64 %arm
		# PE style signature injection
		infile=${sig%.sig}
		cpio -i --to-stdout ${infile#./} <%_sourcedir/gnome-shell-suseprime-switcher.cpio.rsasign > ${infile}.sattrs
		test -s ${infile}.sattrs || exit 1
		ohash=$(pesign -n "$nss_db" -h -P -i "$f")
		pesign -n "$nss_db" -c cert -i "$f" -o "$f.tmp" -d sha256 -I "${infile}.sattrs" -R "$sig"
		rm -f "${infile}.sattrs"
		mv "$f.tmp" "$f"
		nhash=$(pesign -n "$nss_db" -h -P -i "$f")
		if test "$ohash" != "$nhash" ; then
		    echo "hash mismatch error: $ohash $nhash"
		    exit 1
		fi
%else
		# appending to the file itself, e.g. for s390x.
		/usr/lib/rpm/pesign/kernel-sign-file -i pkcs7 -s "$sig" sha256 "$cert" "$f"
%endif
		# Regenerate the HMAC if it exists
		hmac="${f%%/*}/.${f##*/}.hmac"
		if test -e "$hmac"; then
			/usr/lib/rpm/pesign/gen-hmac -r %buildroot "/${sig%.sig}"
		fi
		;;
	*stage3.bin.sig)
		/usr/lib/rpm/pesign/kernel-sign-file -i pkcs7 -s "$sig" sha256 "$cert" "$f"
		;;
	*)
		echo "Warning: unhandled signature: $sig" >&2
	esac
done
popd
/usr/lib/rpm/pesign/pesign-gen-repackage-spec  \
	--directory=%buildroot "${rpms[@]}"
rpmbuild --define "%%buildroot %buildroot" --define "%%disturl $disturl" \
	 --define "%%_builddir $PWD" \
	 --define "%_suse_insert_debug_package %%{nil}" -bb repackage.spec

# This is needed by the kernel packages. Ideally, we should not run _any_ brp
# checks, because the RPMs passed them once already
export NO_BRP_STALE_LINK_ERROR=yes

# Make sure that our rpmbuild does not complain about unpackaged files
rm -rf %buildroot
mkdir %buildroot

