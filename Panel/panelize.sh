#!/bin/tcsh

./scripts/unifyCentroid.py

./scripts/unifyBOM.py

# Run gerbmerge to combine the boards
set GERBMERGE=/Users/ekt/integer-labs/gerbmerge/gerbmerge/gerbmerge.py
$GERBMERGE --place-file=tmp/placement.txt config/panelize.cfg

# Run tabify to add tabs and a border to the outline file
./scripts/tabify.py
