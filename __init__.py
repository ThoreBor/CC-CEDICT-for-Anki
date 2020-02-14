from aqt import mw
from PyQt5.QtWidgets import QAction, QMenu
from aqt.qt import *
from .dict_ui import start

def UI():
	s = start()
	if s.exec():
		pass

action = QAction("CC-CEDICT for Anki", mw)
action.triggered.connect(UI)
mw.form.menuTools.addAction(action)
action.setShortcut(QKeySequence("Ctrl+D"))