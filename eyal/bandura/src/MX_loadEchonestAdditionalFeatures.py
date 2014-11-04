# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 12:39:56 2014

@author: eyalshiv



    Load acoustic features from EchoNest for the MSD:
    Speechiness, danceability etc.
    



"""

import os
import sys
#import glob
#import string
import time
import datetime
import numpy as np

import psycopg2 as psy
import pandas as pd
import csv
import sqlite3




import MX_common

sys.path.append(MX_common.g_base_dir + '/src')
sys.path.append(MX_common.g_base_dir + '/src/EchoNest')
sys.path.append(MX_common.g_base_dir + '/src/EchoNest/beets')
sys.path.append(MX_common.g_base_dir + '/src/EchoNest/pyechonest')

#import hdf5_getters as GETTERS




import pyechonest











