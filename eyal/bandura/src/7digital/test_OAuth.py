# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 12:21:18 2014

@author: eyalshiv
"""




#import sys

#from flask import Flask, render_template, request

sys.path.append('/users/eyalshiv/DI/musixplore/src/7digital')

import OAuth




id_7digital = "123456"



song_url = OAuth.get_song_url(id_7digital)

print song_url