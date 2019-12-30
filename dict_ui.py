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
		Dialog.resize(1103, 348)
		Dialog.setWindowIcon(QtGui.QIcon(join(dirname(realpath(__file__)), 'icon.png')))
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
		Dialog.setSizePolicy(sizePolicy)

		self.layoutWidget = QtWidgets.QWidget(Dialog)
		self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 701, 331))
		self.layoutWidget.setObjectName("layoutWidget")
		self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.gridLayout.setObjectName("gridLayout")

		self.SearchButton = QtWidgets.QPushButton(self.layoutWidget)
		font = QtGui.QFont()
		font.setPointSize(8)
		self.SearchButton.setFont(font)
		self.SearchButton.setObjectName("SearchButton")
		self.SearchButton.clicked.connect(self.search)
		self.gridLayout.addWidget(self.SearchButton, 0, 2, 1, 1)

		self.Results = QtWidgets.QListWidget(self.layoutWidget)
		font = QtGui.QFont()
		font.setFamily("SimHei")
		self.Results.setFont(font)
		self.Results.setObjectName("Results")
		self.Results.itemClicked.connect(self.listwidgetclicked)
		self.gridLayout.addWidget(self.Results, 1, 0, 1, 5)

		self.Query = QtWidgets.QLineEdit(self.layoutWidget)
		font = QtGui.QFont()
		font.setFamily("SimHei")
		font.setPointSize(8)
		self.Query.setFont(font)
		self.Query.setObjectName("Query")
		self.gridLayout.addWidget(self.Query, 0, 0, 1, 1)

		self.Input_Type = QtWidgets.QComboBox(self.layoutWidget)
		self.Input_Type.setObjectName("Input_Type")
		self.Input_Type.addItem("")
		self.Input_Type.addItem("")
		self.Input_Type.addItem("")
		self.gridLayout.addWidget(self.Input_Type, 0, 3, 1, 1)

		self.checkBox = QtWidgets.QCheckBox(self.layoutWidget)
		self.checkBox.setChecked(False)
		self.checkBox.setObjectName("checkBox")
		self.gridLayout.addWidget(self.checkBox, 0, 4, 1, 1)

		self.layoutWidget1 = QtWidgets.QWidget(Dialog)
		self.layoutWidget1.setGeometry(QtCore.QRect(721, 20, 371, 321))
		self.layoutWidget1.setObjectName("layoutWidget1")
		self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget1)
		self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
		self.gridLayout_2.setObjectName("gridLayout_2")

		self.Hanzi = QtWidgets.QLabel(self.layoutWidget1)
		font = QtGui.QFont()
		font.setFamily("SimSun")
		font.setPointSize(20)
		self.Hanzi.setFont(font)
		self.Hanzi.setObjectName("Hanzi")
		self.Hanzi.setWordWrap(True)
		self.gridLayout_2.addWidget(self.Hanzi, 0, 0, 1, 4)

		self.scrollArea = QtWidgets.QScrollArea(self.layoutWidget1)
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setObjectName("scrollArea")
		self.scrollAreaWidgetContents = QtWidgets.QWidget()
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 367, 146))
		self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

		self.English = QtWidgets.QLabel(self.scrollAreaWidgetContents)
		self.English.setGeometry(QtCore.QRect(0, 0, 59, 22))
		font = QtGui.QFont()
		font.setFamily("Times New Roman")
		font.setPointSize(12)
		self.English.setFont(font)
		self.English.setWordWrap(True)
		self.English.setObjectName("English")
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)
		self.gridLayout_2.addWidget(self.scrollArea, 2, 0, 1, 4)

		self.Pinyin = QtWidgets.QLabel(self.layoutWidget1)
		font = QtGui.QFont()
		font.setFamily("Times New Roman")
		font.setPointSize(12)
		self.Pinyin.setFont(font)
		self.Pinyin.setObjectName("Pinyin")
		self.gridLayout_2.addWidget(self.Pinyin, 1, 0, 1, 4)

		self.About = QtWidgets.QPushButton(self.layoutWidget1)
		self.About.setObjectName("About")
		self.About.clicked.connect(self.about)
		self.gridLayout_2.addWidget(self.About, 4, 3, 1, 1)

		self.Deck = QtWidgets.QComboBox(self.layoutWidget1)
		self.Deck.setObjectName("Deck")
		for i in decklist:
			self.Deck.addItem(str(i))
		self.gridLayout_2.addWidget(self.Deck, 3, 0, 1, 2)

		self.Notetype = QtWidgets.QComboBox(self.layoutWidget1)
		self.Notetype.setObjectName("Notetype")
		for i in notetypelist:
			self.Notetype.addItem(str(i))
		self.gridLayout_2.addWidget(self.Notetype, 3, 2, 1, 2)

		self.Add = QtWidgets.QPushButton(self.layoutWidget1)
		self.Add.setObjectName("Add")
		self.Add.clicked.connect(self.Add_Card)
		self.gridLayout_2.addWidget(self.Add, 4, 0, 1, 3)

		self.retranslateUi(Dialog)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "CC-CEDICT for Anki"))
		self.SearchButton.setText(_translate("Dialog", "Search"))
		self.Input_Type.setItemText(0, _translate("Dialog", "Simplified"))
		self.Input_Type.setItemText(1, _translate("Dialog", "Traditional"))
		self.Input_Type.setItemText(2, _translate("Dialog", "English"))
		self.checkBox.setText(_translate("Dialog", "Show only exact matches"))
		self.Hanzi.setText(_translate("Dialog", "漢字\n""汉字"))
		self.Pinyin.setText(_translate("Dialog", "Pinyin"))
		self.English.setText(_translate("Dialog", "English"))
		self.Add.setText(_translate("Dialog", "Add card"))
		self.About.setText(_translate("Dialog", "About"))
	
		c.execute('SELECT * FROM dictionary ORDER BY RANDOM() LIMIT 15')
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
		Card = str(trad + "\t" + simp + "\t" + Pinyin + "\t" + English)
		to_add.write(Card)
		to_add.close()
		importfile(self.Deck.currentText(), self.Notetype.currentText())

	def about(self):
		showInfo('<h3>CC-CEDICT for Anki v1.0</h3><br>This add-on uses the <a href="https://cc-cedict.org/wiki/">CC-CEDICT</a> dictionary. It is licensed under the <a href="https://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share Alike 3.0 License</a>.<br>The code for the add-on is available on <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki">GitHub.</a> It is licensed under the <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/blob/master/LICENSE">MIT License.</a><br><br>If you like this add-on, rate and review it on <a href="https://ankiweb.net/shared/info/418828045">Anki Web</a>. If you want to report a bug, or make a feature request, please create a new <a href="https://github.com/ThoreBor/CC-CEDICT-for-Anki/issues">issue</a> on GitHub.<br><div>Icon made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><br>© Thore Tyborski 2019')




class start(QDialog):
	def __init__(self, parent=None):
		self.parent = parent
		QDialog.__init__(self, parent, Qt.Window)
		self.dialog = Ui_Dialog()
		self.dialog.setupUi(self)
