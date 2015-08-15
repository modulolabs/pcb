#!/usr/bin/env python

import csv, os

config = eval(file('config/placement.json','r').read())

boards = config['boards']
rfqDir = config['rfqDir']

keys = ['RefDes','Layer','LocationX','LocationY','Rotation']

with open(os.path.join(rfqDir,'centroid.csv'),'w') as dstfile :
    writer = csv.DictWriter(dstfile, keys, extrasaction='ignore')
    writer.writeheader()

    for boardNum,boardInfo in boards.iteritems() :
        boardName,xOffset,yOffset = boardInfo
        filename = "../%s/gerber/%s.centroid.csv" % (boardName, boardName)
        with open(filename, 'r') as srcfile :
            reader = csv.DictReader(srcfile)
            for row in reader :
                row['LocationX'] = float(row['LocationX'])+xOffset
                row['LocationY'] = float(row['LocationY'])+yOffset
                row['LocationX'] = "%.3f" % row['LocationX']
                row['LocationY'] = "%.3f" % row['LocationY']
                row['RefDes'] = "%d-%s" % (boardNum, row['RefDes'])
                writer.writerow(row)
