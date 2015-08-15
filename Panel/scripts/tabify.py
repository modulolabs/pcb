#!/usr/bin/env python

import sys, re, os

"""
This script processes a gerber outline file produced by gerbmerge.
It adds tabs between boards and a border around the entire panel.

It operates as a chain of filters. Each filter has methods for
certain gerber commands and is responsible for processing those
commands and calling the next filter. The first filter reads
the source gerber file and the last filter writes the results.
"""

class Reader(object) :
    def __init__(self, writer, filename) :
        self.writer = writer
        self.inFile = file(filename, "r")

    def read(self) :
        drawRegExp = re.compile("X(?P<X>[0-9]+)Y(?P<Y>[0-9]+)D(?P<D>[0-9]+).*")
        apertureRegExp = re.compile("%ADD(?P<D>[0-9]+)C,(?P<width>[0-9]*\.[0-9]*)\*%")

        for line in self.inFile :
            match = drawRegExp.match(line)
            if match is not None :
                X,Y,D = [int(x) for x in match.groups()]
                pos = (X*1e-5, Y*1e-5)
                if (D == 2) :
                    self.writer.moveTo(pos)
                elif (D == 1) :
                    self.writer.drawTo(pos)
                else :
                    self.writer.write(line)
                continue

            match = apertureRegExp.match(line)
            if match is not None :
                D,width = match.groups()
                self.writer.write("%%ADD%sC,0.00500*%%\n" % D)
                continue

            if line.strip() != "M02*" :
                self.writer.write(line)

        self.writer.endFile()

class BorderFilter(object) :

    def __init__(self, writer, borderPoints) :
        self.writer = writer
        self.borderPoints = borderPoints

    def moveTo(self, point) :
        self.writer.moveTo(point)

    def drawTo(self, point) :
        self.writer.drawTo(point)

    def write(self, line) :
        self.writer.write(line)

    def endFile(self) :
        # Draw the inner border
        minX = 1e6
        maxX = 1e-6
        minY = 1e6
        maxY = 1e-6

        self.writer.moveTo(self.borderPoints[-1])
        for point in self.borderPoints :
            self.writer.drawTo(point)
            minX = min(minX, point[0])
            maxX = max(maxX, point[0])
            minY = min(minY, point[1])
            maxY = max(maxY, point[1])

        margin=.2
        self.writer.moveTo((minX-margin, minY-margin))
        self.writer.drawTo((maxX+margin, minY-margin))
        self.writer.drawTo((maxX+margin, maxY+margin))
        self.writer.drawTo((minX-margin, maxY+margin))
        self.writer.drawTo((minX-margin, minY-margin))

        self.writer.endFile()

class Tab() :

    def __init__(self, pos) :
        self.pos = pos
        self.intersections = []
        self.bottomY = None
        self.topY = None

    def __getitem__(self, i) :
        return self.pos[i]

    def __setitem__(self, i, v) :
        self.pos[i] = v

class TabsFilter(object) :
    def __init__(self, writer, tabs):
        self.tabs = tabs
        self.writer = writer
        self.currentPos = (0,0)
        self.tabBottom = -.05
        self.tabTop = .2
        self.tabWidth = .1

    def getTabIntersections(self, tab, p0, p1) :
        if abs(p0[1]-p1[1] > .001) : # Not a horizontal line
            return None
        if (p0[1] < tab[1]+self.tabBottom) : # Below the tab bottom
            return None
        if (p0[1] > tab[1]+self.tabTop) : # Above the tab top
            return None
        if (p0[0] < tab[0] and p1[0] < tab[0]) : #Left of the tab
            return None
        if (p0[0] > tab[0]+self.tabWidth and p1[0] > tab[0]+self.tabWidth) : #Right of the tab
            return None

        if (tab.bottomY is None) :
            tab.bottomY = p0[1]
        elif (tab.bottomY < p0[1]) :
            tab.topY = p0[1]
        else :
            tab.topY = tab.bottomY
            tab.bottomY = p0[1]

        if (p0[0] < p1[0]) : # First point is to the left of the second
            return [(tab[0], p0[1]), (tab[0]+self.tabWidth, p0[1])]
        else :
            return [(tab[0]+self.tabWidth, p0[1]), (tab[0], p0[1])]

    def write(self, line) :
        self.writer.write(line)

    def moveTo(self, point) :
        self.writer.moveTo(point)
        self.currentPos = point

    def _drawToCheckTabs(self, point, tabs) :
        for i in range(len(tabs)) :
            tab = tabs[i]
            intersections = self.getTabIntersections(tab, self.currentPos, point)
            if intersections is not None :
                self._drawToCheckTabs(intersections[0], tabs[i+1:])
                self.writer.moveTo(intersections[1])

        self.currentPos = point
        self.writer.drawTo(point)

    def drawTo(self, point) :
        self._drawToCheckTabs(point, self.tabs)

    def endFile(self) :
        for tab in self.tabs :
            if (tab.bottomY is not None and tab.topY is not None) :
                self.writer.moveTo((tab.pos[0], tab.bottomY))
                self.writer.drawTo((tab.pos[0], tab.topY))
                self.writer.moveTo((tab.pos[0]+self.tabWidth, tab.bottomY))
                self.writer.drawTo((tab.pos[0]+self.tabWidth, tab.topY))

        self.writer.endFile()

class Writer(object) :
    def __init__(self, filename) :
        self.outFile = file(filename,"w")

    def _formatNumber(self, x) :
        return ("%2.5f" % x).replace(".", "")

    def _formatPoint(self, point) :
        return "X%sY%s" % (self._formatNumber(point[0]), self._formatNumber(point[1]))

    def write(self, line) :
        self.outFile.write(line)

    def moveTo(self, point) :
        self.currentPos = point
        self.outFile.write("%sD02*\n" % (self._formatPoint(point)))

    def drawTo(self, point) :
        self.outFile.write("%sD01*\n" % (self._formatPoint(point)))
        self.currentPos = point

    def endFile(self) :
        self.outFile.write("M02*\n")
        self.outFile.close()


if __name__ == '__main__' :

    config = eval(file('config/placement.json','r').read())

    rfqDir = config['rfqDir']
    gerberDir = config['gerberDir']

    # The last object in the chain writes the new gerber file
    writer = Writer(os.path.join(gerberDir,"Modulo.boardoutline.ger"))

    # Lower left hand corner of each tab
    tabs = [(.6, 6.3), (2.1, 6.3),             (5.1, 6.3),             (7, 6.3),
            (.6, 3.8), (2.1, 3.8), (3.6, 3.8), (5.1, 3.7),             (7, 3.7),
            (.6, 2.5), (2.1, 2.5), (3.6, 2.5),
            (.6, 1.2), (2.1, 1.2), (3.6, 1.2), (5.1, 1.2), (6.3, 1.15),
                                                           (6.3, .4),
            (.6, -.1), (2.1, -.1), (3.6, -.1), (5.1, -.1)]

    # Create a flter that inserts the tabs
    tabsFilter = TabsFilter(writer, [Tab(p) for p in tabs])

    # A filter that creates a border around the entire panel
    borderPoints = [(-.1,-.1), (6, -.1), (6, .5), (6.9, .5), (6.9, 1.2), (7.9, 1.2), (7.9, 6.4), (-.1, 6.4)]
    borderFilter = BorderFilter(tabsFilter, borderPoints)

    # Read from the source gerber file.
    reader = Reader(borderFilter, "tmp/boardoutline.ger")
    reader.read()
