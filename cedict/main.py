import re
from os.path import dirname, join, realpath
from sqlite3 import connect
from typing import List

from aqt import mw
from aqt.qt import QDialog, QIcon, QPixmap, qtmajor
from aqt.utils import showInfo, tooltip

if qtmajor > 5:
	from PyQt6.QtCore import Qt
	from PyQt6 import QtGui, QtWidgets
else:
	from PyQt5.QtCore import Qt
	from PyQt5 import QtGui, QtWidgets

from ..third_party.hanzidentifier import hanzidentifier

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
	return [w.strip() for w in re.split(r'[\n，,#%&$/ ]', s, re.M)]

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
		QDialog.__init__(self, parent, Qt.Window)
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
		self.find_fields()
		self.dialog.Field1.setCurrentText(config["field_1_config"])
		self.dialog.Field2.setCurrentText(config["field_2_config"])
		self.dialog.Field3.setCurrentText(config["field_3_config"])
		self.dialog.Field4.setCurrentText(config["field_4_config"])	
		self.dialog.color_pinyin.setChecked(config["color_pinyin"])

		# Connect buttons
		self.dialog.About.clicked.connect(self.about)
		self.dialog.Add.clicked.connect(self.init_add)
		self.dialog.Results.clicked.connect(self.tablewidgetclicked)
		self.dialog.SearchButton.clicked.connect(self.search)
		self.dialog.Query.returnPressed.connect(self.search)
		self.dialog.checkBox.stateChanged.connect(self.search)
		self.dialog.Field1.currentTextChanged.connect(self.save_config)
		self.dialog.Field2.currentTextChanged.connect(self.save_config)
		self.dialog.Field3.currentTextChanged.connect(self.save_config)
		self.dialog.Field4.currentTextChanged.connect(self.save_config)
		self.dialog.color_pinyin.stateChanged.connect(self.save_config)
		self.dialog.Deck.currentTextChanged.connect(self.save_config)
		self.dialog.Notetype.currentTextChanged.connect(self.find_fields)

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
		# debug("words: {}, len: {}".format(str(words), len(words)))
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
			self.dialog.Hanzi.setText(f"{trad}\n{simp}")
		else:
			self.dialog.Hanzi.setText(trad)
		self.dialog.Pinyin.setText(pinyin)
		self.dialog.English.setText(english_entry)
		self.dialog.English.adjustSize()
		self.dialog.Pinyin.adjustSize()
		self.dialog.Hanzi.adjustSize()

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
		note_ids_english = col.find_notes("{}:{}".format(english_field_name, english))
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
			Hanzi = self.dialog.Hanzi.text().split("\n")
			if len(Hanzi) > 1:
				trad = Hanzi[0]
				simp = Hanzi[1]
			else:
				trad = Hanzi[0]
				simp = Hanzi[0]

			pinyin = self.dialog.Pinyin.text()
			english = self.dialog.English.text().replace("\n", ", ")
			tags = self.dialog.tags.text()
			self.add_note([simp, trad, pinyin, english], input_type, tags)

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

		# Save notetype
		config = mw.addonManager.getConfig(__name__)
		notetype_config = self.dialog.Notetype.currentText()
		config = {"deck_config": config["deck_config"], "notetype_config": notetype_config, 
		"field_1_config": config["field_1_config"], "field_2_config": config["field_2_config"], 
		"field_3_config": config["field_3_config"], "field_4_config": config["field_4_config"],
		"color_pinyin": config["color_pinyin"]}
		mw.addonManager.writeConfig(__name__, config)
	
	def save_config(self):
		deck_config = self.dialog.Deck.currentText()
		notetype_config = self.dialog.Notetype.currentText()
		field_1_config = self.dialog.Field1.currentText()
		field_2_config = self.dialog.Field2.currentText()
		field_3_config = self.dialog.Field3.currentText()
		field_4_config = self.dialog.Field4.currentText()
		color_pinyin_config = self.dialog.color_pinyin.isChecked()
		config = {"deck_config": deck_config, "notetype_config": notetype_config, 
		"field_1_config": field_1_config, "field_2_config": field_2_config, "field_3_config": field_3_config, "field_4_config": field_4_config,
		"color_pinyin": color_pinyin_config}
		mw.addonManager.writeConfig(__name__, config)

	def about(self):
		about_text = """
<h3>CC-CEDICT for Anki v1.4</h3>
CC-CEDICT for Anki is licensed under the <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/blob/master/LICENSE">MIT License.</a><br><br>

<b>This add-on also ships with the following third-party code:</b><br>
- <a href="https://github.com/tsroten/hanzidentifier">hanzidentifier</a> by Thomas Roten (MIT Licence)<br>
- <a href="https://github.com/tsroten/zhon">zhon</a> by Thomas Roten (MIT Licence)<br><br>

This add-on uses the <a href="https://cc-cedict.org/wiki/">CC-CEDICT</a> dictionary, which is licensed under the 
<a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share Alike 3.0 License</a>.<br><br>

The code for the add-on is available on <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki">GitHub.</a> 
If you like this add-on, rate and review it on <a href="https://ankiweb.net/shared/info/418828045">Anki Web</a>. 
If you want to report a bug, or make a feature request, please create a new 
<a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/issues">issue</a> on GitHub.<br>

<span>Icon made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> 
from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></span>

<br><br><b>© Thore Tyborski 2022 with contributions from <a href="https://github.com/HappyRay">HappyRay</a>.</b>
		"""
		showInfo(about_text)