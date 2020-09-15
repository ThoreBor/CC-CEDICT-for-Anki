import sqlite3
import re
import traceback
from mafan import pinyin
import time
from progressbar import *
import sys

conn = sqlite3.connect('database.db')
c = conn.cursor()

def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS dictionary(hanzi_trad TEXT, hanzi_simp TEXT, pinyin TEXT, eng TEXT)')

def data_entry(hanzi_trad, hanzi_simp, p, eng):
	c.execute('INSERT INTO dictionary (hanzi_trad, hanzi_simp, pinyin , eng) VALUES(?, ?, ?, ?)', (hanzi_trad, hanzi_simp, p, eng))


def txt_to_database(fname):
	counter = 0
	total = 0

	with open(fname, encoding="utf8") as f:
		for line in f:
			total += 1

	widgets = [FormatLabel(''), ' ', progressbar.Bar('=', '[', ']'),' ', Percentage(),' ', ETA()]
	bar = ProgressBar(maxval=total, widgets=widgets)
	bar.start()

	with open(fname, encoding="utf8") as f:
		for line in f:
			bar.update(counter)
			widgets[0] = FormatLabel('Entry: '+str("{:,}".format(counter))+"/"+ str("{:,}".format(total)))
			counter = counter +1 
			datalist =  line.split(" ")
			hanzi_trad = datalist[0]
			hanzi_simp = datalist[1]
			p = re.match(r"[^[]*\[([^]]*)\]", line).groups()[0]
			p = pinyin.decode(p)
			eng = line.split("/",1)[1]
			eng = eng.replace("/",", ")
			eng = eng.replace("'","")
			regexp_pattern = '\[[^\]\r\n]*\]'
			st = eng
			a = re.findall(regexp_pattern, st)
			for i in a:
				eng = eng.replace(i, "(" + pinyin.decode(i) + ")")
			data_entry(hanzi_trad, hanzi_simp, p, eng)

	bar.finish()

if len(sys.argv) != 2:
	print("No file name provided. Run database.py filename.txt")
	quit()
fname = sys.argv[1:]
create_table()
txt_to_database(fname[0])
conn.commit()