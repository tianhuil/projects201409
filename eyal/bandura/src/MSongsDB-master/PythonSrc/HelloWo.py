# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 17:28:50 2014

@author: eyalshiv
"""

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(port=55000, debug=True)