
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import string 

from flask import Flask, jsonify, render_template, request, redirect
#import requests

sys.path.append('../../..')

sys.path.append('../../../7digital')
import OAuth
sys.path.append('../../../7digital/python-7Digital-master/lib')
import py7D

import MX_traverse
#import MX_constructGraph
#import MX_common
from MX_common import p

#from MX_traverse import pickNextSongsWrapped

#from flask_wtf import Form
#from wtforms import StringField
#from wtforms.validators import DataRequired


# global variables 
g_p = dict()
g_p['play_interval'] = ['3','4']
g_7digital_cur = ''
g_7digital_nexts = []
#g_search_term = ''
g_song_features = None
g_nexts_features = None
g_next_choice = 0


g_p['save_playlist'] = True
g_p['playlist_pref'] = 'PL_current_'

#g_history_list = ['[recently played songs]']


#class MyForm(Form):
#    name = StringField('name', validators=[DataRequired()])




app = Flask(__name__)
app.config.from_object('config')
#app.config["DEBUG"] = True  # Only include this while you are testing your app

@app.route("/")
def hello():
    return redirect("/bandura")



#@app.route('/submit', methods=('GET', 'POST'))
#def submit():
#    form = MyForm()
#    if form.validate_on_submit():
#        return redirect('/success')
#    return render_template('submit.html', form=form)

@app.route("/next_song_choice", methods=["GET", "POST"])
def next_song_choice():
    print "sdfsdfdf"
    print "next: " + str(request.form["suggestions"])
    return None
    #g_next_choice = 


@app.route("/bandura_search", methods=["GET", "POST"])
def bandura_search():
    global g_7digital_cur
    global g_7digital_nexts
    global g_song_features
    global g_nexts_features

    print "bandura_search"
    if request.method == "POST":
        print "POSTT"
        search_term = request.form["search_term"]
        if search_term != '':
            g_7digital_cur = ''
            n_search_results = 2
            while g_7digital_cur=='' and n_search_results<=1000:
                n_search_results *= 5              
                z = py7D.request('track', 'search', q=search_term, pagesize=n_search_results)
                #print z['response']['searchResults'], z['response']['searchResults']['totalItems']
                if int(z['response']['searchResults']['totalItems'])>0:
                    search_results = z['response']['searchResults']['searchResult']
                    search_results2 = list()
                    print "possible matches: " + str(len(search_results))
                    for result in search_results:
                        record=dict()
                        record['track_7digitalid']  = result['track']['@id']
                        record['title']             = result['track']['title']
                        record['artist']            = result['track']['artist']['name']
                        print record['track_7digitalid'], record['title'], record['artist']
                        search_results2.append(record)
                    best_match = MX_traverse.findInSongsDB( [x['track_7digitalid'] for x in search_results2] )
                    g_7digital_cur = best_match[0]
            #print type(g_7digital_cur), len(g_7digital_cur), g_7digital_cur==''
            print "best match: " + g_7digital_cur
            if g_7digital_cur != '':
                print "gotcha!"
                g_7digital_nexts      = MX_traverse.pickNextSongsWrapped( g_7digital_cur );
                g_song_features       = MX_traverse.get_song_by_7digital( g_7digital_cur )
                g_nexts_features      = [MX_traverse.get_song_by_7digital( x ) for x in g_7digital_nexts[0]]
                song_url              = MX_traverse.get_song_url( g_7digital_cur )
#                if g_p['save_playlist']:
#                    g_p['playlist_file'] = g_p['playlist_pref'] + time.strftime("%Y%m%d-%H%M%S") + '.csv'
#                    MX_traverse.addSongToPlaylist( g_p['playlist_file'], g_song_features, song_url )
                context = {'cons_tempo'    : p['conservation']['tempo'],\
                           'cons_loudness'    : p['conservation']['loudness'],\
                           'cons_year'    : p['conservation']['year'],\
                           'cons_artist_familiarity'    : p['conservation']['artist_familiarity'],\
                           'cons_valence'    : p['conservation']['valence'],\
                           'cons_energy'    : p['conservation']['energy'],\
                           'cons_danceability'    : p['conservation']['danceability'],\
                           'cons_acousticness'    : p['conservation']['acousticness'],\
                           'cons_liveness'    : p['conservation']['liveness'],\
                           'cons_speechiness'    : p['conservation']['speechiness'],\
                           'cons_instrumentalness'    : p['conservation']['instrumentalness'],\
                           'noisyness'    : p['noisyness'],\
                           'song_url'       : song_url+'#t='+g_p['play_interval'][0]+","+g_p['play_interval'][1],\
                           'id_7digital'    : g_7digital_cur,\
                           'title'          : g_song_features[p['invkey']['title']],\
                           'artist'         : g_song_features[p['invkey']['artist_name']],\
                           'history_future'   : [ ss[1] for ss in p['suggestions'] ], \
                           'history_cur'      : p['currently_playing'][1], \
                           'history_past'     : [ ss[1] for ss in p['recently_played'] ] }
#                           'history' : string.join([ss[1] for ss in p['recently_played']], "<br>") }
                for i in range(len(g_nexts_features)):
                    context['n'+str(i)+'_id_7digital'] = g_nexts_features[i][p['invkey']['track_7digitalid']]
                    context['n'+str(i)+'_title']       = g_nexts_features[i][p['invkey']['title']]
                    context['n'+str(i)+'_artist']      = g_nexts_features[i][p['invkey']['artist_name']]
                return render_template("bandura.html", **context);
            else:
                return render_template("bandura.html");
        else:
            return render_template("bandura.html");

# SOBOAQC12A8C13E3E9
@app.route("/bandura", methods=["GET","POST"])
def bandura():
    global g_p
    global g_7digital_cur
    global g_7digital_nexts  
    global g_song_features
    global g_nexts_features
    global g_next_choice
    global p
#    global g_search_term

    print "bandura"
#    z = request.form["suggestions"]

    #print str(request.values)
    #print str(request.form["suggestions"])

    if request.method == "POST":
        print "POST"
        g_next_choice = int(request.form["suggestions"])#min(xxx, len(g_7digital_nexts)-1);
        p['conservation']['tempo'] = float(request.form["cons_tempo"])
        p['conservation']['loudness'] = float(request.form["cons_loudness"])
        p['conservation']['year'] = float(request.form["cons_year"])
        p['conservation']['artist_familiarity'] = float(request.form["cons_artist_familiarity"])
        p['conservation']['valence'] = float(request.form["cons_valence"])
        p['conservation']['energy'] = float(request.form["cons_energy"])
        p['conservation']['danceability'] = float(request.form["cons_danceability"])
        p['conservation']['acousticness'] = float(request.form["cons_acousticness"])
        p['conservation']['liveness'] = float(request.form["cons_liveness"])
        p['conservation']['speechiness'] = float(request.form["cons_speechiness"])
        p['conservation']['instrumentalness'] = float(request.form["cons_instrumentalness"])
        p['noisyness'] = float(request.form["noisyness"])

        #print "cons year: " + str(p['conservation']['year'])
        #p['conservation']['year'] = 30
        if g_next_choice >= 0:
            print "cur song id exists"
            print g_7digital_nexts[0]
            g_7digital_cur   = g_7digital_nexts[0][g_next_choice]
            g_song_features  = g_nexts_features[g_next_choice]
            song_url         = OAuth.get_song_url(g_7digital_cur);
#            if g_p['save_playlist']:
#                MX_traverse.addSongToPlaylist( g_p['playlist_file'], g_song_features, song_url )
            g_7digital_nexts = MX_traverse.pickNextSongsWrapped( g_7digital_cur );
            g_nexts_features = [MX_traverse.get_song_by_7digital( x ) for x in g_7digital_nexts[0]]
            ##,

#            histoire = p['recently_played']
#            history_future = p['suggestions']
#            history_cur    = histoire[0]
#            print histoire.pop()
#            history_past   = histoire.pop()

            print p['conservation']['tempo'], p['conservation']['loudness'],  p['conservation']['year'], p['conservation']['artist_familiarity'], p['noisyness']
            context = { 'cons_tempo'    : p['conservation']['tempo'],\
                        'cons_loudness'    : p['conservation']['loudness'],\
                        'cons_year'    : p['conservation']['year'],\
                        'cons_artist_familiarity'    : p['conservation']['artist_familiarity'],\
                        'cons_valence'    : p['conservation']['valence'],\
                        'cons_energy'    : p['conservation']['energy'],\
                        'cons_danceability'    : p['conservation']['danceability'],\
                        'cons_acousticness'    : p['conservation']['acousticness'],\
                        'cons_liveness'    : p['conservation']['liveness'],\
                        'cons_speechiness'    : p['conservation']['speechiness'],\
                        'cons_instrumentalness'    : p['conservation']['instrumentalness'],\
                        'noisyness'    : p['noisyness'],\
                        'song_url'      : song_url+"#t="+g_p['play_interval'][0]+","+g_p['play_interval'][1],\
                        'id_7digital'   : g_7digital_cur,\
                        'title'         : g_song_features[p['invkey']['title']],\
                        'artist'        : g_song_features[p['invkey']['artist_name']],\
                        'history_future'   : [ ss[1] for ss in p['suggestions'] ], \
                        'history_cur'      : p['currently_playing'][1], \
                        'history_past'     : [ ss[1] for ss in p['recently_played'] ] }
#                        'history' : string.join([ss[1] for ss in p['recently_played']], "<br>") }
            for i in range(len(g_nexts_features)):
                context['n'+str(i)+'_id_7digital'] = g_nexts_features[i][p['invkey']['track_7digitalid']]
                context['n'+str(i)+'_title']       = g_nexts_features[i][p['invkey']['title']]
                context['n'+str(i)+'_artist']      = g_nexts_features[i][p['invkey']['artist_name']]
            return render_template("bandura.html", **context);
        else:
            print "cur song id does NOT exists"
            return render_template("bandura.html");
    else:
        print "GET"
        return render_template("bandura.html")



@app.errorhandler(404)
def page_not_found(error):
    return "Sorry not sorry - this page was NOT found", 404  




# always the last function !!!!!!
if __name__ == "__main__":

    #MX_common.init_globals_static()
    #MX_common.init_globals_run()
    app.run(host="0.0.0.0", port=int("4070"))
