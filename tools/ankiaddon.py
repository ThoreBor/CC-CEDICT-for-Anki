import zipfile
import os
from pathlib import Path
import shutil

root = Path(__file__).parents[1]

# create output folder
if not os.path.exists(f"{root}/releases"):
   os.makedirs(f"{root}/releases")

# remove pycache
shutil.rmtree(f"{root}/forms/__pycache__", ignore_errors=True)
shutil.rmtree(f"{root}/cedict/__pycache__", ignore_errors=True)

# create .ankiaddon

data = [
   "-c",
   f"{root}/releases/AnkiLeaderboard.ankiaddon",
   f"{root}/__init__.py",
   f"{root}/config.json",
   f"{root}/manifest.json",
   f"{root}/License.txt",
   f"{root}/CC-CEDICT Info.txt",
   f"{root}/hanzidentifier_licence.txt",
   f"{root}/zhon_licence.txt",
   f"{root}/zhon_licence.txt",
   f"{root}/forms",
   f"{root}/cedict",
   f"{root}/third_party",
   f"{root}/designer",
   f"{root}/CC-CEDICT_dictionary.db",
   ]

zipfile.main(data)