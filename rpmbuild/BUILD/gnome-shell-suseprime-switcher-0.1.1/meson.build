project('gnome-shell-suseprime-switcher',
  version: '0.1.0',
  meson_version: '>= 0.44.0',
  license: 'GPL2+'
)

gettext_domain = meson.project_name()

i18n = import('i18n')

datadir = get_option('datadir')

shelldir = join_paths(datadir, 'gnome-shell')
extensiondir = join_paths(shelldir, 'extensions')

js60 = find_program('js60', required: false)

uuid_suffix = '@hellcp.opensuse.org'
name = 'suseprimeswitcher'
uuid = name + uuid_suffix

extension_sources = files('suseprimeswitcher/extension.js',
'suseprimeswitcher/metadata.json',
'suseprimeswitcher/pkexec_intel',
'suseprimeswitcher/pkexec_nvidia',
'suseprimeswitcher/stylesheet.css')
extension_icons = files('suseprimeswitcher/icons/suseprime-intel-symbolic.svg',
'suseprimeswitcher/icons/suseprime-nvidia-symbolic.svg',
'suseprimeswitcher/icons/suseprime-symbolic.svg'
)

installdir = join_paths(extensiondir, uuid)

install_data (extension_sources,
  install_dir: installdir
)
install_data (extension_icons,
  install_dir: join_paths(installdir, 'icons')
)

subdir('po')

