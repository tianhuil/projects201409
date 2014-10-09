# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 12:05:46 2014

@author: eyalshiv
"""


from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id



@app.route('/play/<song_id>')
def play_song(song_id):
    
    # play preview from 7digital
    
    
    # show the song details
    
    song_string = get_song_url(song_id)
    return song_string







from flask import render_template

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)






if __name__ == '__main__':
    app.debug = True
    app.run()
    
    