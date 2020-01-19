# CC-CEDICT for Anki v1.1 Copyright 2020 Thore Tyborski

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from aqt import mw
from aqt.utils import showInfo, tooltip, askUser
from PyQt5.QtWidgets import QAction, QMenu
from aqt.qt import *
from os.path import dirname, join, realpath
import requests
from bs4 import BeautifulSoup
import webbrowser
from .dict_ui import start

this_version = "v1.1"

def UI():
	s = start()
	if s.exec():
		pass

def Update():
	try:
		url = 'https://chinesewordsfinderupdates.netlify.com'
		headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36 OPR/62.0.3331.116'}
		page = requests.get(url, headers=headers)
		soup = BeautifulSoup(page.content, 'html.parser')
		version = soup.find(id='dict_version').get_text()
		log = soup.find(id='dict_changelog').get_text()
		log_list = log.split(',')
		log = ""
		for i in log_list:
			log = log + "- " + i + "<br>"
	except:
		return
	if version != this_version:
		info = "You can update CC-CEDICT for Anki to version %(version)s. You are currently using version %(this_version)s.<br><br><b>Changes:</b><br>%(log)s <br><br><b>Do you want to update now?</b>" % {'version':version, 'this_version': this_version, 'log':log}

		if not askUser(info, title='Update!'):
			return
		else:
			download()
	else:
		pass

def download():
	try:
		mw.mgr = mw.addonManager
		updated = ['418828045']
		mw.mgr.downloadIds(updated)
		tooltip("CC-CEDICT for Anki was updated successfully. Please restart Anki.")
	except:
		tooltip("Download failed...")


def Main():
	Update()
	UI()
  


action = QAction("CC-CEDICT for Anki", mw)
action.triggered.connect(Main)
mw.form.menuTools.addAction(action)
action.setShortcut(QKeySequence("Ctrl+D"))