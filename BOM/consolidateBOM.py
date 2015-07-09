#!/usr/bin/python

import csv

boards = {
    'Controller': 500,
    'Display': 500,
    'Base': 500,
    #'SparkBase': 250,
    'Knob': 500,
    'MotorDriver': 250,
    'Joystick': 250,
    'TempProbe': 250,
    'IRRemote': 100,
    'BlankSlate': 100
}

data = {0: {'Description': 'Product Qty'}}


for name,qty in boards.iteritems() :
    data[0][name] = int(qty)

for name,qty in boards.iteritems() :
    filename = "../%s/%s.csv" % (name, name)
    with open(filename, 'r') as srcfile :
        reader = csv.DictReader(srcfile)
        for row in reader :
            partNum = row['PARTNUM']
            if partNum not in data :
                data[partNum] = row.copy()
                data[partNum]['Qty'] = 0
                del data[partNum]['Parts']

            data[partNum]['Qty'] += qty*int(row['Qty'])
            data[partNum][name] = qty*int(row['Qty'])

keys = (['Qty','Value','Device','Package','Description','PARTNUM', 'VALUE'] +
    boards.keys())
print keys
with open('ConsolidatedBOM.csv','w') as dstfile :
    writer = csv.DictWriter(dstfile, keys, extrasaction='ignore')
    writer.writeheader()
    for partNum,row in data.items() :
       writer.writerow(row)
