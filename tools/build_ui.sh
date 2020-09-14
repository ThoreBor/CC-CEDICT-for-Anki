# This Code was originally commited to https://github.com/ThoreBor/Anki_Leaderboard by https://github.com/zjosua
#!/bin/bash

set -e

if [ ! -d "designer" ]
then
    echo "Please run this from the project root"
    exit
fi

mkdir -p forms

echo "Generating forms..."
for i in designer/*.ui
do
    base=$(basename $i .ui)
    py="forms/${base}.py"
    if [ $i -nt $py ]; then
        echo " * "$py
        pyuic5 --from-imports $i -o $py
    fi
done

echo "Building resources.."
pyrcc5 designer/icons.qrc -o forms/icons_rc.py
