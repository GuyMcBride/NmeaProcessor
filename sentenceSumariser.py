# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 09:00:42 2020

@author: guymc
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 17:08:18 2020

@author: Guy McBride
"""

import numpy as np
from datetime import datetime
import logging
import pynmea2 as nmea
import matplotlib.pyplot as plt

__log = logging.getLogger(__name__)

######################################################
# MAIN!!!!!
################  ####################################
    
if (__name__ == '__main__'):
    
    filename = r'C:\Users\guymc\OneDrive\Sailing\2020\5_7_2020.log'
    
    import scipy.signal as signal
    __log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    if __log.hasHandlers():
        __log.handlers.clear()
    __log.addHandler(ch)

    sentences = {}

    __log.info("Opening file: {}...".format(filename))
    with open(filename, 'r') as log:
        for line in log:
            if line[0:5] != '!AIVD':
                try:
                    sentence = nmea.parse(line)
                    if (sentence.sentence_type in sentences):
                        sentences[sentence.sentence_type] = sentences[sentence.sentence_type] + 1
                    else:
                        sentences.update({sentence.sentence_type: 0})
                except nmea.ParseError:
                    __log.info("Parse Error - {}".format(line))
