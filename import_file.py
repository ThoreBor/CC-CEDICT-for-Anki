from anki.importing import TextImporter
from aqt import mw
from os.path import dirname, join, realpath
from aqt.utils import showWarning, tooltip
from sqlite3 import connect

def importfile (deck, type):
	try:
		file = join(dirname(realpath(__file__)), "to_add.txt")
		did = mw.col.decks.id(deck)
		mw.col.decks.select(did)
		m = mw.col.models.byName(type)
		deck = mw.col.decks.get(did)
		deck['mid'] = m['id']
		mw.col.decks.save(deck)
		m['did'] = did
		ti = TextImporter(mw.col, file)
		ti.initMapping()
		ti.run()
		tooltip("One card was added.")
	except:
		showWarning("Error. Make sure that you use a notetype with four fields (Traditional, Simplified, Pinyin and English).")