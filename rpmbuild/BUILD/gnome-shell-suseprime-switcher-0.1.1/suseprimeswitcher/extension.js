
const St = imports.gi.St;
const Main = imports.ui.main;
const GLib = imports.gi.GLib;
const PopupMenu = imports.ui.popupMenu;
const PanelMenu = imports.ui.panelMenu;
const Lang = imports.lang;
const Gio = imports.gi.Gio;
const Util = imports.misc.util;
const Me = imports.misc.extensionUtils.getCurrentExtension();

const Gettext = imports.gettext.domain('gnome-shell-suseprime-switcher');
const _ = Gettext.gettext;

let button;

const SusePrimeSwitcher = new Lang.Class({
	Name: 'SUSEPrimeSwitcher',
	Extends: PanelMenu.Button,

	_init: function() {

		this.parent(1, 'SUSEPrimeSwitcher', false);

		let nvidiaicon =	Gio.icon_new_for_string(Me.path + '/icons/suseprime-nvidia-symbolic.svg');
		let intelicon =	Gio.icon_new_for_string(Me.path + '/icons/suseprime-intel-symbolic.svg');
		let primeicon =	Gio.icon_new_for_string(Me.path + '/icons/suseprime-symbolic.svg');
		let currentType;
		if (GLib.file_test('/etc/prime/current_type', GLib.FileTest.EXISTS)){
			currentType = String(GLib.file_get_contents('/etc/prime/current_type')[1]).trim();
		}
		else {
      currentType = '';
		}
		let box = new St.BoxLayout();
		let gicon;

		if (currentType.indexOf('intel') != -1) {
			gicon = intelicon;
		}
		else if (currentType.indexOf('nvidia') != -1) {
			gicon = nvidiaicon;
		}
		else {
			gicon = primeicon;
		}

		let icon =	new St.Icon();
		icon.gicon = gicon;
		icon.style_class = 'system-status-icon';
		box.add(icon);
		this.actor.add_child(box);

		let summaryMenuItem = new PopupMenu.PopupMenuItem(_(`Currently using ${currentType}`), { style_class: "no-background" });

		if ( currentType ) {
			this.menu.addMenuItem(summaryMenuItem);
		}
		// In case the state is undefined, show both
		let nvidiaMenuItem = new PopupMenu.PopupImageMenuItem(_('Switch to Nvidia'), nvidiaicon);
		if ( currentType.indexOf('nvidia') == -1 ) {
			this.menu.addMenuItem(nvidiaMenuItem);
		}
		let intelMenuItem = new PopupMenu.PopupImageMenuItem(_('Switch to Intel'), intelicon);
		if ( currentType.indexOf('intel') == -1 ) {
			this.menu.addMenuItem(intelMenuItem);
		}

		let infoMenuItem = new PopupMenu.PopupMenuItem(_('Restart your session after switching!'), { style_class: "menu-item-small" });
		this.menu.addMenuItem(infoMenuItem);

		nvidiaMenuItem.connect('activate', Lang.bind(this, function(){
			Util.trySpawnCommandLine(Me.path + '/pkexec_nvidia');
			Main.notify(_('Restart or log out and back in to finish the switch'));
			icon.style_class = 'system-status-icon screencast-indicator';
			icon.gicon = nvidiaicon;
		}));
		intelMenuItem.connect('activate', Lang.bind(this, function(){
			Util.trySpawnCommandLine(Me.path + '/pkexec_intel');
			Main.notify(_('Restart or log out and back in to finish the switch'));
			icon.style_class = 'system-status-icon screencast-indicator';
			icon.gicon = intelicon;
		}));

	},
	destroy: function() {
		this.parent();
	}
});

function init() {}

function enable() {
		button = new SusePrimeSwitcher;
		Main.panel.addToStatusArea('SUSEPrimeSwitcher', button, 0, 'right');
}

function disable() {
		button.destroy();
}
