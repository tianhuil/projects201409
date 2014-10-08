import requests
import StringIO
import pandas as pd
import numpy as np
import os
import csv
import urllib2
import matplotlib.pylab as plt

class GetCrimeData(object):
    def __init__(self):
        self.temp = 0
    
    def downloadData(self):
        if 'Crimes_-_2001_to_present.csv' not in os.listdir('../data'):
            msg = 'Download crime data now? This may take an hour...:'
            shall = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
            if shall:
            
                CrimeURL = 'https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv?accessType=DOWNLOAD'
                response = urllib2.urlopen(CrimeURL)
                csvR = csv.reader(response)
            
                writer = csv.writer(open("Crimes_-_2001_to_present.csv", 'w'))
                count = 0
                csvRL = 'many'
                for row in csvR:
                    if count % 100000==0:
                        print str(count) + ' of ' + csvRL
                    writer.writerow(row)
                    count += 1
                return True
            else:
                return False
        else:
            print 'Crime Data in Data Folder... all set'
            return True
        
 get = GetCrimeData()
 get.downloadData()