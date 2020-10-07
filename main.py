from PyQt5 import QtCore, QtGui, QtWidgets
from sqlite3 import connect
from os.path import dirname, join, realpath

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .forms import dict_ui
from .import_file import importfile

# Connect to dictionary database
db_path = join(dirname(realpath(__file__)), 'CC-CEDICT_dictionary.db')
conn = connect(db_path)
c = conn.cursor()


class start_main(QDialog):

	def __init__(self, parent=None):
		self.parent = parent
		QDialog.__init__(self, parent, Qt.Window)
		self.dialog = dict_ui.Ui_Dialog()
		self.dialog.setupUi(self)
		self.setupUI()

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
		self.dialog.Results.doubleClicked.connect(self.tablewidgetclicked)
		self.dialog.SearchButton.clicked.connect(self.search)
		self.dialog.Query.returnPressed.connect(self.search)
		self.dialog.checkBox.stateChanged.connect(self.search)
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
		self.dialog.Results.setColumnCount(4)
		self.dialog.Results.insertRow(rowPosition)
		self.dialog.Results.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(result[0])))
		self.dialog.Results.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(result[1])))
		self.dialog.Results.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(result[2])))
		self.dialog.Results.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(str(result[3])))
		#self.dialog.Results.resizeColumnsToContents()

	def search(self):
		line_list = []
		self.dialog.Results.setRowCount(0)
		query = self.dialog.Query.text()

		if self.dialog.Input_Type.currentText() == "Traditional":
			#batch search
			if "/" in query:
				query = query.split("/")
				for i in query:
					c.execute('SELECT * FROM dictionary WHERE hanzi_trad=?', (i,))
					for row in c.fetchall():
						traditional = row[0]
						simplified = row[1]
						p = row[2]
						english = row[3]
						english = english[:-3]
						result = [simplified, traditional, p, english]
						line_list.append(result)
						self.add_result(result)

			if self.dialog.checkBox.isChecked() and "/" not in query:
				#exact match
				c.execute('SELECT * FROM dictionary WHERE hanzi_trad=?', (query,))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					result = [simplified, traditional, p, english]
					line_list.append(result)
					self.add_result(result)
			else:
				#partial match
				c.execute('SELECT * FROM dictionary WHERE hanzi_trad Like ?',('%{}%'.format(query),))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					result = [simplified, traditional, p, english]
					if result not in line_list:
						self.add_result(result)

		if self.dialog.Input_Type.currentText() == "Simplified":
			#batch search
			if "/" in query:
				query = query.split("/")
				for i in query:
					c.execute('SELECT * FROM dictionary WHERE hanzi_simp=?', (i,))
					for row in c.fetchall():
						traditional = row[0]
						simplified = row[1]
						p = row[2]
						english = row[3]
						english = english[:-3]
						result = [simplified, traditional, p, english]
						line_list.append(result)
						self.add_result(result)

			if self.dialog.checkBox.isChecked():
				#exact match
				c.execute('SELECT * FROM dictionary WHERE hanzi_simp=?', (query,))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					result = [simplified, traditional, p, english]
					line_list.append(result)
					self.add_result(result)
			else:
				#partial
				c.execute('SELECT * FROM dictionary WHERE hanzi_simp Like ?',('%{}%'.format(query),))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
					result = [simplified, traditional, p, english]
					if result not in line_list:
						self.add_result(result)

		if self.dialog.Input_Type.currentText() == "English":
			#batch search
			if "/" in query:
				query = query.split("/")
				for i in query:
					c.execute('SELECT * FROM dictionary WHERE eng=?', (i,))
					for row in c.fetchall():
						traditional = row[0]
						simplified = row[1]
						p = row[2]
						english = row[3]
						english = english[:-3]
						result = [simplified, traditional, p, english]
						line_list.append(result)
						self.add_result(result)
					c.execute('SELECT * FROM dictionary WHERE eng Like ?',('%{}%'.format(i),))
					for row in c.fetchall():
						traditional = row[0]
						simplified = row[1]
						p = row[2]
						english = row[3]
						english = english[:-3]
						english_list = english.split(",")
						result = [simplified, traditional, p, english]
						if i in english_list:
							if result not in line_list:
								self.add_result(result)

			if self.dialog.checkBox.isChecked():
				#exact match
				c.execute('SELECT * FROM dictionary WHERE eng=?', (query,))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					result = [simplified, traditional, p, english]
					line_list.append(result)
					self.add_result(result)
				c.execute('SELECT * FROM dictionary WHERE eng Like ?',('%{}%'.format(query),))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					english_list = english.split(",")
					result = [simplified, traditional, p, english]
					if query in english_list:
						if result not in line_list:
							self.add_result(result)
			else:
				#partial
				c.execute('SELECT * FROM dictionary WHERE eng Like ?',('%{}%'.format(query),))
				for row in c.fetchall():
					traditional = row[0]
					simplified = row[1]
					p = row[2]
					english = row[3]
					english = english[:-3]
					result = [simplified, traditional, p, english]
					if result not in line_list:
						self.add_result(result)

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

	def Add_Card(self):
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