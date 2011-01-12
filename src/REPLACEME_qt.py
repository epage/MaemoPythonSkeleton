#!/usr/bin/env python
# -*- coding: UTF8 -*-

from __future__ import with_statement

import os
import simplejson
import logging

from PyQt4 import QtGui

import constants
from util import qwrappers


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
	app = QtGui.QApplication([])
	handle = REPLACEME(app)
	return app.exec_()


if __name__ == "__main__":
	import sys

	logFormat = '(%(relativeCreated)5d) %(levelname)-5s %(threadName)s.%(name)s.%(funcName)s: %(message)s'
	logging.basicConfig(level=logging.DEBUG, format=logFormat)
	try:
		os.makedirs(constants._data_path_)
	except OSError, e:
		if e.errno != 17:
			raise

	val = run()
	sys.exit(val)
