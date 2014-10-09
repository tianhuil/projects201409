# taxi_website.py

# Flask application for displaying taxi project data on a website.

# Outside imports

from flask import Flask, render_template, request, redirect, json, g, send_file  
import urllib
import sqlite3 as sql
import numpy as np
import matplotlib
matplotlib.use("Agg")           # prevents python rocketship
import matplotlib.pyplot as plt
import StringIO

# import local modules

import google_api as api
import taxi_database as dbase
import figures

# Databases

trip_times_database = 'trip_times_data.db'
trip_speeds_database = 'trip_speeds_data.db'
trip_fares_database = 'trip_fares_data.db'

# path = '/Users/jcb/Documents/Data Incubator/taxi-project/src/website/'
# trip_times_database = path + 'trip_times_data.db'
# trip_speeds_database = path + 'databases/trip_speeds_data.db'
# trip_fares_database = path + 'databases/trip_fares_data.db'

databases = {'times': trip_times_database, 'speeds': trip_speeds_database,
                'fares': trip_fares_database}
tol = .01 # Rounding tolerance that generated these databases

# Beginning of app

app = Flask(__name__)

default_start = 'New York Penn Station'
default_dest = 'Metropolitan Museum of Art'
hour_sel = ['' for i in range(12)]
hour_sel[10] = 'selected'
day_sel = ['' for i in range(7)]
day_sel[1] = 'selected'
checked = ['checked','']

@app.route('/')
def test_site():
    return render_template('test_site-bootstrap.html', default_start=default_start,
                            default_dest=default_dest, day_sel=day_sel, hour_sel=hour_sel,
                            checked=checked)
    
@app.route('/output', methods = ['POST'])
def record_data():
    start_point = request.form.get('start_point')
    default_start = start_point
    end_point = request.form.get('end_point')
    default_dest = end_point
    day = int(request.form.get('day'))
    day_sel = ['' for i in range(7)]
    day_sel[day] = 'selected'
    hour = int(request.form.get('hour'))
    hour_sel = ['' for i in range(12)]
    hour_sel[hour] = 'selected'
    ampm = request.form.get('ampm')
    checked = ['checked','']
    if ampm == 'pm':
        checked = ['','checked']
        hour += 12
    days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday',
                5: 'Saturday', 6: 'Sunday'}
    day_name = days_of_week[day]


    
    bounds="40.5,-74.2|40.9,-73.7"   
    try:    
        start_coords = api.get_lat_lon_coords(start_point,bounds=bounds)
        end_coords = api.get_lat_lon_coords(end_point,bounds=bounds)
    except api.NoPlaceError:
        return render_template('error.html',default_start=default_start,
                            default_dest=default_dest, day_sel=day_sel, hour_sel=hour_sel,
                            checked=checked)
    distance = api.get_trip_distance(','.join(str(i) for i in start_coords),
                                     ','.join(str(j) for j in end_coords))
                                     
    def roundCoord(coordinates, tol=tol):
        return str((np.rint(coordinates/tol)*tol))
    
    output = {}
    for time_diff in range(-6,7):
        new_hour = hour+time_diff
        output[time_diff] = \
                dbase.query_database_row(trip_speeds_database,
                                             start_lat_rnd=roundCoord(start_coords[0]),
                                             start_lon_rnd=roundCoord(start_coords[1]),
                                             end_lat_rnd=roundCoord(end_coords[0]),
                                             end_lon_rnd=roundCoord(end_coords[1]),
                                             day=(new_hour/24)%7, hour=new_hour%24)        

        
#    samples = int(output[0][6])
    quantiles = {}
    labels = {}
    for key in output:
        if output[key] is not None:
            quantiles[key] = sorted([distance/spd for spd in output[key][7:12]])
        else:
            quantiles[key] = [0,0,0,0,0]
            
        labels[key] = str((hour+key)%24)+':00'
    
    print 'Quantiles:',quantiles
    quantiles_to_url = \
        'z'.join(str(num) for key in sorted(quantiles) for num in quantiles[key])
    
    labels_to_url = \
        ','.join(labels[key].replace(' ','+') for key in sorted(labels))
    
    heatmap = 'static/hex-'+str(day)+'-'+str(hour)+'-large.png'   
    map_url = api.make_static_map_url(start_point,end_point,size='500x400',
                        maptype='terrain', markers=start_point+'|'+end_point)
    
    days = range(168)
    return render_template('output.html', map_url=map_url, quantiles=quantiles_to_url,
                                labels = labels_to_url, start_address=start_point,
                                text_time=str(hour)+':00', hour=hour, day=day,
                                day_name=days_of_week[day], end_address=end_point,
                                days=days, days_of_week=days_of_week,
                                start_lat=start_coords[0], start_lon=start_coords[1],
                                default_start=default_start, default_dest=default_dest,
                                hour_sel=hour_sel, day_sel=day_sel, checked=checked)
                                
@app.route('/description')
def description():
    return render_template('description.html')
    
@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/fig/<quantiles>/<labels>/<start>/<end>/<day>')
def make_figure(quantiles,labels,start,end,day):

    split_data = np.array([float(num) for num in quantiles.split('z')])

    quantiles_list = [split_data[i:i+5] for i in range(0,len(split_data),5)]
    
    quantile_labels = [label.replace('+',' ') for label in labels.split(',')]
    
    fig = figures.multi_boxplot(quantiles_list,quantile_labels,start,end,day)
    
    img = StringIO.StringIO()
    fig.savefig(img)            #  bbox_inches='tight'
    img.seek(0)
    return send_file(img, mimetype='image/png')
    
    

if __name__ == '__main__':
    app.run(debug=True)