#!/usr/bin/env python
# -*- coding: UTF8 -*-

from __future__ import with_statement

import os
import simplejson
import logging
import logging.handlers

import util.qt_compat as qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module("QtGui")

import constants
from util import qwrappers
from util import linux as linux_utils


_moduleLogger = logging.getLogger(__name__)


class REPLACEME(qwrappers.ApplicationWrapper):

	_DATA_PATHS = [
		os.path.dirname(__file__),
		os.path.join(os.path.dirname(__file__), "../share"),
		os.path.join(os.path.dirname(__file__), "../data"),
		'/usr/share/%s' % constants.__app_name__,
		'/opt/%s/share' % constants.__app_name__,
	]

	def __init__(self, app):
		self._dataPath = ""
		if False:
			for dataPath in self._DATA_PATHS:
				appIconPath = os.path.join(dataPath, "pixmaps", "%s.png" %  constants.__app_name__)
				if os.path.isfile(appIconPath):
					self._dataPath = dataPath
					break
			else:
				raise RuntimeError("UI Descriptor not found!")
		else:
			appIconPath = ""
		self._appIconPath = appIconPath
		qwrappers.ApplicationWrapper.__init__(self, app, constants)

	@property
	def appIconPath(self):
		return self._appIconPath

	def load_settings(self):
		try:
			with open(constants._user_settings_, "r") as settingsFile:
				settings = simplejson.load(settingsFile)
		except IOError, e:
			_moduleLogger.info("No settings")
			settings = {}
		except ValueError:
			_moduleLogger.info("Settings were corrupt")
			settings = {}

		self._fullscreenAction.setChecked(settings.get("isFullScreen", False))

	def save_settings(self):
		settings = {
			"isFullScreen": self._fullscreenAction.isChecked(),
		}
		with open(constants._user_settings_, "w") as settingsFile:
			simplejson.dump(settings, settingsFile)

	def _new_main_window(self):
		return MainWindow(None, self)


class MainWindow(qwrappers.WindowWrapper):

	def __init__(self, parent, app):
		qwrappers.WindowWrapper.__init__(self, parent, app)
		self._window.setWindowTitle("%s" % constants.__pretty_app_name__)
		self._window.setWindowIcon(QtGui.QIcon(self._app.appIconPath))


def run():
	try:
		os.makedirs(linux_utils.get_resource_path("config", constants.__app_name__))
	except OSError, e:
		if e.errno != 17:
			raise
	try:
		os.makedirs(linux_utils.get_resource_path("cache", constants.__app_name__))
	except OSError, e:
		if e.errno != 17:
			raise
	try:
		os.makedirs(linux_utils.get_resource_path("data", constants.__app_name__))
	except OSError, e:
		if e.errno != 17:
			raise

	logPath = linux_utils.get_resource_path("cache", constants.__app_name__, "%s.log" % constants.__app_name__)
	logFormat = '(%(relativeCreated)5d) %(levelname)-5s %(threadName)s.%(name)s.%(funcName)s: %(message)s'
	logging.basicConfig(level=logging.DEBUG, format=logFormat)
	rotating = logging.handlers.RotatingFileHandler(logPath, maxBytes=512*1024, backupCount=1)
	rotating.setFormatter(logging.Formatter(logFormat))
	root = logging.getLogger()
	root.addHandler(rotating)
	_moduleLogger.info("%s %s-%s" % (constants.__app_name__, constants.__version__, constants.__build__))
	_moduleLogger.info("OS: %s" % (os.uname()[0], ))
	_moduleLogger.info("Kernel: %s (%s) for %s" % os.uname()[2:])
	_moduleLogger.info("Hostname: %s" % os.uname()[1])

	app = QtGui.QApplication([])
	handle = REPLACEME(app)
	return app.exec_()


if __name__ == "__main__":
	import sys

	val = run()
	sys.exit(val)
