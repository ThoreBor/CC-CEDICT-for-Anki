from aqt import mw
from aqt.utils import showInfo
from aqt.qt import qtmajor

from PyQt6.QtWidgets import QCompleter

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
	"color_pinyin": config["color_pinyin"], "tags": config["tags"]}
	mw.addonManager.writeConfig(__name__, config)

def find_tags(self):
	all_tags = mw.col.db.all("select tags from notes")
	tags = []
	for i in all_tags:
		tag = i[0].strip()
		if tag not in tags and tag and "leech" not in tag:
			tags.append(tag)
	completer = QCompleter(tags)
	self.dialog.tags.setCompleter(completer)

def save_config(self):
	deck_config = self.dialog.Deck.currentText()
	notetype_config = self.dialog.Notetype.currentText()
	field_1_config = self.dialog.Field1.currentText()
	field_2_config = self.dialog.Field2.currentText()
	field_3_config = self.dialog.Field3.currentText()
	field_4_config = self.dialog.Field4.currentText()
	color_pinyin_config = self.dialog.color_pinyin.isChecked()
	tags_config = self.dialog.tags.text()
	config = {
		"deck_config": deck_config, 
		"notetype_config": notetype_config, 
		"field_1_config": field_1_config, 
		"field_2_config": field_2_config, 
		"field_3_config": field_3_config, 
		"field_4_config": field_4_config,
		"color_pinyin": color_pinyin_config,
		"tags": tags_config
	}
	mw.addonManager.writeConfig(__name__, config)

def about(self):
	about_text = """
<h3>CC-CEDICT for Anki v1.4.1</h3>
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