from PyQt5 import QtCore, QtGui, QtWidgets
from sqlite3 import connect
from os.path import dirname, join, realpath

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip


from .forms import dict_ui
from .import_file import importfile

# Connect to dictionary database
db_path = join(dirname(realpath(__file__)), 'CC-CEDICT_dictionary.db')
conn = connect(db_path)
c = conn.cursor()


def debug(s):
	sys.stdout.write(s + "\n")


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

		# Connect buttons
		self.dialog.About.clicked.connect(self.about)
		self.dialog.Add.clicked.connect(self.Add_Card)
		self.dialog.Results.itemClicked.connect(self.listwidgetclicked)
		self.dialog.SearchButton.clicked.connect(self.search)
		self.dialog.Field1.currentTextChanged.connect(self.save_config)
		self.dialog.Field2.currentTextChanged.connect(self.save_config)
		self.dialog.Field3.currentTextChanged.connect(self.save_config)
		self.dialog.Field4.currentTextChanged.connect(self.save_config)
		self.dialog.Deck.currentTextChanged.connect(self.save_config)
		self.dialog.Notetype.currentTextChanged.connect(self.save_config)
		self.dialog.Input_Type.currentTextChanged.connect(self.save_config)

		# Set current text for config items
		self.dialog.Input_Type.setCurrentText(config["search_config"])
		self.dialog.Deck.setCurrentText(config["deck_config"])
		self.dialog.Notetype.setCurrentText(config["notetype_config"])
		self.dialog.Field1.setCurrentText(config["field_1_config"])
		self.dialog.Field2.setCurrentText(config["field_2_config"])
		self.dialog.Field3.setCurrentText(config["field_3_config"])
		self.dialog.Field4.setCurrentText(config["field_4_config"])

		# Show 20 random entries
		c.execute('SELECT * FROM dictionary ORDER BY RANDOM() LIMIT 20')
		for row in c.fetchall():
			traditional = row[0]
			simplified = row[1]
			p = row[2]
			english = row[3]
			english = english[:-3]
			line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
			self.dialog.Results.addItem(line)

	def batch_mode_search(self, words):
		self.batch_search_mode = True
		for w in words:
			self.search_word(w)
		if self.skipped:
			line = "Can't find {} words: {}".format(len(self.skipped), ",".join(self.skipped))
			self.dialog.Results.addItem(line)

	def search_word(self, word):
		# debug("search word: {}".format(word))
		c.execute('SELECT * FROM dictionary WHERE hanzi_simp=?', (word,))
		row = c.fetchone()
		# debug("row is {}".format(str(row)))
		if row:
			traditional = row[0]
			simplified = row[1]
			pin_ying = row[2]
			# the English part contains a new line.
			english = row[3].rstrip("\n")
			line = str(simplified + "\t" + traditional + "\t" + pin_ying + "\t" + english)
			self.dialog.Results.addItem(line)
			self.inputs.append(row)
		else:
			self.skipped.append(word)

	def search(self):
		self.skipped = []
		self.inputs = []
		self.duplicate = []
		self.batch_search_mode = False
		self.dialog.Results.clear()
		query = self.dialog.Query.text()
		# note that this is the Chinese "，" character which is different from "," in English.
		words = [w.strip() for w in query.split("，")]
		# debug("words: {}, len: {}".format(str(words), len(words)))
		if len(words) > 1:
			self.batch_mode_search(words)
			return

		line_list = []
		if self.dialog.Input_Type.currentText() == "Traditional":
			#exact match
			c.execute('SELECT * FROM dictionary WHERE hanzi_trad=?', (query,))
			for row in c.fetchall():
				traditional = row[0]
				simplified = row[1]
				p = row[2]
				english = row[3]
				english = english[:-3]
				line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
				line_list.append(line)
				self.dialog.Results.addItem(line)
			#partial match
			c.execute('SELECT * FROM dictionary WHERE hanzi_trad Like ?',('%{}%'.format(query),))
			if self.dialog.checkBox.isChecked():
				pass
			else:
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
					if line not in line_list:
						self.dialog.Results.addItem(line)

		if self.dialog.Input_Type.currentText() == "Simplified":
			#exact match
			c.execute('SELECT * FROM dictionary WHERE hanzi_simp=?', (query,))
			for row in c.fetchall():
				traditional = row[0]
				simplified = row[1]
				p = row[2]
				english = row[3]
				english = english[:-3]
				line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
				line_list.append(line)
				self.dialog.Results.addItem(line)

			#partial
			c.execute('SELECT * FROM dictionary WHERE hanzi_simp Like ?',('%{}%'.format(query),))
			if self.dialog.checkBox.isChecked():
				pass
			else:
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
					if line not in line_list:
						self.dialog.Results.addItem(line)

		if self.dialog.Input_Type.currentText() == "English":
			c.execute('SELECT * FROM dictionary WHERE eng=?', (query,))
			for row in c.fetchall():
				traditional = row[0]
				simplified = row[1]
				p = row[2]
				english = row[3]
				english = english[:-3]
				line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
				line_list.append(line)
				self.dialog.Results.addItem(line)
			c.execute('SELECT * FROM dictionary WHERE eng Like ?',('%{}%'.format(query),))
			for row in c.fetchall():
				traditional = row[0]
				simplified = row[1]
				p = row[2]
				english = row[3]
				english = english[:-3]
				english_list = english.split(",")
				line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
				if query in english_list:
					if line not in line_list:
						self.dialog.Results.addItem(line)

			if self.dialog.checkBox.isChecked():
				pass
			else:
				c.execute('SELECT * FROM dictionary WHERE eng Like ?',('%{}%'.format(query),))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)	
					if line not in line_list:
						self.dialog.Results.addItem(line)

	def listwidgetclicked(self, item):
		data = item.text()
		data = data.split("\t")
		simp = data[0]
		trad = data[1]
		pinyin = data[2]
		english = data[3]
		english = english.split(", ")
		english_entry = ""
		for i in english:
			english_entry = english_entry + i + "\n"
		if trad != simp:
			self.dialog.Hanzi.setText(trad+"\n"+simp)
		else:
			self.dialog.Hanzi.setText(trad)
		self.dialog.Pinyin.setText(pinyin)
		self.dialog.English.setText(english_entry)
		self.dialog.English.adjustSize()
		self.dialog.Pinyin.adjustSize()
		self.dialog.Hanzi.adjustSize()

	def add_note(self, row):
		col = mw.col
		deck_name = self.dialog.Deck.currentText()
		did = col.decks.id_for_name(deck_name)
		note_type_name = self.dialog.Notetype.currentText()
		m = col.models.byName(note_type_name)
		col.models.setCurrent(m)
		n = col.newNote()
		traditional = row[0]
		simplified = row[1]
		pin_ying = row[2]
		english = row[3]

		n['Pinyin'] = pin_ying
		simplified_field_name = "Simplified"
		n[simplified_field_name] = simplified
		n['English'] = english
		n['Traditional'] = traditional
		node_ids = col.find_notes("{}:{}".format(simplified_field_name, simplified))
		if node_ids:
			showInfo("The note with the question {} already exists".format(simplified))
			self.duplicate.append(simplified)
		else:
			col.add_note(n, did)

	def add_multiple_notes(self):
		for row in self.inputs:
			self.add_note(row)
		added_count = len(self.inputs) - len(self.duplicate)
		tooltip("Added {} notes, skipped: {}, duplicate: {}".format(
			added_count, len(self.skipped), len(self.duplicate)))

	def Add_Card(self):
		if self.batch_search_mode:
			if self.inputs:
				self.add_multiple_notes()
			return

		to_add =  open(join(dirname(realpath(__file__)), 'to_add.txt'), "w", encoding="utf-8")
		Hanzi = self.dialog.Hanzi.text()
		Hanzi = Hanzi.split("\n")
		if len(Hanzi) > 1:
			trad = Hanzi[0]
			simp = Hanzi[1]
		else:
			trad = Hanzi[0]
			simp = Hanzi[0]
		Pinyin = self.dialog.Pinyin.text()
		English = self.dialog.English.text()
		
		if self.dialog.Field1.currentText() == "Simplified":
			Field1_content = simp
		if self.dialog.Field1.currentText() == "Traditional":
			Field1_content = trad
		if self.dialog.Field1.currentText() == "Pinyin":
			Field1_content = Pinyin
		if self.dialog.Field1.currentText() == "English":
			Field1_content = English

		if self.dialog.Field2.currentText() == "Simplified":
			Field2_content = simp
		if self.dialog.Field2.currentText() == "Traditional":
			Field2_content = trad
		if self.dialog.Field2.currentText() == "Pinyin":
			Field2_content = Pinyin
		if self.dialog.Field2.currentText() == "English":
			Field2_content = English

		if self.dialog.Field3.currentText() == "Simplified":
			Field3_content = simp
		if self.dialog.Field3.currentText() == "Traditional":
			Field3_content = trad
		if self.dialog.Field3.currentText() == "Pinyin":
			Field3_content = Pinyin
		if self.dialog.Field3.currentText() == "English":
			Field3_content = English
		if self.dialog.Field3.currentText() == "Nothing":
			Field3_content = ""

		if self.dialog.Field4.currentText() == "Simplified":
			Field4_content = simp
		if self.dialog.Field4.currentText() == "Traditional":
			Field4_content = trad
		if self.dialog.Field4.currentText() == "Pinyin":
			Field4_content = Pinyin
		if self.dialog.Field4.currentText() == "English":
			Field4_content = English
		if self.dialog.Field4.currentText() == "Nothing":
			Field4_content = ""

		Card = str(Field1_content + "\t" + Field2_content + "\t" + Field3_content + "\t" + Field4_content)
		to_add.write(Card)
		to_add.close()
		importfile(self.dialog.Deck.currentText(), self.dialog.Notetype.currentText())

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