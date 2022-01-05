#!/bin/python

import math
import glob
import numpy as np
from scipy import *
from scipy.io import wavfile
from pylab import *

# mowa ludzka 80-300 hz (?)
# https://www.axiomaudio.com/blog/audio-oddities-frequency-ranges-of-male-female-and-childrens-voices/
male_freq   = [85, 155]
female_freq = [155,255]

# maksymalne downsamplowanie
DOWN_SAMPLE = 6

# macierz pomylek
err_mat = [[0, 0],
           [0, 0]]

# wczyt plikow glob
files = glob.glob("audio/*.wav")

def HPS(orig_data, rate):
    # podzial danych na 1 sekundowe okna
    windows = int(len(orig_data) / rate)
    partData = [orig_data[i * rate: (i + 1) * rate] for i in range(windows)]

    max_size = 0
    calculated = [] 

    for data in partData:
        fourier     = abs(fft(data)) / rate
        fft_down    = copy(fourier)

        for i in range(2, DOWN_SAMPLE):
            downSampled = copy(fourier[::i])
            fft_down    = fft_down[:len(downSampled)]
            fft_down    *= downSampled 

        calculated.append(fft_down)
        if (len(fft_down) > max_size):
            max_size = len(fft_down)
    
    result = [1] * max_size
    for window in calculated:
        result += window

    return result

def calcErrorMatrix(real, presumed):
    if (real == 'K' and presumed == 'K'):
        err_mat[0][0] += 1
    elif (real == 'K' and presumed == 'M'):
        err_mat[1][0] += 1
    elif (real == 'M' and presumed == 'M'):
        err_mat[1][1] += 1
    else:
        err_mat[0][1] += 1

for file in files:
    # specyficzny format nazwy jest tutaj wymagany
    #print(file)
    real_gender = file.split('_')[1][0]
    rate, signal = wavfile.read(file)
    # zapis do jednego kanalu
    if (len(signal.shape) == 2):
        signal = [s[0] for s in signal]

    result = HPS(signal, rate)

    val_male    = sum(result[male_freq[0]:male_freq[1]])
    val_female  = sum(result[female_freq[0]:female_freq[1]])

    hps_gender = ''

    # wykrycie meskiego glosu z pasma czestotliwosci
    if (val_male > val_female):
        hps_gender = 'M'
    else:
        hps_gender = 'K'

    if (real_gender != hps_gender):
        print(real_gender, hps_gender)
    calcErrorMatrix(real_gender, hps_gender)
print (err_mat)
