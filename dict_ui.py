from PyQt5 import QtCore, QtGui, QtWidgets
from os.path import dirname, join, realpath
from sqlite3 import connect
from aqt import mw
from aqt.qt import *
from .import_file import importfile
from aqt.utils import showInfo

db_path = join(dirname(realpath(__file__)), 'CC-CEDICT_dictionary.db')
conn = connect(db_path)
c = conn.cursor()


class Ui_Dialog(object):
	def setupUi(self, Dialog):

		out=mw.col.decks.all()
		decklist = []
		subdeckslist = []
		for l in out:
		   decklist.append(l['name'])

		out=mw.col.models.all()
		notetypelist = []
		for l in out:
			notetypelist.append(l['name'])

		Dialog.setObjectName("Dialog")
		Dialog.resize(1080, 391)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
		Dialog.setSizePolicy(sizePolicy)
		Dialog.setWindowIcon(QtGui.QIcon(join(dirname(realpath(__file__)), 'icon.png')))

		self.layoutWidget = QtWidgets.QWidget(Dialog)
		self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 641, 371))
		self.layoutWidget.setObjectName("layoutWidget")

		self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.gridLayout.setObjectName("gridLayout")

		self.Query = QtWidgets.QLineEdit(self.layoutWidget)
		font = QtGui.QFont()
		font.setFamily("SimHei")
		font.setPointSize(8)
		self.Query.setFont(font)
		self.Query.setObjectName("Query")
		self.gridLayout.addWidget(self.Query, 0, 0, 1, 1)

		self.Results = QtWidgets.QListWidget(self.layoutWidget)
		font = QtGui.QFont()
		font.setFamily("SimHei")
		font.setPointSize(10)
		self.Results.setFont(font)
		self.Results.setObjectName("Results")
		self.Results.itemClicked.connect(self.listwidgetclicked)
		self.gridLayout.addWidget(self.Results, 2, 0, 1, 5)

		self.Input_Type = QtWidgets.QComboBox(self.layoutWidget)
		self.Input_Type.setObjectName("Input_Type")
		self.Input_Type.addItem("")
		self.Input_Type.addItem("")
		self.Input_Type.addItem("")
		self.Input_Type.currentTextChanged.connect(self.save_config)
		self.gridLayout.addWidget(self.Input_Type, 0, 3, 1, 1)

		self.SearchButton = QtWidgets.QPushButton(self.layoutWidget)
		font = QtGui.QFont()
		font.setPointSize(8)
		self.SearchButton.setFont(font)
		self.SearchButton.setObjectName("SearchButton")
		self.SearchButton.clicked.connect(self.search)
		self.gridLayout.addWidget(self.SearchButton, 0, 2, 1, 1)

		self.checkBox = QtWidgets.QCheckBox(self.layoutWidget)
		self.checkBox.setChecked(False)
		self.checkBox.setObjectName("checkBox")
		self.gridLayout.addWidget(self.checkBox, 0, 4, 1, 1)

		self.AddCard = QtWidgets.QGroupBox(Dialog)
		self.AddCard.setGeometry(QtCore.QRect(660, 210, 411, 172))
		self.AddCard.setObjectName("AddCard")
		self.widget = QtWidgets.QWidget(self.AddCard)
		self.widget.setGeometry(QtCore.QRect(13, 29, 391, 134))
		self.widget.setObjectName("widget")

		self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
		self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
		self.gridLayout_2.setObjectName("gridLayout_2")

		self.Deck_Label = QtWidgets.QLabel(self.widget)
		self.Deck_Label.setObjectName("Deck_Label")
		self.gridLayout_2.addWidget(self.Deck_Label, 0, 0, 1, 1)

		self.Notetype_Label = QtWidgets.QLabel(self.widget)
		self.Notetype_Label.setObjectName("Notetype_Label")
		self.gridLayout_2.addWidget(self.Notetype_Label, 0, 2, 1, 1)

		self.Field1_Label = QtWidgets.QLabel(self.widget)
		self.Field1_Label.setObjectName("Field1_Label")
		self.gridLayout_2.addWidget(self.Field1_Label, 2, 0, 1, 1)

		self.Field2_Label = QtWidgets.QLabel(self.widget)
		self.Field2_Label.setObjectName("Field2_Label")
		self.gridLayout_2.addWidget(self.Field2_Label, 2, 1, 1, 1)

		self.Field3_Label = QtWidgets.QLabel(self.widget)
		self.Field3_Label.setObjectName("Field3_Label")
		self.gridLayout_2.addWidget(self.Field3_Label, 2, 2, 1, 1)

		self.Field4_Label = QtWidgets.QLabel(self.widget)
		self.Field4_Label.setObjectName("Field4_Label")
		self.gridLayout_2.addWidget(self.Field4_Label, 2, 3, 1, 1)

		self.Field1 = QtWidgets.QComboBox(self.widget)
		self.Field1.setObjectName("Field1")
		self.Field1.addItem("")
		self.Field1.addItem("")
		self.Field1.addItem("")
		self.Field1.addItem("")
		self.Field1.currentTextChanged.connect(self.save_config)
		self.gridLayout_2.addWidget(self.Field1, 3, 0, 1, 1)

		self.Field2 = QtWidgets.QComboBox(self.widget)
		self.Field2.setObjectName("Field2")
		self.Field2.addItem("")
		self.Field2.addItem("")
		self.Field2.addItem("")
		self.Field2.addItem("")
		self.Field2.currentTextChanged.connect(self.save_config)
		self.gridLayout_2.addWidget(self.Field2, 3, 1, 1, 1)

		self.Field3 = QtWidgets.QComboBox(self.widget)
		self.Field3.setObjectName("Field3")
		self.Field3.addItem("")
		self.Field3.addItem("")
		self.Field3.addItem("")
		self.Field3.addItem("")
		self.Field3.addItem("")
		self.Field3.currentTextChanged.connect(self.save_config)
		self.gridLayout_2.addWidget(self.Field3, 3, 2, 1, 1)

		self.Field4 = QtWidgets.QComboBox(self.widget)
		self.Field4.setObjectName("Field4")
		self.Field4.addItem("")
		self.Field4.addItem("")
		self.Field4.addItem("")
		self.Field4.addItem("")
		self.Field4.addItem("")
		self.Field4.currentTextChanged.connect(self.save_config)
		self.gridLayout_2.addWidget(self.Field4, 3, 3, 1, 1)

		self.About = QtWidgets.QPushButton(self.widget)
		self.About.setObjectName("About")
		self.About.clicked.connect(self.about)
		self.gridLayout_2.addWidget(self.About, 4, 3, 1, 1)

		self.Deck = QtWidgets.QComboBox(self.widget)
		self.Deck.setObjectName("Deck")
		for i in decklist:
			self.Deck.addItem(str(i))
		self.gridLayout_2.addWidget(self.Deck, 1, 0, 1, 2)
		self.Deck.currentTextChanged.connect(self.save_config)

		self.Notetype = QtWidgets.QComboBox(self.widget)
		self.Notetype.setObjectName("Notetype")
		for i in notetypelist:
			self.Notetype.addItem(str(i))
		self.gridLayout_2.addWidget(self.Notetype, 1, 2, 1, 2)
		self.Notetype.currentTextChanged.connect(self.save_config)

		self.Add = QtWidgets.QPushButton(self.widget)
		self.Add.setObjectName("Add")
		self.Add.clicked.connect(self.Add_Card)
		self.gridLayout_2.addWidget(self.Add, 4, 0, 1, 3)

		self.scrollArea = QtWidgets.QScrollArea(Dialog)
		self.scrollArea.setGeometry(QtCore.QRect(660, 10, 411, 191))
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setObjectName("scrollArea")
		self.scrollAreaWidgetContents = QtWidgets.QWidget()
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 409, 189))
		self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
		self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
		self.verticalLayout.setObjectName("verticalLayout")

		self.Hanzi = QtWidgets.QLabel(self.scrollAreaWidgetContents)
		font = QtGui.QFont()
		font.setFamily("SimSun")
		font.setPointSize(20)
		self.Hanzi.setFont(font)
		self.Hanzi.setWordWrap(True)
		self.Hanzi.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
		self.Hanzi.setObjectName("Hanzi")
		self.verticalLayout.addWidget(self.Hanzi)

		self.Pinyin = QtWidgets.QLabel(self.scrollAreaWidgetContents)
		font = QtGui.QFont()
		font.setFamily("Times New Roman")
		font.setPointSize(12)
		self.Pinyin.setFont(font)
		self.Pinyin.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
		self.Pinyin.setObjectName("Pinyin")
		self.verticalLayout.addWidget(self.Pinyin)
		
		self.English = QtWidgets.QLabel(self.scrollAreaWidgetContents)
		font = QtGui.QFont()
		font.setFamily("Times New Roman")
		font.setPointSize(12)
		self.English.setFont(font)
		self.English.setObjectName("English")
		self.verticalLayout.addWidget(self.English)
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)

		self.retranslateUi(Dialog)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		config = mw.addonManager.getConfig(__name__)
		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "CC-CEDICT for Anki"))

		self.Input_Type.setItemText(0, _translate("Dialog", "Simplified"))
		self.Input_Type.setItemText(1, _translate("Dialog", "Traditional"))
		self.Input_Type.setItemText(2, _translate("Dialog", "English"))
		self.Input_Type.setCurrentText(config["search_config"])

		self.Deck.setCurrentText(config["deck_config"])

		self.Notetype.setCurrentText(config["notetype_config"])

		self.checkBox.setText(_translate("Dialog", "Show only exact matches"))

		self.SearchButton.setText(_translate("Dialog", "Search"))

		self.Hanzi.setText(_translate("Dialog", "漢字\n""汉字"))
		self.Pinyin.setText(_translate("Dialog", "Pinyin"))
		self.English.setText(_translate("Dialog", "English"))

		self.AddCard.setTitle(_translate("Dialog", "Add Card"))

		self.Deck_Label.setText(_translate("Dialog", "Deck:"))
		self.Notetype_Label.setText(_translate("Dialog", "Notetype:"))

		self.Field1.setItemText(0, _translate("Dialog", "Simplified"))
		self.Field1.setItemText(1, _translate("Dialog", "Traditional"))
		self.Field1.setItemText(2, _translate("Dialog", "Pinyin"))
		self.Field1.setItemText(3, _translate("Dialog", "English"))
		self.Field1.setCurrentText(config["field_1_config"])
		self.Field1_Label.setText(_translate("Dialog", "Field 1:"))

		self.Field2.setItemText(0, _translate("Dialog", "Traditional"))
		self.Field2.setItemText(1, _translate("Dialog", "Simplified"))
		self.Field2.setItemText(2, _translate("Dialog", "Pinyin"))
		self.Field2.setItemText(3, _translate("Dialog", "English"))
		self.Field2.setCurrentText(config["field_2_config"])
		self.Field2_Label.setText(_translate("Dialog", "Field 2:"))

		self.Field3.setItemText(0, _translate("Dialog", "Pinyin"))
		self.Field3.setItemText(1, _translate("Dialog", "Simplified"))
		self.Field3.setItemText(2, _translate("Dialog", "Traditional"))
		self.Field3.setItemText(3, _translate("Dialog", "English"))
		self.Field3.setItemText(4, _translate("Dialog", "Nothing"))
		self.Field3.setCurrentText(config["field_3_config"])
		self.Field3_Label.setText(_translate("Dialog", "Field 3:"))

		self.Field4.setItemText(0, _translate("Dialog", "English"))
		self.Field4.setItemText(1, _translate("Dialog", "Simplified"))
		self.Field4.setItemText(2, _translate("Dialog", "Traditional"))
		self.Field4.setItemText(3, _translate("Dialog", "Pinyin"))
		self.Field4.setItemText(4, _translate("Dialog", "Nothing"))
		self.Field4.setCurrentText(config["field_4_config"])
		self.Field4_Label.setText(_translate("Dialog", "Field 4:"))

		self.About.setText(_translate("Dialog", "About"))

		self.Add.setText(_translate("Dialog", "Add card"))
	
		c.execute('SELECT * FROM dictionary ORDER BY RANDOM() LIMIT 20')
		for row in c.fetchall():
			traditional = row[0]
			simplified = row[1]
			p = row[2]
			english = row[3]
			english = english[:-3]
			line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
			self.Results.addItem(line)

	def search(self):
		line_list = []
		self.Results.clear()
		query = self.Query.text()

		if self.Input_Type.currentText() == "Traditional":
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
				self.Results.addItem(line)
			#partial match
			c.execute('SELECT * FROM dictionary WHERE hanzi_trad Like ?',('%{}%'.format(query),))
			if self.checkBox.isChecked():
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
						self.Results.addItem(line)

		if self.Input_Type.currentText() == "Simplified":
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
				self.Results.addItem(line)

			#partial
			c.execute('SELECT * FROM dictionary WHERE hanzi_simp Like ?',('%{}%'.format(query),))
			if self.checkBox.isChecked():
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
						self.Results.addItem(line)

		if self.Input_Type.currentText() == "English":
			c.execute('SELECT * FROM dictionary WHERE eng=?', (query,))
			for row in c.fetchall():
				traditional = row[0]
				simplified = row[1]
				p = row[2]
				english = row[3]
				english = english[:-3]
				line = str(simplified + "\t" + traditional + "\t" + p + "\t" + english)
				line_list.append(line)
				self.Results.addItem(line)
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
						self.Results.addItem(line)

			if self.checkBox.isChecked():
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
						self.Results.addItem(line)


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
			self.Hanzi.setText(trad+"\n"+simp)
		else:
			self.Hanzi.setText(trad)
		self.Pinyin.setText(pinyin)
		self.English.setText(english_entry)
		self.English.adjustSize()
		self.Pinyin.adjustSize()
		self.Hanzi.adjustSize()

	def Add_Card(self):
		to_add =  open(join(dirname(realpath(__file__)), 'to_add.txt'), "w", encoding="utf-8")
		Hanzi = self.Hanzi.text()
		Hanzi = Hanzi.split("\n")
		if len(Hanzi) > 1:
			trad = Hanzi[0]
			simp = Hanzi[1]
		else:
			trad = Hanzi[0]
			simp = Hanzi[0]
		Pinyin = self.Pinyin.text()
		English = self.English.text()
		English = English.replace("\n", "，")
		English = English[:-1]

		# Wrap the english field in '"'. Escape the " character in the value.
		# This is needed to import the card correctly when a value contains the ',' character or others
		# that are used to separate fields.
		# The other three fields are unlikely to contain this character.
		# see https://docs.ankiweb.net/#/importing
		English = English.replace('"', '""')
		English = '"{}"'.format(English)


		if self.Field1.currentText() == "Simplified":
			Field1_content = simp
		if self.Field1.currentText() == "Traditional":
			Field1_content = trad
		if self.Field1.currentText() == "Pinyin":
			Field1_content = Pinyin
		if self.Field1.currentText() == "English":
			Field1_content = English

		if self.Field2.currentText() == "Simplified":
			Field2_content = simp
		if self.Field2.currentText() == "Traditional":
			Field2_content = trad
		if self.Field2.currentText() == "Pinyin":
			Field2_content = Pinyin
		if self.Field2.currentText() == "English":
			Field2_content = English

		if self.Field3.currentText() == "Simplified":
			Field3_content = simp
		if self.Field3.currentText() == "Traditional":
			Field3_content = trad
		if self.Field3.currentText() == "Pinyin":
			Field3_content = Pinyin
		if self.Field3.currentText() == "English":
			Field3_content = English
		if self.Field3.currentText() == "Nothing":
			Field3_content = ""

		if self.Field4.currentText() == "Simplified":
			Field4_content = simp
		if self.Field4.currentText() == "Traditional":
			Field4_content = trad
		if self.Field4.currentText() == "Pinyin":
			Field4_content = Pinyin
		if self.Field4.currentText() == "English":
			Field4_content = English
		if self.Field4.currentText() == "Nothing":
			Field4_content = ""

		Card = str(Field1_content + "\t" + Field2_content + "\t" + Field3_content + "\t" + Field4_content)
		to_add.write(Card)
		to_add.close()
		importfile(self.Deck.currentText(), self.Notetype.currentText())

	def save_config(self):
		search_config = self.Input_Type.currentText()
		deck_config = self.Deck.currentText()
		notetype_config = self.Notetype.currentText()
		field_1_config = self.Field1.currentText()
		field_2_config = self.Field2.currentText()
		field_3_config = self.Field3.currentText()
		field_4_config = self.Field4.currentText()
		config = {"search_config": search_config, "deck_config": deck_config, "notetype_config": notetype_config, 
		"field_1_config": field_1_config, "field_2_config": field_2_config, "field_3_config": field_3_config, "field_4_config": field_4_config}
		mw.addonManager.writeConfig(__name__, config)


	def about(self):
		showInfo('<h3>CC-CEDICT for Anki v1.2</h3><br>This add-on uses the <a href="https://cc-cedict.org/wiki/">CC-CEDICT</a> dictionary. It is licensed under the <a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share Alike 3.0 License</a>.<br>The code for the add-on is available on <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki">GitHub.</a> It is licensed under the <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/blob/master/LICENSE">MIT License.</a><br><br>If you like this add-on, rate and review it on <a href="https://ankiweb.net/shared/info/418828045">Anki Web</a>. If you want to report a bug, or make a feature request, please create a new <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/issues">issue</a> on GitHub.<br><div>Icon made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><br>© Thore Tyborski 2020')




class start(QDialog):
	def __init__(self, parent=None):
		self.parent = parent
		QDialog.__init__(self, parent, Qt.Window)
		self.dialog = Ui_Dialog()
		self.dialog.setupUi(self)
