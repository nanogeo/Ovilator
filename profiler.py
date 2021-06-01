# -*- coding: utf-8 -*-
"""
Created on Mon May 31 12:16:07 2021

@author: hocke
"""

import os

# pip install snakeviz
# run game and create a profile
os.system("py -3.9 -m cProfile -o profile.prof ZergBot.py")
# watch it in snakeviz
os.system("snakeviz profile.prof")