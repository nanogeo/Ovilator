# -*- coding: utf-8 -*-
"""
Created on Mon May 31 12:16:07 2021

@author: hocke
"""

import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt




my_data = genfromtxt('timings.txt', delimiter=',')

my_data = my_data * 1000
my_data = my_data[:,:11]

each_max = np.amax(my_data,axis=0)
each_avg = np.average(my_data, axis=0)
totals = my_data.sum(axis = 1)

plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,0:1], color = 'red', label = "update unit tags")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,1:2], color = 'black', label = "display debug")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,2:3], color = 'blue', label = "distribute workers")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,3:4], color = 'green', label = "execute build, get upgrades, inject larva")
#plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,4:5], color = 'r', label = "update creep")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,5:6], color = 'purple', label = "spread creep")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,6:7], color = 'orange', label = "position overlords, scouting")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,7:8], color = 'yellow', label = "update enemy units")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,8:9], color = 'gray', label = "track enemy army position")
plt.plot(np.array(range(0, len(my_data[:,0:1]))) / 12, my_data[:,9:10], color = 'pink', label = "execute plan")
plt.plot(np.array(range(0, len(totals))) / 12, totals, color = 'red', label = "total")
plt.show()