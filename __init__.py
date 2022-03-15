from aqt import mw
from aqt.qt import QAction, QKeySequence, qtmajor
from .cedict.main import start_main
if qtmajor > 5:
	from .forms.pyqt6UI import dict_ui
else:
	from .forms.pyqt5UI import dict_ui


def open_dict():
	mw.dict = start_main(dict_ui.Ui_Dialog())
	mw.dict.show()
	mw.dict.raise_()
	mw.dict.activateWindow()


action = QAction("CC-CEDICT for Anki", mw)
action.triggered.connect(open_dict)
mw.form.menuTools.addAction(action)
action.setShortcut(QKeySequence("Ctrl+D"))