from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets
from sqlite3 import connect
from os.path import dirname, join, realpath

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip


from .forms import dict_ui

import re

# Connect to dictionary database
db_path = join(dirname(realpath(__file__)), 'CC-CEDICT_dictionary.db')
conn = connect(db_path)
c = conn.cursor()

def debug(s):
	sys.stdout.write(s + "\n")

def split_string(s: str) -> List[str]:
	"""
	Split a string using one of the supported separator characters.
	Each element is then stripped of leading the trailing spaces.

	:param s: a string
	:return:
	"""
	return [w.strip() for w in re.split(r'[，,#%&$/]', s)]


class start_main(QDialog):

	def __init__(self, parent=None):
		self.parent = parent
		QDialog.__init__(self, parent, Qt.Window)
		self.dialog = dict_ui.Ui_Dialog()
		self.dialog.setupUi(self)
		self.setupUI()
		self.inputs = []
		self.skipped = []
		self.duplicate = []
		self.batch_search_mode = False

	def setupUI(self):
		config = mw.addonManager.getConfig(__name__)

		# Find all decks and add them to dropdown
		out = mw.col.decks.all()
		decklist = []
		for l in out:
			decklist.append(l['name'])
		for i in decklist:
			self.dialog.Deck.addItem(str(i))

		# Find all notetypes and add them to dropdown
		out = mw.col.models.all()
		notetypelist = []
		for l in out:
			notetypelist.append(l['name'])
		for i in notetypelist:
			self.dialog.Notetype.addItem(str(i))

		# Set current text for config items
		self.dialog.Input_Type.setCurrentText(config["search_config"])
		self.dialog.Deck.setCurrentText(config["deck_config"])
		self.dialog.Notetype.setCurrentText(config["notetype_config"])
		self.find_fields()
		self.dialog.Field1.setCurrentText(config["field_1_config"])
		self.dialog.Field2.setCurrentText(config["field_2_config"])
		self.dialog.Field3.setCurrentText(config["field_3_config"])
		self.dialog.Field4.setCurrentText(config["field_4_config"])		

		# Connect buttons
		self.dialog.About.clicked.connect(self.about)
		self.dialog.Add.clicked.connect(self.init_add)
		self.dialog.Results.doubleClicked.connect(self.tablewidgetclicked)
		self.dialog.SearchButton.clicked.connect(self.search)
		self.dialog.Query.returnPressed.connect(self.search)
		self.dialog.checkBox.stateChanged.connect(self.search)
		self.dialog.Field1.currentTextChanged.connect(self.save_config)
		self.dialog.Field2.currentTextChanged.connect(self.save_config)
		self.dialog.Field3.currentTextChanged.connect(self.save_config)
		self.dialog.Field4.currentTextChanged.connect(self.save_config)
		self.dialog.Deck.currentTextChanged.connect(self.save_config)
		self.dialog.Notetype.currentTextChanged.connect(self.find_fields)
		self.dialog.Input_Type.currentTextChanged.connect(self.save_config)

		# Tooltips
		self.dialog.Query.setToolTip("Search and import multiple words by separating them with one of those characters: ，,#%&$/")
		self.dialog.SearchButton.setToolTip("Search and import multiple words by separating them with one of those characters: ，,#%&$/")
		self.dialog.Add.setToolTip("If you searched for multiple words all results will be added, otherwise the entry above will be added.")

		# Align header
		item = self.dialog.Results.horizontalHeaderItem(0)
		item.setTextAlignment(Qt.AlignLeft)
		item = self.dialog.Results.horizontalHeaderItem(1)
		item.setTextAlignment(Qt.AlignLeft)
		item = self.dialog.Results.horizontalHeaderItem(2)
		item.setTextAlignment(Qt.AlignLeft)
		item = self.dialog.Results.horizontalHeaderItem(3)
		item.setTextAlignment(Qt.AlignLeft)

		# Show 10 random entries
		c.execute('SELECT * FROM dictionary ORDER BY RANDOM() LIMIT 10')
		for row in c.fetchall():
			traditional = row[0]
			simplified = row[1]
			p = row[2]
			english = row[3]
			english = english[:-3]
			result = [simplified, traditional, p, english]
			self.add_result(result)

	def add_result(self, result):
		rowPosition = self.dialog.Results.rowCount()
		self.dialog.Results.insertRow(rowPosition)
		self.dialog.Results.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(result[0])))
		self.dialog.Results.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(result[1])))
		self.dialog.Results.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(result[2])))
		self.dialog.Results.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(result[3]).rstrip(", ")))

		font = QtGui.QFont()
		font.setFamily("SimHei")
		font.setPointSize(10)
		self.dialog.Results.item(rowPosition, 0).setFont(font)
		self.dialog.Results.item(rowPosition, 1).setFont(font)
		font.setFamily("Arial")
		font.setPointSize(8)
		self.dialog.Results.item(rowPosition, 2).setFont(font)
		self.dialog.Results.item(rowPosition, 3).setFont(font)
		self.dialog.Results.resizeColumnsToContents()

	def batch_mode_search(self, words):
		self.batch_search_mode = True
		for w in words:
			if self.dialog.Input_Type.currentText() == "Traditional":
				self.exact_match(w, "hanzi_trad")
			if self.dialog.Input_Type.currentText() == "Simplified":
				self.exact_match(w, "hanzi_simp")
			if self.dialog.Input_Type.currentText() == "English":
				self.exact_match(w, "eng")

		if self.skipped:
			line = "Can't find {} words: {}".format(len(self.skipped), ",".join(self.skipped))
			showInfo(line)

	def exact_match(self, word, input_type):
		c.execute("SELECT * FROM dictionary WHERE (%s) = (?)" % (input_type), (word,))
		result = c.fetchall()
		for row in result:
			traditional = row[0]
			simplified = row[1]
			pinyin = row[2]
			# the English part contains a new line.
			english = row[3].rstrip("\n")
			self.add_result([simplified, traditional, pinyin, english])
			self.inputs.append([simplified, traditional, pinyin, english])
		if not result and input_type != "eng":
			self.skipped.append(word)

		if input_type == "eng":
			c.execute('SELECT * FROM dictionary WHERE eng Like ?',('%{}%'.format(word),))
			result = c.fetchall()
			for row in result:
				traditional = row[0]
				simplified = row[1]
				pinyin = row[2]
				english = row[3]
				english = english[:-3]
				english_list = english.split(",")
				if word in english_list and [simplified, traditional, pinyin, english] not in self.inputs:
					self.add_result([simplified, traditional, pinyin, english])
					self.inputs.append([simplified, traditional, pinyin, english])
			if not result:
				self.skipped.append(word)

	def partial_match(self, word, input_type):
		c.execute("SELECT * FROM dictionary WHERE (%s) Like ?" % (input_type), ('%{}%'.format(word),))
		for row in c.fetchall():
			traditional = row[0]
			simplified = row[1]
			pinyin = row[2]
			# the English part contains a new line.
			english = row[3].rstrip("\n")
			if [simplified, traditional, pinyin, english] not in self.inputs:
				self.add_result([simplified, traditional, pinyin, english])
				self.inputs.append([simplified, traditional, pinyin, english])
		
	def search(self):
		query = self.dialog.Query.text()
		if not query:
			return
		self.dialog.Results.setRowCount(0)
		self.skipped = []
		self.inputs = []
		self.duplicate = []
		self.batch_search_mode = False
		words = split_string(query)
		# debug("words: {}, len: {}".format(str(words), len(words)))
		if len(words) > 1:
			self.batch_mode_search(words)
			return

		if self.dialog.Input_Type.currentText() == "Traditional":
			if self.dialog.checkBox.isChecked():
				self.exact_match(query, "hanzi_trad")
			else:
				self.partial_match(query, "hanzi_trad")

		if self.dialog.Input_Type.currentText() == "Simplified":
			if self.dialog.checkBox.isChecked():
				self.exact_match(query, "hanzi_simp")
			else:
				self.partial_match(query, "hanzi_simp")

		if self.dialog.Input_Type.currentText() == "English":
			if self.dialog.checkBox.isChecked():
				self.exact_match(query, "eng")
			else:
				self.partial_match(query, "eng")

	def tablewidgetclicked(self):
		for idx in self.dialog.Results.selectionModel().selectedIndexes():
			row = idx.row()
		simp = self.dialog.Results.item(row, 0).text()
		trad = self.dialog.Results.item(row, 1).text()
		pinyin = self.dialog.Results.item(row, 2).text()
		english = self.dialog.Results.item(row, 3).text()
		english = english.split(", ")
		english_entry = ""
		for i in english:
			english_entry = f"{english_entry}{i}\n"
		if trad != simp:
			self.dialog.Hanzi.setText(f"{trad}\n{simp}")
		else:
			self.dialog.Hanzi.setText(trad)
		self.dialog.Pinyin.setText(pinyin)
		self.dialog.English.setText(english_entry)
		self.dialog.English.adjustSize()
		self.dialog.Pinyin.adjustSize()
		self.dialog.Hanzi.adjustSize()

	def add_note(self, row):
		config = mw.addonManager.getConfig(__name__)
		col = mw.col
		deck_name = self.dialog.Deck.currentText()
		did = col.decks.id_for_name(deck_name)
		note_type_name = self.dialog.Notetype.currentText()
		m = col.models.byName(note_type_name)
		col.models.setCurrent(m)
		# Since we don't set the model for the selected desk, set the forDeck parameter to false
		# to make sure the current global model is used for the new note.
		n = col.newNote(forDeck=False)
		simplified = row[0]
		traditional = row[1]
		pinyin = row[2]
		english = row[3]

		simplified_field_name = config["field_1_config"]
		n[simplified_field_name] = simplified
		traditional_field_name = config["field_2_config"]
		n[traditional_field_name] = traditional
		pinyin_field_name = config["field_3_config"]
		n[pinyin_field_name] = pinyin
		english_field_name = config["field_4_config"]
		n[english_field_name] = english

		if self.dialog.Input_Type.currentText() == "Simplified":
			note_ids = col.find_notes("{}:{}".format(simplified_field_name, simplified))
		if self.dialog.Input_Type.currentText() == "Traditional":
			note_ids = col.find_notes("{}:{}".format(traditional_field_name, traditional))
		if self.dialog.Input_Type.currentText() == "English":
			note_ids = col.find_notes("{}:{}".format(english_field_name, english))

		if note_ids:
			newline = "\n"
			showInfo(f"This note already exists:\n{simplified} \t {traditional} \t {pinyin} \t {english.replace(newline, ' ')}")
			self.duplicate.append([simplified, traditional, pinyin, english])
		else:
			col.add_note(n, did)

	def add_multiple_notes(self):
		for row in self.inputs:
			self.add_note(row)
		added_count = len(self.inputs) - len(self.duplicate)
		tooltip("Added {} notes, skipped: {}, duplicate: {}".format(added_count, len(self.skipped), len(self.duplicate)))

	def init_add(self):
		used_fields = [self.dialog.Field1.currentText(), self.dialog.Field2.currentText(), self.dialog.Field3.currentText(), self.dialog.Field4.currentText()]
		if any(used_fields.count(fields) > 1 for fields in used_fields):
			showInfo("Each field can only be used once.")
			return

		if self.batch_search_mode:
			if self.inputs:
				self.add_multiple_notes()
			return
		else:
			Hanzi = self.dialog.Hanzi.text().split("\n")
			if len(Hanzi) > 1:
				trad = Hanzi[0]
				simp = Hanzi[1]
			else:
				trad = Hanzi[0]
				simp = Hanzi[0]
			pinyin = self.dialog.Pinyin.text()
			english = self.dialog.English.text()
			self.add_note([simp, trad, pinyin, english])

		if [simp, trad, pinyin, english] not in self.duplicate:
			tooltip("Added 1 note")

	def find_fields(self):
		# Remove old items
		self.dialog.Field1.blockSignals(True)
		self.dialog.Field2.blockSignals(True)
		self.dialog.Field3.blockSignals(True)
		self.dialog.Field4.blockSignals(True)

		self.dialog.Field1.clear()
		self.dialog.Field2.clear()
		self.dialog.Field3.clear()
		self.dialog.Field4.clear()

		# Find fields of the selected notetype and add them to dropdown
		out = mw.col.models.all()
		fieldlist = []
		for l in out:
			if l['name'] == self.dialog.Notetype.currentText():
				for i in l['flds']:
					fieldlist.append(i['name'])
		for i in fieldlist:
			self.dialog.Field1.addItem(str(i))
			self.dialog.Field2.addItem(str(i))
			self.dialog.Field3.addItem(str(i))
			self.dialog.Field4.addItem(str(i))

		self.dialog.Field1.blockSignals(False)
		self.dialog.Field2.blockSignals(False)
		self.dialog.Field3.blockSignals(False)
		self.dialog.Field4.blockSignals(False)
		self.save_config()
	
	def save_config(self):
		search_config = self.dialog.Input_Type.currentText()
		deck_config = self.dialog.Deck.currentText()
		notetype_config = self.dialog.Notetype.currentText()
		field_1_config = self.dialog.Field1.currentText()
		field_2_config = self.dialog.Field2.currentText()
		field_3_config = self.dialog.Field3.currentText()
		field_4_config = self.dialog.Field4.currentText()
		config = {"search_config": search_config, "deck_config": deck_config, "notetype_config": notetype_config, 
		"field_1_config": field_1_config, "field_2_config": field_2_config, "field_3_config": field_3_config, "field_4_config": field_4_config}
		mw.addonManager.writeConfig(__name__, config)

	def about(self):
		about_text = """
<h3>CC-CEDICT for Anki v1.2</h3><br>This add-on uses the <a href="https://cc-cedict.org/wiki/">CC-CEDICT</a> dictionary. 
It is licensed under the <a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share Alike 3.0 License</a>.<br>
The code for the add-on is available on <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki">GitHub.</a> 
It is licensed under the <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/blob/master/LICENSE">MIT License.</a><br><br>
If you like this add-on, rate and review it on <a href="https://ankiweb.net/shared/info/418828045">Anki Web</a>. 
If you want to report a bug, or make a feature request, please create a new 
<a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/issues">issue</a> on GitHub.<br>
<div>Icon made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> 
from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
<br><b>© Thore Tyborski 2020 with contributions from <a href="https://github.com/HappyRay">HappyRay</a>.</b>
		"""
		showInfo(about_text)