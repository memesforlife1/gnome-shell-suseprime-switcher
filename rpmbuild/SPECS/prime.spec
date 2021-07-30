#
# spec file for package gnome-shell-suseprime-switcher
#
# Copyright (c) 2019 Stasiek Michalski <hellcp@opensuse.org>.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%define _appid  suseprimeswitcher@hellcp.opensuse.org

Name:           gnome-shell-suseprime-switcher
Version:        0.1.1
Release:        0
Summary:        Gnome Shell extension for switching between GPUs. All Credits to the Opensuse team for making the original package. This is the Git Link to the original Package, https://github.com/openSUSE/gnome-shell-suseprime-switcher
Group:          System/GUI/GNOME
License:        GPL-2.0
Url:            https://github.com/memesforlife1/%{name}
Source0:        %{url}/archive/refs/tags/%{name-}%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  ninja
BuildRequires:  gnome-shell
Requires:       gnome-shell
Supplements:    (gnome-shell and suse-prime)

%description
Gnome Shell extension for switching between GPUs.

%prep
%setup -q

%build
%meson
%meson_build

%install
%meson_install

%find_lang %{name}

%files -f %{name}.lang
%dir %{_datadir}/gnome-shell/extensions/%{_appid}/
%{_datadir}/gnome-shell/extensions/%{_appid}/extension.js
%dir %{_datadir}/gnome-shell/extensions/%{_appid}/icons/
%{_datadir}/gnome-shell/extensions/%{_appid}/icons/suseprime-intel-symbolic.svg
%{_datadir}/gnome-shell/extensions/%{_appid}/icons/suseprime-nvidia-symbolic.svg
%{_datadir}/gnome-shell/extensions/%{_appid}/icons/suseprime-symbolic.svg
%{_datadir}/gnome-shell/extensions/%{_appid}/metadata.json
%{_datadir}/gnome-shell/extensions/%{_appid}/pkexec_intel
%{_datadir}/gnome-shell/extensions/%{_appid}/pkexec_nvidia
%{_datadir}/gnome-shell/extensions/%{_appid}/stylesheet.css

%changelog
