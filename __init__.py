from aqt import mw
from PyQt5.QtWidgets import QAction, QMenu
from aqt.qt import *
from .main import start_main

def open_dict():
	mw.dict = start_main()
	mw.dict.show()
	mw.dict.raise_()
	mw.dict.activateWindow()

action = QAction("CC-CEDICT for Anki", mw)
action.triggered.connect(open_dict)
mw.form.menuTools.addAction(action)
action.setShortcut(QKeySequence("Ctrl+D"))