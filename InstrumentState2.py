# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 17:08:18 2020

@author: Guy McBride
"""

import numpy as np
from datetime import datetime
import logging
import pynmea2 as nmea


__log = logging.getLogger(__name__)


class Instruments:
    def __init__(self):
        self.__log = logging.getLogger(__name__)

        self.ground_velocity = []
        self.water_velocity = []
        self.position = []
        self.wind_apparent = []
        self.depth = []
        self.water_temperature = []
        self.datetime = []
        self.__clear_filters()

    @property
    def wind_true(self):
        return self.wind_apparent - np.absolute(self.water_velocity)

    @property
    def wind_direction(self):
        angles = np.angle(self.wind_true)
        speeds = abs(self.wind_true)
        headings = np.angle(self.water_velocity)
        geo_wind = speeds * np.exp(1j * (angles + headings))
        return geo_wind

    def __getcomplex(self, speed, bearing):
        speed = np.mean(speed)
        if speed <= 0:
            speed = 0.001
        velocity = speed * np.mean(bearing)
        return velocity

    def __clear_filters(self):
        self._ground_velocity = []
        self._water_speed = []
        self._water_heading = []
        self._ground_speed = []
        self._ground_heading = []
        self._water_temperature = []
        self._position = []
        self._wind_apparent = []
        self._depth = []

    def __append_latest(self, datetime):
        self.datetime.append(datetime)
        self.depth.append(np.mean(self._depth))
        self.position.append(np.mean(self._position))
        self.water_temperature.append(np.mean(self._water_temperature))
        self.wind_apparent.append(np.mean(self._wind_apparent))
        self.water_velocity.append(
            self.__getcomplex(self._water_speed, self._water_heading)
        )
        self.ground_velocity.append(
            self.__getcomplex(self._ground_speed, self._ground_heading)
        )

    def process_sentence(self, sentence: str):
        try:
            self.__log.debug("Processing {}".format(sentence))
            sentence = nmea.parse(sentence)
            test = sentence.sentence_type
        except nmea.ParseError:
            if sentence[0:5] != "!AIVD":
                self.__log.debug("Couldn't parse: {}".format(sentence))
            return
        except AttributeError:
            self.__log.debug(f"Didn't decode: {sentence}")
            return
        self.__process_position(sentence)
        self.__process_depth(sentence)
        self.__process_water_temperature(sentence)
        self.__process_water_velocity(sentence)
        self.__process_ground_velocity(sentence)
        self.__process_wind_apparent(sentence)
        self.__process_time(sentence)
        return

    def __process_position(self, sentence):
        try:
            if sentence.sentence_type == "RMC":
                if sentence.status == "A":
                    self.__log.debug("Processing RMC in position")
                    self._position.append(
                        np.complex(sentence.latitude, sentence.longitude)
                    )
        except AttributeError:
            self.__log.error(f"Processing {sentence}")

    def __process_depth(self, sentence):
        if sentence.sentence_type == "DPT":
            self.__log.debug("Processing DPT")
            depth = float(sentence.depth + sentence.offset)
            if depth < 1.6:
                self.__log.info("Aground: {} - {}".format(depth, sentence))
            self._depth.append(depth)
        pass

    def __process_water_temperature(self, sentence):
        if sentence.sentence_type == "MTW":
            self.__log.debug("Processing MTW")
            self._water_temperature.append(sentence.temperature)
        pass

    def __process_water_velocity(self, sentence):
        if sentence.sentence_type == "VHW":
            self.__log.debug("Processing VHW")
            if sentence.heading_true is not None:
                self._water_heading.append(
                    np.exp(1j * np.deg2rad(float(sentence.heading_true)))
                )
            self._water_speed.append(float(sentence.water_speed_knots))
        #            self._water_velocity.append(speed * np.exp(1j * np.deg2rad(heading)))
        elif sentence.sentence_type == "HDT":
            if sentence.heading == None:
                self.__log.info("Received bad HDT - {}".format(sentence))
            else:
                self._water_heading.append(
                    np.exp(1j * np.deg2rad(float(sentence.heading)))
                )
        return

    def __process_ground_velocity(self, sentence):
        if sentence.sentence_type == "RMC":
            if sentence.status == "A":
                self.__log.debug("Processing RMC for Velocity")
                if sentence.true_course is not None:
                    self._ground_heading.append(
                        np.exp(1j * np.deg2rad(float(sentence.true_course)))
                    )
                self._ground_speed.append(float(sentence.spd_over_grnd))
        return

    def __process_wind_apparent(self, sentence):
        if sentence.sentence_type == "VWR":
            self.__log.debug("Processing VWR")
            wind_angle = float(sentence.deg_r)
            if sentence.l_r == "L":
                wind_angle *= -1
            wind_speed = float(sentence.wind_speed_kn)
            self._wind_apparent.append(wind_speed * np.exp(1j * np.deg2rad(wind_angle)))
        return

    def __process_time(self, sentence):
        if sentence.sentence_type == "RMC":
            if sentence.status == "A":
                self.__log.debug("Processing RMC in time")
                self.__append_latest(
                    datetime.combine(sentence.datestamp, sentence.timestamp)
                )
                self.__clear_filters()


#%%
def count_sentences(filename):
    __log.info("Counting Sentences...")
    sentences = {}
    with open(filename, "r") as f:
        for line in f:
            if line[0:5] != "!AIVD":
                try:
                    sentence = nmea.parse(line)
                    if sentence.sentence_type in sentences:
                        sentences[sentence.sentence_type] = (
                            sentences[sentence.sentence_type] + 1
                        )
                    else:
                        sentences.update({sentence.sentence_type: 0})
                except nmea.ParseError:
                    __log.debug("Parse Error - {}".format(line))
    __log.info("...{} 'RMC' sentences found".format(sentences["RMC"]))
    return sentences


#%%
def PlotPlot(title, time, vector, bearing=False):
    plt.figure(title)  # makes this figure 'active'
    plt.clf()
    fig, axes_set = plt.subplots(2, sharex=True, num=title)
    for axis_set in axes_set:
        axis_set.tick_params(labelbottom=True, labelright=True)
        axis_set.grid(True)
        axis_set.yaxis.set_minor_locator(MultipleLocator(5))
    fig.suptitle(title)
    x = np.arange(0, len(time))

    angle = np.angle(vector)
    if bearing:
        angle[angle < 0] += 2 * np.pi
        axes_set[0].set_yticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    else:
        axes_set[0].set_yticks([-180, -135, -90, -45, 0, 45, 90, 135, 180])
    angle = np.rad2deg(angle)
    np.round(angle)
    axes_set[0].plot(time, angle, linestyle="None", marker=".", markersize=2.0)
    #        yTicks = axes_set[0].get_yticks()
    #        yTicks %= 360
    #        ax[0].set_yticklabels(list(map(str,yTicks)))
    # Plot the 'speed'
    axes_set[1].plot(time, np.round(np.absolute(vector), 2))


#%%
######################################################
# MAIN!!!!!
################  ####################################

if __name__ == "__main__":

    filename = r"C:\Users\guymc\OneDrive\Sailing\2020\11_7_2020.log"

    import scipy.signal as signal
    import matplotlib.pyplot as plt

    # from matplotlib.collections import LineCollection
    # from matplotlib.colors import ListedColormap, BoundaryNorm
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator

    __log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    if __log.hasHandlers():
        __log.handlers.clear()
    __log.addHandler(ch)

    instrument_data = Instruments()
    __log.info("Opening file: {}...".format(filename))
    with open(filename, "r") as log:
        for line in log:
            instrument_data.process_sentence(line)

    index = np.where(instrument_data.depth == np.nanmin(instrument_data.depth))[0]
    if len(index) > 0:
        __log.info("depth Readings: {}".format(len(instrument_data.depth)))
        __log.info("depth average: {}".format(np.nanmean(instrument_data.depth)))
        time_min_depth = instrument_data.datetime[index[0]]
        __log.info(
            "depth minimum: {} at {}".format(
                np.nanmin(instrument_data.depth), time_min_depth
            )
        )
        plt.figure()
        plt.subplot(211)
        plt.plot(instrument_data.datetime, instrument_data.depth)
        plt.subplot(212)
        plt.plot(instrument_data.datetime, instrument_data.water_temperature)

    plt.figure()
    plt.plot(
        np.array(instrument_data.position).imag, np.array(instrument_data.position).real
    )

    #%%
    PlotPlot("Water", instrument_data.datetime, instrument_data.water_velocity, True)
    filteredVector = np.convolve(
        instrument_data.water_velocity, np.ones(10) / 10, mode="same"
    )
    PlotPlot("FilteredWater", instrument_data.datetime, filteredVector, True)
    PlotPlot(
        "Apparent Wind", instrument_data.datetime, instrument_data.wind_apparent, False
    )
    filteredVector = np.convolve(
        instrument_data.wind_apparent, np.ones(100) / 100, mode="same"
    )
    PlotPlot("Filtered Apparent Wind", instrument_data.datetime, filteredVector, False)
    PlotPlot("True Wind", instrument_data.datetime, instrument_data.wind_true, False)
    PlotPlot(
        "Wind Direction", instrument_data.datetime, instrument_data.wind_direction, True
    )
    plt.show()
