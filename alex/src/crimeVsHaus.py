## Housing data from zillow

from pandas import *
import os
import matplotlib as plt
import csv

# Reads Zillow Data
def readHausData(city):

    # Reading all city data (to get Chicago Median Price)
    cty1BmedSale = read_csv('City_Zhvi_1bedroom.csv')
    cty1BmedSale = cty1BmedSale[cty1BmedSale.RegionName == city]
    
    # Create Series of prices
    s1Bcity = cty1BmedSale.ix[:,'1996-04':'2014-07'].T
    s1Bcity.columns = ['salePrice']
    
    # Reading all neighbourhood data analogous to above
    neib1BmedSale = read_csv('Neighborhood_Zhvi_1bedroom.csv')
    neib1BmedSale = neib1BmedSale[neib1BmedSale.City == city]
    neib1BmedSale = neib1BmedSale.set_index('RegionName')
    neib1BmedSale = neib1BmedSale.drop(['Metro','City','State','CountyName'],axis=1)
    neib1BmedSale = neib1BmedSale.T
    neib1BmedSale['CityMed'] = s1Bcity.salePrice
    
    neibPriceIdx = neib1BmedSale.div(neib1BmedSale.CityMed, axis='index')
    
    # The next few lines of code index the neibPriceIdx in terms of a fractional year
    neibPriceIdx['Year'] = [int(neibPriceIdx.index[k].split('-')[0]) for k in range(len(neibPriceIdx))]
    neibPriceIdx['Month'] = [int(neibPriceIdx.index[k].split('-')[1]) for k in range(len(neibPriceIdx))]
    neibPriceIdx['YearDec'] = neibPriceIdx['Year']  + neibPriceIdx['Month']/12
    neibPriceIdx = neibPriceIdx.set_index('YearDec')
    return neib1BmedSale, neibPriceIdx

# Reads crime data (reads subset because all crime data is huge)
def readCrimeData():
    dataR = read_csv('Crimes_-_2001_to_present.csv', iterator=True, chunksize=1000, nrows=10000000, usecols = [2,3]+range(5,15)+[17,19,20])
    return dataR
    
def longLat2dec(longLat):
    lng = longLat[0] + longLat[1]/60 + longLat[2]/60**2
    lat = longLat[3] + longLat[4]/60 + longLat[5]/60**2
    return lng, lat



CHIneib, CHImedPriceIdx = readHausData(city = 'Chicago')
CHImedPriceIdx.to_csv('CHImedPriceIdxByNeib.csv')

def yrCrimeCount(group):
    return len(group)

d1 = dataR[dataR['Community Area']==1].groupby('Year').apply(yrCrimeCount)
print d1


    