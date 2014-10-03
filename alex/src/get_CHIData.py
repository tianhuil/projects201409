# fetch data for CHI house-crime project

import requests
import zipfile
import StringIO
import pandas as pd
import numpy as np
import os

result = requests.get("https://data.cityofchicago.org/api/views/xzkq-xp2w/rows.csv?accessType=DOWNLOAD")

