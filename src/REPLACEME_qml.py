#!/usr/bin/env python
# -*- coding: UTF8 -*-

from __future__ import with_statement

import os
import logging
import logging.handlers

import util.qt_compat as qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module("QtGui")
QtDeclarative = qt_compat.import_module("QtDeclarative")

import constants
from util import linux as linux_utils


_moduleLogger = logging.getLogger(__name__)


def run(args):
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

	app = QtGui.QApplication(args)

	view = QtDeclarative.QDeclarativeView()
	view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
	view.setWindowTitle(constants.__pretty_app_name__)

	context = view.rootContext()

	topLevelQMLFile = os.path.join(os.path.dirname(__file__), "data", constants.__app_name__+".qml")
	view.setSource(topLevelQMLFile)

	view.show()
	return app.exec_()


if __name__ == "__main__":
	import sys

	val = run(sys.argv)
	sys.exit(val)
