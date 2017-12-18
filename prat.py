# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib.pyplot as plt
import cmath

def GetPosition(sentence):
    fields = sentence.split(',')
    if (fields[0] == '$IIGLL'):
        lat = float(fields[1][0:2]) + (float(fields[1][2:]) / 60)
        if (fields[2] == 'S'):
            lat = -1 * lat
        lon = float(fields[3][0:3]) + (float(fields[3][3:]) / 60)
        if (fields[4] == 'W'):
            lon = -1 * lon
        return (complex(lat, lon))

def GetTime(sentence):
    fields = sentence.split(',')
    if (fields[0] == '$IIGLL'):
        time = float(fields[5][0:2]) * 3600 + (float(fields[5][2:4]) * 60
                     + (float(fields[5][4:6])))
        return (time)

def GetGroundVelocity(sentence):
    fields = sentence.split(',')
    if (fields[0] == '$IIVTG'):
        sog = float(fields[5])
        cog = float(fields[1])
        cog = np.radians(cog)
        return(cmath.rect(sog, cog))

def GetWaterVelocity(sentence):
    fields = sentence.split(',')
    if (fields[0] == '$IIVHW'):
        sog = float(fields[5])
        cog = float(fields[3])
        cog = np.radians(cog)
        return(cmath.rect(sog, cog))

def GetApparentWind(sentence):
    fields = sentence.split(',')
    if (fields[0] == '$IIVWR'):
        speed = float(fields[3])
        angle = float(fields[1])
        if (fields[2] == 'L'):
            angle = angle * -1
        angle = np.radians(angle)
        return(cmath.rect(speed, angle))
        
def PlotHist(title, vector):
    plt.figure(title)
    plt.clf()
    plt.subplot(211)
    plt.hist(np.angle(vector, deg = True), 360)
    plt.subplot(212)
    plt.hist(np.absolute(vector), 100)

def PlotPlot(title, vector):
    plt.figure(title)
    plt.clf()
    plt.subplot(211)
    plt.plot(time, np.angle(vector, deg = True))
    plt.subplot(212)
    plt.plot(time, np.absolute(vector))



position = []
time = []
ground = []
apparentWind = []
water = []

log = open(r'D:\sailing\2017\logs\1_5_2017_2.log', 'r')
for line in log:
    currentPosition = GetPosition(line)
    if currentPosition:
        position.append(currentPosition)
    currentTime = GetTime(line)
    if currentTime:
        time.append(currentTime)
    currentGround = GetGroundVelocity(line)
    if currentGround:
        ground.append(currentGround)
    currentWater = GetWaterVelocity(line)
    if currentWater:
        water.append(currentWater)
    currentApparentWind = GetApparentWind(line)
    if currentApparentWind:
        apparentWind.append(currentApparentWind)
log.close()

position = np.array(position)
time = np.array(time)
ground = np.array(ground)
water = np.array(water)
apparentWind = np.array(apparentWind)

time = time[0:min(time.size, ground.size, apparentWind.size, water.size)]
ground = ground[0:min(time.size, ground.size, apparentWind.size, water.size)]
apparentWind = apparentWind[0:min(time.size, ground.size, apparentWind.size, water.size)]

apparentWind = apparentWind * 1.2

trueWind = apparentWind - (np.absolute(water) + 0j)
geographicWind = abs(trueWind) + np.exp(1j * (np.angle(water) + np.angle(trueWind)))

tide = ground - water

#PlotHist("Ground Velocity Histogram", ground)
#PlotHist("Apparent Wind Histogram", apparentWind)
PlotHist("Geographic Wind Histogram", geographicWind)
PlotHist("Tide Histogram", tide)

PlotPlot("Water Velocity", water)
PlotPlot("tide Velocity", tide)
PlotPlot("Apparent Wind", apparentWind)
PlotPlot("True Wind", trueWind)
PlotPlot("Geographic Wind", geographicWind)

plt.show()

