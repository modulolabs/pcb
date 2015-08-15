#!/usr/bin/python

import sys, os

boardFile= sys.argv[1]

eagle="/Applications/EAGLE-7.3.0/EAGLE.app/Contents/MacOS/EAGLE"

layerMap = [
    (".tcream.ger", ["-dGERBER_RS274X","tCream"]),
    (".bcream.ger", ["-dGERBER_RS274X","bCream"]),
    (".topsoldermask.ger", ["-dGERBER_RS274X", "tStop"]),
    (".bottomsoldermask.ger", ["-dGERBER_RS274X", "bStop"]),
    (".toplayer.ger", ["-dGERBER_RS274X", "Top","Pads","Vias"]),
    (".bottomlayer.ger", ["-dGERBER_RS274X", "Bottom","Pads","Vias"]),
    (".topsilkscreen.ger", ["-dGERBER_RS274X", "tPlace","tNames"]),
    (".bottomsilkscreen.ger", ["-dGERBER_RS274X", "bPlace","bNames"]),
    (".boardoutline.ger", ["-dGERBER_RS274X", "Dimension"]),
    (".drills.xln", ["-dEXCELLON_24", "Drills","Holes"]),
    (".topplace.eps", ["-dEPS", "tPlace","tNames","tValues","Dimension","Pads","tCream"]),
    (".bottomplace.eps", ["-dEPS", "-m","bPlace","bNames","bValues","Dimension","Pads","bCream"])
]

dirName = os.path.dirname(os.path.abspath(boardFile))
fileName = os.path.basename(boardFile)
gerberDir = os.path.join(dirName,"gerber")
if not os.path.exists(gerberDir) :
    os.makedirs(gerberDir)

for ext,options in layerMap :
    outFilename = os.path.join(dirName, "gerber", fileName.replace(".brd",ext))
    cmd = " ".join([eagle,"-X","-o",outFilename,boardFile] + options)
    print cmd
    os.system(cmd)


centroidFilename = os.path.join(gerberDir,fileName.replace(".brd",".centroid.csv"))
bomFilename = os.path.join(gerberDir,fileName.replace(".brd",".bom.csv"))

centroidCmd = 'edit .brd; run ~/integer-labs/pcb/Panel/scripts/centroid.ulp %s ;' % centroidFilename
bomCmd = 'edit .sch; run ~/integer-labs/pcb/Panel/scripts/bom.ulp %s ;' % bomFilename
quitCmd = "quit;"
cmd = " ".join([eagle,"-C",'"' + centroidCmd + bomCmd + quitCmd + '"',boardFile])
print cmd
os.system(cmd)
