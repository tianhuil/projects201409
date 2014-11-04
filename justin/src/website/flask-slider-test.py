# flask-slider-test.py

# Testing a slider app
from flask import Flask, render_template, request, redirect, json, g, send_file  
import urllib




days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday',
                5: 'Saturday', 6: 'Sunday'}

# Beginning of app

app = Flask(__name__)

@app.route('/')
def test_site():

    days = range(168)
    return render_template('flask-slider-test.html', days=days, days_of_week=days_of_week)
                                
    
if __name__ == '__main__':
    app.run(debug=True)