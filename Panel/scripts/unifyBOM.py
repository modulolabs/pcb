#!/usr/bin/python

import csv, os

config = eval(file('config/placement.json','r').read())

boards = config['boards']
rfqDir = config['rfqDir']

data = []

def rowForPartNum(partNum) :
    for row in data :
        if row['Part Number'] == partNum :
            return row

    data.append({'Part Number': partNum, 'Qty': 0})
    return data[-1]

with open("config/PartDetails.csv","r") as detailsFile :
    reader = csv.DictReader(detailsFile)
    for row in reader :
        row['Qty'] = 0
        data.append(row)

for boardNum,boardInfo in boards.iteritems() :
    boardName,xOffset,yOffset = boardInfo
    filename = "../%s/gerber/%s.bom.csv" % (boardName, boardName)
    with open(filename, 'r') as srcfile :
        reader = csv.DictReader(srcfile)
        for boardRow in reader :
            partNum = boardRow['PARTNUM']

            row = rowForPartNum(partNum)

            if 'Designators' not in row :
                row['Designators'] = []

            for designator in boardRow['Parts'].split(',') :
                row['Designators'].append(str(boardNum) + "-" + designator.strip())

            row['Qty'] += int(boardRow['Qty'])

keys = (['Qty','Qty*250','Part Number', 'Manufacturer', 'Category', 'Description', 'Package', 'Assembly Type',
    'Substitutions', 'Designators', 'Notes'])

for row in data :
    if 'Designators' in row :
        row['Designators'] = ",".join(row['Designators'])
    for key in ['Assembly Type', 'Category', 'Description'] :
        if key not in row :
            row[key] = ''
    row['Qty*250'] = row['Qty']*250

excludedRows = []
with open(os.path.join(rfqDir, 'bom.csv'),'w') as dstfile :
    writer = csv.DictWriter(dstfile, keys, extrasaction='ignore')
    writer.writeheader()

    for row in data :
        if (row['Qty'] == 0) :
            excludedRows.append(row)
            continue
        if row['Assembly Type'] in ['PCB','Exclude'] :
            continue

        writer.writerow(row)

print('The following parts had Qty 0 and were excluded')
for row in excludedRows :
    print('    %s %s %s' % (row['Part Number'], row['Category'], row['Description']))
