import requests
import StringIO
import pandas as pd
import numpy as np
import os
import csv
import urllib2
import matplotlib.pylab as plt

class dwellingInCrime(object):
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
        
    def readCrimeData(self):
        self.downloadData()
        df_crimeDataR = pd.read_csv('../data/Crimes_-_2001_to_present.csv', 
                        iterator=True, chunksize=1000, nrows=10000000, usecols = [2,3]+range(5,15)+[17,19,20])
        df_crimeDataR.rename(columns = {'Community Area':'comNum', 'Latitude':'lat', 'Longitude':'lng'}, inplace=True)
    
        # The following converts all the comNums into the same format:
        def convert_to_float(x):
            if type(x)==type('hello'): # type string
                if x.isdigit()==True:
                    return float(x)
                else:
                    return 0.
            elif type(x)==type(1): # type integer
                return float(x)
            elif type(x)==type(1.): # type float
                if np.isnan(x):
                    return 0.
                else:
                    return x
            else:
                return 0.
    
        df_crimeDataR.comNum = df_crimeDataR.comNum.apply(convert_to_float) # converts comNums to floats
        df_crimeDataR['Month'] = df_crimeDataR.Date.apply(lambda x: float(x.split('/')[0])) # gets month
        #df_crimeDataR['Date'] = pd.to_datetime(df_crimeDataR.Date) # This code is currently killing my Kernel
        df_crimeDataR['DateYr'] = df_crimeDataR.Year + (df_crimeDataR.Month-1)/12 # data in fraction of the year (by month)
        return df_crimeDataR
            
                
class DataGrids(object):
    # Constructor
    def __init__(self, data, tarCol, gData):
        # Input a pandas DataFrame called data with a lat and lng column,
        # a target column to aggregate (tarCol), and grid data (gData)
        self.data = data
        self.tarCol = tarCol
        self.gData = gData
        
    def AssignGridValues(self):
        
        try:
            self.data.gridNum = 0 # If this doesn't exist, the except initializes it
        except:
            self.data['gridNum'] = 0
            
        # The for loops start at the bottom-left, and col upward to the top before
        # moving one column to the right and repeating
        #
        # This can be done better with a map reduce (see assignGridValues_MR method)
        gCount = 1
        for gXidx in range(self.gData['gNumX']):
            for gYidx in range(self.gData['gNumY']):
                self.data.loc[(self.data.lat >=self.gData['bottom']+self.gData['gSpaceY']*gYidx) & 
                              (self.data.lat < self.gData['bottom']+self.gData['gSpaceY']*(gYidx+1)) &
                              (self.data.lng >=self.gData['left']  +self.gData['gSpaceX']*gXidx) &
                              (self.data.lng < self.gData['left']  +self.gData['gSpaceX']*(gXidx+1)),'gridNum'] = gCount
                gCount += 1
                if gCount % 100 == 0:
                    print gCount
                if gCount==self.gData['gNumX']*self.gData['gNumY']//2:
                    print '50% complete' 
        print '100% complete'
        
        self.gb = self.data.groupby('gridNum')
        return self.data
    
    def AggDataByGrid(self,f):
        try:
            return self.gb.apply(f)
        except:
            print("Call AssignGridValues() before calling AggDataByGrid(f), or make sure f is a defined function to apply to df")
            return None
        
    def get_gLatLngs(self):
        self.gLat = []
        self.gLng = []
        for gXidx in range(self.gData['gNumX']):
            for gYidx in range(self.gData['gNumY']):
                self.gLat.append(self.gData['bottom']+self.gData['gSpaceY']*(gYidx+0.5))
                self.gLng.append(self.gData['left']+self.gData['gSpaceX']*(gXidx+0.5))
    
        return np.array(self.gLat), np.array(self.gLng)
    
    

dwell = dwellingInCrime()
df_crimeDataR = dwell.readCrimeData()     
df_recCr = df_crimeDataR[df_crimeDataR.Year >= 2013]
df_recCr['gridNum'] = 0 #Initializes grid numbers, which will be counted from (bottom-left rightward, and end at the top-right)
df_recCr_HOMI = df_recCr[df_recCr['Primary Type'] == 'HOMICIDE']
df_recCr_BURG = df_recCr[df_recCr['Primary Type'] == 'BURGLARY']
df_recCr_NARC = df_recCr[df_recCr['Primary Type'] == 'NARCOTICS']
print "END LOADING"

gData = {
    'top': 42.03,
    'bottom': 41.64,
    'left': -87.89,
    'right': -87.52,
    'gNumX': 30,
    'gNumY': 40,
    'milesPerLat': 111.2 * 0.621371, # miles/lat (near Chi) - these numbers are km/unit * mi/km
    'milesPerLng': 82.63 * 0.621371 # miles/lng (near Chi)
}
gData['gSpaceX'] = (gData['right'] - gData['left'])/gData['gNumX']
gData['gSpaceY'] = (gData['top'] - gData['bottom'])/gData['gNumY']
gData['gridArea'] = gData['gSpaceX']*gData['milesPerLng'] * gData['gSpaceY']*gData['milesPerLat']

# Aggregate Data into Grids
crDataGrid = DataGrids(df_recCr,1,gData)
df_recCr = crDataGrid.AssignGridValues()
df_recCr_gAllCrime = crDataGrid.AggDataByGrid(lambda x: len(x)) # total number of crimes per grid (gridNum = 0, all crimes outside of grid)
df_recCr_gComNum = np.round(crDataGrid.gb.mean(),0).comNum # Calculates Community Numbers Corresponding to Each Gridcbv
gLat, gLng = crDataGrid.get_gLatLngs()

# Homicides, Burglaries, Narcotics
# Aggregate Data into Grids
def get_grid_data(df,f,gData):
    DataGrid = DataGrids(df,1,gData)
    data = DataGrid.AssignGridValues()
    return DataGrid.AggDataByGrid(f)

df_recCr_gHOMI = get_grid_data(df_recCr_HOMI,(lambda x: len(x)),gData)
df_recCr_gBURG = get_grid_data(df_recCr_BURG,(lambda x: len(x)),gData)
df_recCr_gNARC = get_grid_data(df_recCr_NARC,(lambda x: len(x)),gData)

# Read Scraped Price Data:
df_hPrices = pd.read_csv('../data/priceLatLngAll.csv')

# Function for Aggregating Means (only aggregate means if number of data points greater than minVal):
def meanPrice(gb,minVal):
    if (len(gb) >= minVal):
        return np.round(np.mean(gb.price),0)
    else:
        return 0
    
prDataGrid = DataGrids(df_hPrices,1,gData)
df_recPr = prDataGrid.AssignGridValues()
df_recPr_gMeanPrice = np.round(prDataGrid.gb.apply(meanPrice,1),0)
df_recPr_gNumPrices = prDataGrid.gb.apply(lambda x: len(x))

# Loading and Gridding School Data
df_schools = pd.read_csv('../data/Chicago_Public_Schools_-_Progress_Report_Cards__2011-2012_.csv',
                         usecols = [2]+range(17,34,2)+[72,73,74])

# Switching to Standardized Column Names (for merges)
df_schools.rename(columns = {'Latitude':'lat', 'Longitude':'lng', 'Community Area Number':'comNum'}, inplace=True)
df_schools = df_schools.replace({'NDA':np.nan},regex=True)

# The question is, how to aggregate school performace numbers into grid spaces
#df_schools.iloc[:,:10].apply(lambda x: nan if type(x)==type('hello') else x)

df_schools['avgScore'] = df_schools.iloc[:,1:9].mean(axis =1)
df_schoolsForGriding = df_schools.iloc[:,-5:]
scDataGrid = DataGrids(df_schoolsForGriding,1,gData)
df_recSc = scDataGrid.AssignGridValues()
df_recSc_gSchScore = np.round(scDataGrid.gb.avgScore.mean(),2)
df_recSc_gNumSch = scDataGrid.gb.apply(lambda x: len(x))

# Community Area Populations over time
# By the end of this cell, mergedComData contains the 2014 estimated pop
# by community number, and population density
comPops = pd.read_csv('../data/comPops.csv')
colsToKeep = [col for col in comPops.columns if (col.find('Total')==0 | col.find('Comm'))==0]
comPops = comPops[colsToKeep]
comPops.rename(columns = {colsToKeep[0]:"comNum"}, inplace=True)
comPops['pop2010'] = pd.read_csv('../data/mergedData.csv', usecols=[2])

# get linear model coeficents to extrapolate poputaltion over time:
popChgPerYear = np.zeros(77)
popAt0 = popChgPerYear.copy()
for k in range(len(popChgPerYear)):
    popChgPerYear[k], popAt0[k] = np.polyfit([2000,2009,2010],comPops.ix[k,-3:],1)
pop2014linEst = popChgPerYear*2014 + popAt0
mergedComData = pd.read_csv('../data/mergedData.csv')
pop2014wsEst = np.array(mergedComData.comPop)

# Not all the walk score (ws) estimated populations are correct because of data set incompleteness
# If the pop2014wsEst is too far off from the linEst, take the linEst
if len(pop2014linEst) == len(pop2014wsEst):
    popEst2014 = pop2014linEst
    for idx in range(len(popEst2014)):
        if abs(pop2014wsEst[idx] - pop2014linEst[idx]) < 1000:
            popEst2014[idx] = pop2014wsEst[idx]
mergedComData['comPop2014est'] = floor(popEst2014)
mergedComData['popDen2014est'] = mergedComData.comPop2014est / mergedComData.area * (5280**2) # Note the units, ppl/sqMile

# Here we group by grid numbers and calculate
# the amount of crime in each grid, as well as the population
# and the associated comNum

gCrime_all = np.zeros(crDataGrid.gData['gNumX']*crDataGrid.gData['gNumY']+1)
gCrime_HOMI = gCrime_all.copy()
gCrime_BURG = gCrime_all.copy()
gCrime_NARC = gCrime_all.copy()
gComNum = gCrime_all.copy()
gPrice = gCrime_all.copy()
gPriceNum = gCrime_all.copy()
gSchScr = gCrime_all.copy()
gSchNum = gCrime_all.copy()
for idx in df_recCr_gAllCrime.index:
    gCrime_all[idx] = df_recCr_gAllCrime[idx]
    gComNum[idx] = df_recCr_gComNum[idx]
for idx in df_recCr_gHOMI.index:
    gCrime_HOMI[idx] = df_recCr_gHOMI[idx]
for idx in df_recCr_gBURG.index:
    gCrime_BURG[idx] = df_recCr_gBURG[idx]
for idx in df_recCr_gNARC.index:
    gCrime_NARC[idx] = df_recCr_gNARC[idx]
for idx in df_recPr_gMeanPrice.index:
    gPrice[idx] = df_recPr_gMeanPrice[idx]
    gPriceNum[idx] = df_recPr_gNumPrices[idx]
for idx in df_recSc_gNumSch.index:
    gSchScr[idx] = df_recSc_gSchScore[idx] if np.isnan(df_recSc_gSchScore[idx]) == 0 else 0
    gSchNum[idx] = df_recSc_gNumSch[idx]
# The reason for this for loop is that not all grid number occur in the "df_recCr_gAllCrime" DataFrame

gCrime_all = gCrime_all[1:]
gCrime_HOMI = gCrime_HOMI[1:]
gCrime_BURG = gCrime_BURG[1:]
gCrime_NARC = gCrime_NARC[1:]
gComNum = gComNum[1:]
gPrice = gPrice[1:]
gPriceNum = gPriceNum[1:]
gSchScr = gSchScr[1:]
gSchNum = gSchNum[1:]


# note above that grid square 1 corresponds to index 0 
# grid# n corresponds to index n-1

gPop = []
for idx in range(len(gComNum)):
    try:
        gPop.append(float(mergedComData.popDen2014est[mergedComData.comNum==gComNum[idx]])*crDataGrid.gData['gridArea'])
    except: # when comNum = 0 because grid is outside a community or no crime occured there
        gPop.append(0)
    
def normalizeCrime(crime,gPop):
    data = floor(crime/gPop*100000)
    data[np.isnan(data)] = 0
    return data
    
    
gCrime_allPer100000 = normalizeCrime(gCrime_all,gPop)
gCrime_HOMIper100000 = normalizeCrime(gCrime_HOMI,gPop)
gCrime_BURGper100000 = normalizeCrime(gCrime_BURG,gPop)
gCrime_NARCper100000 = normalizeCrime(gCrime_NARC,gPop)
# At this point, we have the normalized crime arrays for each grid point
