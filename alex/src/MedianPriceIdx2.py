from pandas import *
import matplotlib as plt

# Managing Zillow Housing Value Index (ZHVI) csv data
city = 'Chicago'

# Collecting city-wide 2bdrm ZHVI
cty2BmedSale = read_csv('../data/City_Zhvi_2bedroom.csv')
cty2BmedSale = cty2BmedSale[cty2BmedSale.RegionName == city]
# convert DataFrame (df) to Series (s)
s2Bcity = cty2BmedSale.ix[:,'1996-04':'2014-07'].T
s2Bcity.columns = ['salePrice']

# Collecting city-wide neighbourhood specific 2bdrm ZHVI
neib2BmedSale = read_csv('../data/Neighborhood_Zhvi_2bedroom.csv')
neib2BmedSale = neib2BmedSale[neib2BmedSale.City == city]
neib2BmedSale = neib2BmedSale.set_index('RegionName')
neib2BmedSale = neib2BmedSale.drop(['Metro','City','State','CountyName'],axis=1)
neib2BmedSale = neib2BmedSale.T
neib2BmedSale['CityMed'] = s2Bcity.salePrice
# Normalizing all ZHVI to citywide ZHVI
neib2BpriceIdx = neib2BmedSale.div(neib2BmedSale.CityMed, axis='index')
neib2BpriceIdx['Year'] = [int(neib2BpriceIdx.index[k].split('-')[0]) for k in range(len(neib2BpriceIdx))]
neib2BpriceIdx['Month'] = [int(neib2BpriceIdx.index[k].split('-')[1]) for k in range(len(neib2BpriceIdx))]
neib2BpriceIdx['YearDec'] = neib2BpriceIdx['Year']  + neib2BpriceIdx['Month']/12
neib2BpriceIdx = neib2BpriceIdx.set_index('YearDec')


# Plots and Figures
neib2BpriceIdx['Rogers Park'].plot(legend = False, ylim = [0.4,0.85])
"""



# Attempting to import gigantic Crime File

# In[85]:

dataR = read_csv('Crimes_-_2001_to_present.csv', iterator=True, chunksize=1000, nrows=10000000, usecols = [2,3]+range(5,15)+[17,19,20])


# In[63]:

# df= read_csv('CHIcommAreaNums.csv')


# In[162]:

def yrCrimeCount(group):
    return len(group)

d1 = dataR[dataR['Community Area']==1].groupby('Year').apply(yrCrimeCount)


# In[163]:

d1[1:-2].plot(xlim=[1995,2015], ylim=[0,6200])


# In[ ]:


"""
