#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import gc
import logging
import logging.handlers
import ConfigParser

import gobject
import dbus
import gtk

try:
	import osso
except ImportError:
	osso = None

import constants
import utils.hildonize as hildonize
import util.misc as misc_utils


_moduleLogger = logging.getLogger(__name__)
PROFILE_STARTUP = False


class REPLACEMEProgram(hildonize.get_app_class()):

	def __init__(self):
		super(REPLACEMEProgram, self).__init__()

		if not hildonize.IS_HILDON_SUPPORTED:
			_moduleLogger.info("No hildonization support")

		if osso is not None:
			self._osso_c = osso.Context(constants.__app_name__, constants.__version__, False)
			self._deviceState = osso.DeviceState(self._osso_c)
			self._deviceState.set_device_state_callback(self._on_device_state_change, 0)
		else:
			_moduleLogger.info("No osso support")
			self._osso_c = None
			self._deviceState = None

	def _save_settings(self):
		config = ConfigParser.SafeConfigParser()

		self._REPLACEME.save_settings(config, "Windows")

		with open(constants._user_settings_, "wb") as configFile:
			config.write(configFile)

	def _load_settings(self):
		config = ConfigParser.SafeConfigParser()
		config.read(constants._user_settings_)

		self._REPLACEME.load_settings(config, "Windows")

	@misc_utils.log_exception(_moduleLogger)
	def _on_device_state_change(self, shutdown, save_unsaved_data, memory_low, system_inactivity, message, userData):
		"""
		For system_inactivity, we have no background tasks to pause

		@note Hildon specific
		"""
		if memory_low:
			gc.collect()

		if save_unsaved_data or shutdown:
			self._save_settings()

	@misc_utils.log_exception(_moduleLogger)
	def _on_destroy(self, widget = None, data = None):
		try:
			self.quit()
		finally:
			gtk.main_quit()

	def quit(self):
		try:
			self._save_settings()
		except Exception:
			_moduleLogger.exception("Error saving settigns")

		try:
			self._deviceState.close()
		except AttributeError:
			pass # Either None or close was removed (in Fremantle)
		except Exception:
			_moduleLogger.exception("Error closing device state")
		try:
			self._osso_c.close()
		except AttributeError:
			pass # Either None or close was removed (in Fremantle)
		except Exception:
			_moduleLogger.exception("Error closing osso state")


def run():
	try:
		os.makedirs(constants._data_path_)
	except OSError, e:
		if e.errno != 17:
			raise

	try:
		os.makedirs(constants._cache_path_)
	except OSError, e:
		if e.errno != 17:
			raise

	logFormat = '(%(relativeCreated)5d) %(levelname)-5s %(threadName)s.%(name)s.%(funcName)s: %(message)s'
	logging.basicConfig(level=logging.DEBUG, format=logFormat)
	rotating = logging.handlers.RotatingFileHandler(constants._user_logpath_, maxBytes=512*1024, backupCount=1)
	rotating.setFormatter(logging.Formatter(logFormat))
	root = logging.getLogger()
	root.addHandler(rotating)
	_moduleLogger.info("%s %s-%s" % (constants.__app_name__, constants.__version__, constants.__build__))
	_moduleLogger.info("OS: %s" % (os.uname()[0], ))
	_moduleLogger.info("Kernel: %s (%s) for %s" % os.uname()[2:])
	_moduleLogger.info("Hostname: %s" % os.uname()[1])

	gobject.threads_init()
	gtk.gdk.threads_init()
	l = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	# HACK Playback while silent on Maemo 5
	hildonize.set_application_name("FMRadio")

	app = REPLACEMElProgram()
	if not PROFILE_STARTUP:
		try:
			gtk.main()
		except KeyboardInterrupt:
			app.quit()
			raise
	else:
		app.quit()


if __name__ == "__main__":
	run()
