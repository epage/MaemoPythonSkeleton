#!/usr/bin/env python
# -*- coding: UTF8 -*-

from __future__ import with_statement

import os
import simplejson
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

import constants
from util import qui_utils
from util import misc as misc_utils


_moduleLogger = logging.getLogger(__name__)


class REPLACEME(object):

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
		self._app = app
		self._appIconPath = appIconPath
		self._recent = []
		self._clipboard = QtGui.QApplication.clipboard()

		self._mainWindow = None

		self._fullscreenAction = QtGui.QAction(None)
		self._fullscreenAction.setText("Fullscreen")
		self._fullscreenAction.setCheckable(True)
		self._fullscreenAction.setShortcut(QtGui.QKeySequence("CTRL+Enter"))
		self._fullscreenAction.toggled.connect(self._on_toggle_fullscreen)

		self._logAction = QtGui.QAction(None)
		self._logAction.setText("Log")
		self._logAction.setShortcut(QtGui.QKeySequence("CTRL+l"))
		self._logAction.triggered.connect(self._on_log)

		self._quitAction = QtGui.QAction(None)
		self._quitAction.setText("Quit")
		self._quitAction.setShortcut(QtGui.QKeySequence("CTRL+q"))
		self._quitAction.triggered.connect(self._on_quit)

		self._app.lastWindowClosed.connect(self._on_app_quit)
		self._mainWindow = MainWindow(None, self)
		self._mainWindow.window.destroyed.connect(self._on_child_close)

		self.load_settings()

		self._mainWindow.show()
		self._idleDelay = QtCore.QTimer()
		self._idleDelay.setSingleShot(True)
		self._idleDelay.setInterval(0)
		self._idleDelay.timeout.connect(lambda: self._mainWindow.start())
		self._idleDelay.start()

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

	@property
	def appIconPath(self):
		return self._appIconPath

	@property
	def fullscreenAction(self):
		return self._fullscreenAction

	@property
	def logAction(self):
		return self._logAction

	@property
	def quitAction(self):
		return self._quitAction

	def _close_windows(self):
		if self._mainWindow is not None:
			self.save_settings()
			self._mainWindow.window.destroyed.disconnect(self._on_child_close)
			self._mainWindow.close()
			self._mainWindow = None

	@misc_utils.log_exception(_moduleLogger)
	def _on_app_quit(self, checked = False):
		if self._mainWindow is not None:
			self.save_settings()
			self._mainWindow.destroy()

	@misc_utils.log_exception(_moduleLogger)
	def _on_child_close(self, obj = None):
		if self._mainWindow is not None:
			self.save_settings()
			self._mainWindow = None

	@misc_utils.log_exception(_moduleLogger)
	def _on_toggle_fullscreen(self, checked = False):
		for window in self._walk_children():
			window.set_fullscreen(checked)

	@misc_utils.log_exception(_moduleLogger)
	def _on_log(self, checked = False):
		with open(constants._user_logpath_, "r") as f:
			logLines = f.xreadlines()
			log = "".join(logLines)
			self._clipboard.setText(log)

	@misc_utils.log_exception(_moduleLogger)
	def _on_quit(self, checked = False):
		self._close_windows()


class MainWindow(object):

	def __init__(self, parent, app):
		self._app = app

		self._errorLog = qui_utils.QErrorLog()
		self._errorDisplay = qui_utils.ErrorDisplay(self._errorLog)

		self._layout = QtGui.QVBoxLayout()
		self._layout.setContentsMargins(0, 0, 0, 0)
		self._layout.addWidget(self._errorDisplay.toplevel)

		centralWidget = QtGui.QWidget()
		centralWidget.setLayout(self._layout)
		centralWidget.setContentsMargins(0, 0, 0, 0)

		self._window = QtGui.QMainWindow(parent)
		self._window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		qui_utils.set_autorient(self._window, True)
		qui_utils.set_stackable(self._window, True)
		self._window.setWindowTitle("%s" % constants.__pretty_app_name__)
		self._window.setWindowIcon(QtGui.QIcon(self._app.appIconPath))
		self._window.setCentralWidget(centralWidget)

		self._aboutAction = QtGui.QAction(None)
		self._aboutAction.setText("About")
		self._aboutAction.triggered.connect(self._on_about)

		self._closeWindowAction = QtGui.QAction(None)
		self._closeWindowAction.setText("Close")
		self._closeWindowAction.setShortcut(QtGui.QKeySequence("CTRL+w"))
		self._closeWindowAction.triggered.connect(self._on_close_window)

		if constants.IS_MAEMO:
			fileMenu = self._window.menuBar().addMenu("&File")

			viewMenu = self._window.menuBar().addMenu("&View")
			viewMenu.addAction(self._aboutAction)

			self._window.addAction(self._closeWindowAction)
			self._window.addAction(self._app.quitAction)
			self._window.addAction(self._app.fullscreenAction)
		else:
			fileMenu = self._window.menuBar().addMenu("&Units")
			fileMenu.addAction(self._closeWindowAction)
			fileMenu.addAction(self._app.quitAction)

			viewMenu = self._window.menuBar().addMenu("&View")
			viewMenu.addAction(self._app.fullscreenAction)
			viewMenu.addAction(self._aboutAction)

		self._window.addAction(self._app.logAction)

		self.set_fullscreen(self._app.fullscreenAction.isChecked())
		self._window.show()

	@property
	def window(self):
		return self._window

	def walk_children(self):
		return ()

	def start(self):
		pass

	def close(self):
		for child in self.walk_children():
			child.window.destroyed.disconnect(self._on_child_close)
			child.close()
		self._window.close()

	def destroy(self):
		pass

	def show(self):
		self._window.show()
		for child in self.walk_children():
			child.show()

	def hide(self):
		for child in self.walk_children():
			child.hide()
		self._window.hide()

	def set_fullscreen(self, isFullscreen):
		if isFullscreen:
			self._window.showFullScreen()
		else:
			self._window.showNormal()
		for child in self.walk_children():
			child.set_fullscreen(isFullscreen)

	def _on_about(self, checked = True):
		with qui_utils.notify_error(self._errorLog):
			if self._aboutDialog is None:
				import dialogs
				self._aboutDialog = dialogs.AboutDialog(self._app)
			response = self._aboutDialog.run()

	@misc_utils.log_exception(_moduleLogger)
	def _on_close_window(self, checked = True):
		self.close()


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
