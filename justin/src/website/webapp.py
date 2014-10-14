# webapp.py

# Application for displaying taxi project data on a website.

from flask import Flask, render_template, request, redirect, json, g, send_file  
import urllib
import sqlite3 as sql
import numpy as np
import matplotlib
matplotlib.use("Agg")           # prevents python rocketship
import matplotlib.pyplot as plt
import StringIO

# Tolerance and rounding function to translate raw lat/lon data into our grids

ROUNDING_TOL = .01  # Fixed by prior computation
DATABASES = ['taxi_trip_data.db','taxi_speed_data.db','taxi_price_data.db']
days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'
                5: 'Saturday', 6: 'Sunday'}

def roundCoord(coordinates, tol):
     return str((np.rint(coordinates/tol)*tol))
     
def open_database(database):
    conn = sql.connect(database)
    return conn.cursor()
    
def make_boxplot(percentile_data, axes_object, label):
    # Make the boxplot and get rid of borders I don't want.
    
    axes_object.boxplot(num_data,vert=False,widths=0.6)
    axes_object.spines['top'].set_visible(False)
    axes_object.spines['right'].set_visible(False)
    axes_object.spines['left'].set_visible(False)

    # Get rid of ticks.

    axes_object.xaxis.set_ticks_position('none')
    axes_object.yaxis.set_ticks_position('none')
    
    axes_object.xaxis.set_label_text(label, size=8)
    axes_object.xaxis.set_tick_params(labelsize=8)

    # Set scale of plot as roughly [0,(4/3)*max]

    upper_bound = int(max(max(num_data)*4/3,max(num_data)+2))

    # Scale the plot

    plt.xticks(range(0,upper_bound,max(upper_bound/7,1)))

    # Maybe not necessary, but seems to make things look better for now

    plt.tight_layout()

    # Remove pointless y-axis labels in a hacky way

    axes_object.yaxis.set_ticklabels(' ')
    
    return axes_object
    
def query_databases(query):
    output = {}
    for database in DATABASES:
        db = open_database(database)
        db.execute('SELECT * from test_table WHERE pickup_latitude=:start_lat_rnd \
                                          AND pickup_longitude=:start_lon_rnd \
                                          AND dropoff_latitude=:end_lat_rnd \
                                          AND dropoff_longitude=:end_lon_rnd \
                                          AND day_of_week=:day AND hour=:hour',
                        {'start_lat_rnd': query['start_lat_rnd'], 
                         'start_lon_rnd': query['start_lon_rnd'],
                         'end_lat_rnd': query['end_lat_rnd'],
                         'end_lon_rnd': query['end_lon_rnd'],
                         'day': query['day'], 'hour': query['hour']})
        
        output[database] = db.fetchone()
    
    return output
    
def get_raw_coords(list_of_places):
    
    coords = {}
    url_prefix = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    api_key = 'key=AIzaSyDg3Rx-2nU5CtR3DnhUUwAcmgrN6ITUopg'
    
    for place in list_of_places:
        place_format =  place.replace(' ','+')
        link = url_prefix + place_format + '&' + api_key
        

def parse_json_geocode(location_json):
    if location_json['status'] == 'OK':
        most_likely_place = location_json['results'][0]
        most_likely_lat = most_likely_place['geometry']['location']['lat']
        most_likely_lon = most_likely_place['geometry']['location']['lng']
        return [most_likely_lat, most_likely_lon]
    else:
        raise exception_to_be_defined    

def parse_json_distance(journey):
    pass
    


    
# Beginning of app

app = Flask(__name__)

@app.route('/')
def test_site():
    return render_template('test_site.html')
    
@app.route('/output', methods = ['POST'])
def record_data():
    start_point = request.form.get('start_point')
    end_point = request.form.get('end_point')
    day = int(request.form.get('day'))
    hour = int(request.form.get('hour'))
    ampm = request.form.get('ampm')
    if ampm == 'pm':
        hour += 12
    
    text_time = str(hour)+ ' ' + ampm.upper()
    
    day_name = days_of_week[day]
    
    print 'Accepted input'
        
    
    start_format = start_point.replace(' ','+')
    end_format = end_point.replace(' ','+')
    
    url_prefix = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    api_key = 'key=AIzaSyDg3Rx-2nU5CtR3DnhUUwAcmgrN6ITUopg'
    start_link = url_prefix + start_format + '&' + api_key
    end_link = url_prefix + end_format + '&' + api_key
    
    start_query = urllib.urlopen(start_link)
    end_query = urllib.urlopen(end_link)
    
    print 'submitted google geocoding query'
    print start_link
    
    start_data = json.loads(start_query.read())
    end_data = json.loads(end_query.read())
    
    if start_data['status'] == 'OK' and end_data['status'] == 'OK':
        start_lat = start_data['results'][0]['geometry']['location']['lat']
        start_lon = start_data['results'][0]['geometry']['location']['lng']
        end_lat = end_data['results'][0]['geometry']['location']['lat']
        end_lon = end_data['results'][0]['geometry']['location']['lng']
    elif start_data['status'] != 'OK' and end_data['status'] != 'OK':
        message = 'cannot recognize starting address or destination'
        return render_template('error.html', message=message, start_address=start_point,
                    end_address=end_point, text_time=text_time, day_name=day_name) 
    elif start_data['status'] != 'OK' and end_data['status'] == 'OK':
        message = 'cannot recognize starting address'
        return render_template('error.html', message=message, start_address=start_point,
                    end_address=end_point, text_time=text_time, day_name=day_name) 
    else:
        message = 'cannot recognize destination'
        return render_template('error.html', message=message, start_address=start_point,
                    end_address=end_point, text_time=text_time, day_name=day_name) 
   
    print 'extracted data'
    
    # Round coordinates and convert to strings
        
    start_lat_rnd = roundCoord(start_lat, ROUNDING_TOL)
    start_lon_rnd = roundCoord(start_lon, ROUNDING_TOL)
    end_lat_rnd = roundCoord(end_lat, ROUNDING_TOL)
    end_lon_rnd = roundCoord(end_lon, ROUNDING_TOL)
    
    print 'rounded coordinates'
    print start_lat_rnd, start_lon_rnd, end_lat_rnd, end_lon_rnd
        
    conn = sql.connect('taxi_trip_data.db')
    
    print 'connected to database'
    
    cur = conn.cursor()
    
    print 'established cursor'
       
    cur.execute('SELECT * from test_table WHERE pickup_latitude=:start_lat_rnd \
                                          AND pickup_longitude=:start_lon_rnd \
                                          AND dropoff_latitude=:end_lat_rnd \
                                          AND dropoff_longitude=:end_lon_rnd \
                                          AND day_of_week=:day AND hour=:hour',
                        {'start_lat_rnd': start_lat_rnd, 'start_lon_rnd': start_lon_rnd,
                        'end_lat_rnd': end_lat_rnd, 'end_lon_rnd': end_lon_rnd,
                        'day': day, 'hour': hour})
                 
    print 'submitted query'
                 
    data = cur.fetchone()
    print data
                 
    print 'fetched data'

    if data is not None:
        pct10 = str(int(np.rint(data[11]/60)))
        pct25 = str(int(np.rint(data[9]/60)))
        pct50 = str(int(np.rint(data[7]/60)))
        pct75 = str(int(np.rint(data[10]/60)))
        pct90 = str(int(np.rint(data[8]/60)))
        samples = str(data[6])
        pct10dec = str(data[11]/60)
        pct25dec = str(data[9]/60)
        pct50dec = str(data[7]/60)
        pct75dec = str(data[10]/60)
        pct90dec = str(data[8]/60)
        
        concat = pct10dec+','+pct25dec+','+pct50dec+','+pct75dec+','+pct90dec    
    else:
        message = 'insufficent data to compute travel times'
        return render_template('error.html', message=message, start_address=start_point,
                    end_address=end_point, text_time=text_time, day_name=day_name) 
   
    print pct10
        
    conn.close()

    print 'closed connection'
    
    print 'all done!'
    
    pipe = '%7C'
    marker_style_start = 'label:A'+pipe+'color:blue'
    marker_style_end = 'label:B'+pipe+'color:green'
    
    img_prefix = 'http://maps.googleapis.com/maps/api/staticmap?size=500x400'
    window = 'visible='+start_format+pipe+end_format
    marker_start = 'markers='+marker_style_start+pipe+start_format 
    marker_end = 'markers='+marker_style_end+pipe+end_format
    style = 'maptype=terrain'

    
    return render_template('output.html', img_prefix=img_prefix, window=window,
                                marker_start=marker_start, marker_end=marker_end,
                                start_address=start_point, end_address=end_point,
                                style=style, pct10=pct10, pct25=pct25, pct50=pct50,
                                pct75=pct75, pct90=pct90, concat=concat,
                                text_time=text_time, samples=samples, day_name=day_name)
                                

@app.route('/fig-<data>')
def make_figure(data):

    # define "figure" and "axes" objects, where the "axes" is really my figure and
    # "figure" is the thing containing my figure. Confusing.
    
    split_data = data.split(',')
    num_data = [float(num) for num in split_data]

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.set_size_inches(5,1)

    # Make the boxplot and get rid of borders I don't want.
    
    ax.boxplot(num_data,vert=False,widths=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Get rid of ticks.

    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    
    ax.xaxis.set_label_text('Trip time in minutes', size=8)
    ax.yaxis.set_tickparams(labelsize=8)

    # Set scale of plot as roughly [0,(4/3)*max]

    upper_bound = int(max(max(num_data)*4/3,max(num_data)+2))

    # Scale the plot

    plt.xticks(range(0,upper_bound,max(upper_bound/7,1)))

    # Maybe not necessary, but seems to make things look better for now

    plt.tight_layout()

    # Remove pointless y-axis labels in a hacky way

    ax.yaxis.set_ticklabels(' ')

    # Save the figure (untested)
    # Relevant: http://stackoverflow.com/questions/20107414/passing-a-matplotlib-figure-to-html-flask

    img = StringIO.StringIO()
    fig.savefig(img)        #  bbox_inches='tight' ?
    img.seek(0)
    return send_file(img, mimetype='image/png')
    
if __name__ == '__main__':
    app.run(debug=True)