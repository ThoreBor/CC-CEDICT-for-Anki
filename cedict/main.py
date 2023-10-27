import re
from os.path import dirname, join, realpath
from sqlite3 import connect
from typing import List

from aqt import mw
from aqt.qt import QDialog, QIcon, QPixmap
from aqt.utils import showInfo, tooltip

from PyQt6.QtCore import Qt
from PyQt6 import QtGui, QtWidgets, QtCore

from ..third_party.hanzidentifier import hanzidentifier
from .config import *

# Connect to dictionary database
db_path = join(dirname(realpath(__file__)), '../CC-CEDICT_dictionary.db')
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
	return [w.strip() for w in re.split(r'[\n，,#%&$/ ]', s, 0, re.M)]

def color_tone(pinyin):
	firstTone = "āēīōūǖ"
	secondTone = "áéíóúǘ"
	thirdTone = "ǎěǐǒǔǚ"
	fourthTone = "àèìòùǜ"
	letters = list(pinyin)
	for i in letters:
		if i in firstTone:
			return f'<span style="color:#ff0000">{pinyin}</span>'
		if i in secondTone:
			return f'<span style="color:#d89000">{pinyin}</span>'
		if i in thirdTone:
			return f'<span style="color:#00a000">{pinyin}</span>'
		if i in fourthTone:
			return f'<span style="color:#0000ff">{pinyin}</span>'
	return f'<span>{pinyin}</span>'

class start_main(QDialog):

	def __init__(self, dialog, parent=None):
		self.parent = parent
		QDialog.__init__(self, parent, Qt.WindowType.Window)
		self.dialog = dialog
		self.dialog.setupUi(self)
		self.setupUI()
		self.inputs = []
		self.skipped = []
		self.duplicate = []
		self.batch_search_mode = False

	def setupUI(self):
		config = mw.addonManager.getConfig(__name__)

		# set icon
		icon = QIcon()
		icon.addPixmap(QPixmap(join(dirname(dirname(realpath(__file__))), "designer/icons/icon.png")), QIcon.Mode.Normal, QIcon.State.Off)
		self.setWindowIcon(icon)

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
		self.dialog.Deck.setCurrentText(config["deck_config"])
		self.dialog.Notetype.setCurrentText(config["notetype_config"])
		find_fields(self)
		self.dialog.Field1.setCurrentText(config["field_1_config"])
		self.dialog.Field2.setCurrentText(config["field_2_config"])
		self.dialog.Field3.setCurrentText(config["field_3_config"])
		self.dialog.Field4.setCurrentText(config["field_4_config"])	
		self.dialog.color_pinyin.setChecked(config["color_pinyin"])
		self.dialog.tags.setText(config["tags"])
		find_tags(self)

		# Connect buttons
		self.dialog.About.clicked.connect(lambda: about(self))
		self.dialog.Add.clicked.connect(self.init_add)
		self.dialog.Results.clicked.connect(self.tablewidgetclicked)
		self.dialog.SearchButton.clicked.connect(self.search)
		self.dialog.Query.returnPressed.connect(self.search)
		self.dialog.checkBox.stateChanged.connect(self.search)
		self.dialog.Field1.currentTextChanged.connect(lambda: save_config(self))
		self.dialog.Field2.currentTextChanged.connect(lambda: save_config(self))
		self.dialog.Field3.currentTextChanged.connect(lambda: save_config(self))
		self.dialog.Field4.currentTextChanged.connect(lambda: save_config(self))
		self.dialog.color_pinyin.stateChanged.connect(lambda: save_config(self))
		self.dialog.Deck.currentTextChanged.connect(lambda: save_config(self))
		self.dialog.Notetype.currentTextChanged.connect(lambda: find_fields(self))
		self.dialog.tags.textChanged.connect(lambda: save_config(self))

		# Tooltips
		self.dialog.Query.setToolTip("Search and import multiple words by separating them with one of those characters: ，,#%&$/")
		self.dialog.SearchButton.setToolTip("Search and import multiple words by separating them with one of those characters: ，,#%&$/")
		self.dialog.Add.setToolTip("If you searched for multiple words all results will be added, otherwise the entry above will be added.")

		# Align header
		item = self.dialog.Results.horizontalHeaderItem(0)
		item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		item = self.dialog.Results.horizontalHeaderItem(1)
		item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		item = self.dialog.Results.horizontalHeaderItem(2)
		item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		item = self.dialog.Results.horizontalHeaderItem(3)
		item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

		# Show 10 random entries
		c.execute('SELECT * FROM dictionary WHERE LENGTH(hanzi_trad) ==2  ORDER BY RANDOM() LIMIT 10')
		for row in c.fetchall():
			traditional = row[0]
			simplified = row[1]
			p = row[2]
			english = row[3]
			english = english
			result = [simplified, traditional, p, english]
			self.add_result(result)
		self.first_result()

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
		query = self.dialog.Query.text()
		if hanzidentifier.is_traditional(query):
			input_type = "hanzi_trad"
		if hanzidentifier.is_simplified(query):
			input_type = "hanzi_simp"
		if not hanzidentifier.is_traditional(query) and not hanzidentifier.is_simplified(query):
			input_type = "eng"
		for w in words:
			self.exact_match(w, input_type)

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
			english = row[3]
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
				english_list = english.split(",")
				if word in english_list and [simplified, traditional, pinyin, english] not in self.inputs:
					self.add_result([simplified, traditional, pinyin, english])
					self.inputs.append([simplified, traditional, pinyin, english])
			if not result:
				self.skipped.append(word)
		self.first_result()

	def partial_match(self, word, input_type):
		c.execute("SELECT * FROM dictionary WHERE (%s) Like ?" % (input_type), ('%{}%'.format(word),))
		for row in c.fetchall():
			traditional = row[0]
			simplified = row[1]
			pinyin = row[2]
			english = row[3]
			if [simplified, traditional, pinyin, english] not in self.inputs:
				self.add_result([simplified, traditional, pinyin, english])
				self.inputs.append([simplified, traditional, pinyin, english])
		self.first_result()
		
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
		if len(words) > 1:
			self.batch_mode_search(words)
			return

		if hanzidentifier.is_traditional(query):
			if self.dialog.checkBox.isChecked():
				self.exact_match(query, "hanzi_trad")
				return
			else:
				self.partial_match(query, "hanzi_trad")
				return
		if hanzidentifier.is_simplified(query):
			if self.dialog.checkBox.isChecked():
				self.exact_match(query, "hanzi_simp")
				return
			else:
				self.partial_match(query, "hanzi_simp")
				return
		if not hanzidentifier.is_traditional(query) and not hanzidentifier.is_simplified(query):
			self.dialog.checkBox.setChecked(True)
			self.exact_match(query, "eng")
			return

	def tablewidgetclicked(self):
		for idx in self.dialog.Results.selectionModel().selectedIndexes():
			row = idx.row()
		simp = self.dialog.Results.item(row, 0).text()
		trad = self.dialog.Results.item(row, 1).text()
		pinyin = self.dialog.Results.item(row, 2).text()
		english = self.dialog.Results.item(row, 3).text()
		self.show_entry(english, pinyin, trad, simp)

	def first_result(self):
		if self.dialog.Results.rowCount() > 0:
			simp = self.dialog.Results.item(0, 0).text()
			trad = self.dialog.Results.item(0, 1).text()
			pinyin = self.dialog.Results.item(0, 2).text()
			english = self.dialog.Results.item(0, 3).text()
			self.show_entry(english, pinyin, trad, simp)

	def show_entry(self, english, pinyin, trad, simp):
		english = english.split(", ")
		english_entry = ""
		for i in english:
			english_entry = f"{english_entry}{i}\n"
		if trad != simp:
			self.dialog.Hanzi.setText(f"{trad}/{simp}")
		else:
			self.dialog.Hanzi.setText(trad)
		self.dialog.Pinyin.setText(pinyin)
		self.dialog.English.setText(english_entry)

	def add_note(self, row, input_type, tags):
		config = mw.addonManager.getConfig(__name__)
		col = mw.col
		deck_name = self.dialog.Deck.currentText()
		did = col.decks.id_for_name(deck_name)
		note_type_name = self.dialog.Notetype.currentText()
		nid = col.models.id_for_name(note_type_name)
		m = col.models.byName(note_type_name)
		col.models.setCurrent(m)
		# new_note will replace newNote
		try:
			n = col.new_note(nid)
		except:
			n = col.newNote(forDeck=False)
		simplified = row[0]
		pinyin_raw = row[2]
		traditional = row[1]
		english = row[3].rstrip(", ")

		if config["color_pinyin"]:
			pinyin_list = pinyin_raw.split(" ")
			pinyin = ""
			for i in pinyin_list:
				pinyin = f"{pinyin} {color_tone(i)}" if pinyin else f"{pinyin}{color_tone(i)}"
		else:
			pinyin = row[2]

		simplified_field_name = config["field_1_config"]
		n[simplified_field_name] = simplified
		traditional_field_name = config["field_2_config"]
		n[traditional_field_name] = traditional
		pinyin_field_name = config["field_3_config"]
		n[pinyin_field_name] = pinyin
		english_field_name = config["field_4_config"]
		n[english_field_name] = english
		n.add_tag(tags)

		note_ids_simplified = col.find_notes("{}:{}".format(simplified_field_name, simplified))
		note_ids_traditional = col.find_notes("{}:{}".format(traditional_field_name, traditional))
		note_ids_english = col.find_notes("{}:{}".format(english_field_name, english.replace("or", ""))) # excluding "or" because it causes errors
		note_ids = []
		for i in note_ids_simplified:
			note_ids.append(i)
		for i in note_ids_traditional:
			note_ids.append(i)
		for i in note_ids_english:
			note_ids.append(i)
		
		if note_ids:
			newline = "\n"
			showInfo(f"This note already exists:\n{simplified} \t {traditional} \t {pinyin} \t {english.replace(newline, ' ')}")
			self.duplicate.append([simplified, traditional, pinyin_raw, english])
		else:
			col.add_note(n, did)

	def add_multiple_notes(self, input_type):
		tags = self.dialog.tags.text()
		for row in self.inputs:
			self.add_note(row, input_type, tags)
		added_count = len(self.inputs) - len(self.duplicate)
		tooltip("Added {} notes, skipped: {}, duplicate: {}".format(added_count, len(self.skipped), len(self.duplicate)))

	def init_add(self):
		config = mw.addonManager.getConfig(__name__)
		used_fields = [self.dialog.Field1.currentText(), self.dialog.Field2.currentText(), self.dialog.Field3.currentText(), self.dialog.Field4.currentText()]
		if any(used_fields.count(fields) > 1 for fields in used_fields):
			showInfo("Each field can only be used once.")
			return
		query = self.dialog.Query.text()
		if hanzidentifier.is_traditional(query):
			input_type = "hanzi_trad"
		if hanzidentifier.is_simplified(query):
			input_type = "hanzi_simp"
		if not hanzidentifier.is_traditional(query) and not hanzidentifier.is_simplified(query):
			input_type = "eng"

		if self.batch_search_mode:
			if self.inputs:
				self.add_multiple_notes(input_type)
			return
		else:
			Hanzi = self.dialog.Hanzi.text().split("/")
			if len(Hanzi) > 1:
				trad = Hanzi[0]
				simp = Hanzi[1]
			else:
				trad = Hanzi[0]
				simp = Hanzi[0]

			pinyin = self.dialog.Pinyin.text()
			english = self.dialog.English.toPlainText().replace("\n", ", ")
			tags = self.dialog.tags.text()
			self.add_note([simp, trad, pinyin, english], input_type, tags)

		if [simp, trad, pinyin, english] not in self.duplicate:
			tooltip("Added 1 note")
