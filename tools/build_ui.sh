#!/bin/bash

set -e

mkdir -p ../forms/

#pyqt6

echo "Generating pyqt6 forms..."
for i in ../designer/*.ui
do
    base=$(basename $i .ui)
    py="../forms/${base}.py"
    if [ $i -nt $py ]; then
        echo " * "$py
        pyuic6 $i -o $py
    fi
done