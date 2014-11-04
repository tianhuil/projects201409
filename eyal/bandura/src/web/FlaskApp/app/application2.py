
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import string 

from flask import Flask, jsonify, render_template, request, redirect

sys.path.append('../../..') 

sys.path.append('../../../7digital')
import OAuth
sys.path.append('../../../7digital/python-7Digital-master/lib')
import py7D

import MX_traverse
from   MX_common import p


# global web-application variables 
g_p = dict()
g_p['play_interval'] = ['3','9']
g_7digital_cur = ''
g_7digital_nexts = list()
g_song_features = None
g_nexts_features = None
g_next_choice = 0

g_p['save_playlist'] = False
g_p['playlist_pref'] = 'PL_current_'



app = Flask(__name__)
app.config.from_object('config')
#app.config["DEBUG"] = True  # Only include this while you are testing your app

@app.route("/")
def hello():
    print os.getcwd()
    return redirect("/bandura")


@app.route("/next_song_choice", methods=["GET", "POST"])
def next_song_choice():
    print "sdfsdfdf"
    print "next: " + str(request.form["suggestions"])
    return None


def packContext( mode=0 ):    
    global p
    global g_p

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
               'history_future'   : [ ss[1] for ss in p['suggestions'] ], \
               'history_cur'      : p['currently_playing'][1], \
               'history_past'     : [ ss[1] for ss in p['recently_played'] ], \
               'debug_neighbors'     : p['debug_neighbors'], \
               'play_start_sec'     : g_p['play_interval'][0], \
               'play_stop_sec'      : g_p['play_interval'][1] }
    return context


def setCurrentCalcNext( context = dict() ):
    global p
    global g_p
    global g_7digital_cur
    global g_7digital_nexts
    global g_song_features

    g_7digital_nexts      = MX_traverse.pickNextSongsWrapped( g_7digital_cur );
    g_song_features       = MX_traverse.get_song_by_7digital( g_7digital_cur )
    g_nexts_features      = [MX_traverse.get_song_by_7digital( x ) for x in g_7digital_nexts[0]]
    song_url              = MX_traverse.get_song_url( g_7digital_cur )
    if g_p['save_playlist']:
        g_p['playlist_file'] = g_p['playlist_pref'] + time.strftime("%Y%m%d-%H%M%S") + '.csv'
        MX_traverse.addSongToPlaylist( g_p['playlist_file'], g_song_features, song_url )
    
    context['song_url']    = song_url+'#t='+str(g_p['play_interval'][0])+","+str(g_p['play_interval'][1])
    context['id_7digital'] = g_7digital_cur
    context['title']       = g_song_features[p['invkey']['title']]
    context['artist']      = g_song_features[p['invkey']['artist_name']]

    for i in range(len(g_nexts_features)):
        context['n'+str(i)+'_id_7digital'] = g_nexts_features[i][p['invkey']['track_7digitalid']]
        context['n'+str(i)+'_title']       = g_nexts_features[i][p['invkey']['title']]
        context['n'+str(i)+'_artist']      = g_nexts_features[i][p['invkey']['artist_name']]

    return context


@app.route("/bandura_search", methods=["GET", "POST"])
def bandura_search():
    global g_7digital_cur
    global g_7digital_nexts
    global g_song_features
    global g_nexts_features

    print "bandura_search"

    if request.method == "POST":
        print "'bandura search' called by POST"

        #updateParamsFromSite( request.form )

        context = packContext( 0 );

        search_term = request.form["search_term"]
        if search_term != '':

            # seach the exact term in the DB
            best_match = [MX_traverse.get_song_id_by_token(search_term)]

            if best_match[0]=='':
                # if the exact term wasn't found in the DB, perform a more flexible search using the EchoNest API
                g_7digital_cur = ''
                n_search_results = 2
                while best_match[0]=='' and n_search_results<=1000:
                    n_search_results *= 5              
                    z = py7D.request('track', 'search', q=search_term, pagesize=n_search_results)
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
                        # intersect the EchoNest results with our DB    
                        best_match = MX_traverse.findInSongsDB( [x['track_7digitalid'] for x in search_results2] )

            if best_match[0]!='':
                g_next_choice = 0
                g_7digital_nexts = [[best_match[0]]]
                g_nexts_features = list()
                g_nexts_features.append( tuple(MX_traverse.get_song_by_7digital( g_7digital_nexts[0][g_next_choice] )) )
                print "best match: " + g_nexts_features[g_next_choice][0]
            else:
                print "no match..."
        else:
            print "No search term..."
    else:
        context = dict()
        "'bandura_search' called by GET"
    render_template("bandura.html", **context);
    return redirect("/bandura")


def updateParamsFromSite( formo ):
    global p
    global g_next_choice

    if "suggestions" in formo.keys():
        g_next_choice = int(formo["suggestions"])
    else:
        print "no suggestions"
        g_next_choice = 0
    p['conservation']['tempo']          = float(formo["cons_tempo"])
    p['conservation']['loudness']       = float(formo["cons_loudness"])
    p['conservation']['year']           = float(formo["cons_year"])
    p['conservation']['artist_familiarity'] = float(formo["cons_artist_familiarity"])
    p['conservation']['valence']        = float(formo["cons_valence"])
    p['conservation']['energy']         = float(formo["cons_energy"])
    p['conservation']['danceability']   = float(formo["cons_danceability"])
    p['conservation']['acousticness']   = float(formo["cons_acousticness"])
    p['conservation']['liveness']       = float(formo["cons_liveness"])
    p['conservation']['speechiness']    = float(formo["cons_speechiness"])
    p['conservation']['instrumentalness'] = float(formo["cons_instrumentalness"])
    p['noisyness'] = float(formo["noisyness"])

    g_p['play_interval'][0] = int(formo["play_start_sec"])
    g_p['play_interval'][1] = int(formo["play_stop_sec"])


@app.route("/bandura", methods=["GET","POST"])
def bandura():
    global p
    global g_p
    global g_7digital_cur
    global g_7digital_nexts  
    global g_song_features
    global g_nexts_features
    global g_next_choice

    print "bandura"
    context = packContext( 0 );

    if 1: #request.method == "POST":
        if request.method == "POST":
            print "'bandura' called by POST"
            updateParamsFromSite( request.form )

        context = packContext( 0 ); 

        if g_7digital_nexts:
            print "cur song id exists"
            print g_7digital_nexts
            g_7digital_cur   = g_7digital_nexts[0][g_next_choice]
            g_song_features  = g_nexts_features[g_next_choice]
            song_url         = OAuth.get_song_url(g_7digital_cur);
            g_7digital_nexts = MX_traverse.pickNextSongsWrapped( g_7digital_cur );
            g_nexts_features = [MX_traverse.get_song_by_7digital( x ) for x in g_7digital_nexts[0]]
            if g_p['save_playlist']:
                MX_traverse.addSongToPlaylist( g_p['playlist_file'], g_song_features, song_url )

            context['song_url']     = song_url+"#t="+str(g_p['play_interval'][0])+","+str(g_p['play_interval'][1])
            context['id_7digital']  = g_7digital_cur
            context['title']        = g_song_features[p['invkey']['title']]
            context['artist']       = g_song_features[p['invkey']['artist_name']]
                        
            for i in range(len(g_nexts_features)):
                context['n'+str(i)+'_id_7digital'] = g_nexts_features[i][p['invkey']['track_7digitalid']]
                context['n'+str(i)+'_title']       = g_nexts_features[i][p['invkey']['title']]
                context['n'+str(i)+'_artist']      = g_nexts_features[i][p['invkey']['artist_name']]
        else:
            print "cur song id does NOT exists"
    else:
        print "'bandura' called by GET"
    print "rendering bandura"
    return render_template("bandura.html", **context);


@app.route("/bandura_pause", methods=["GET","POST"])
def bandura_pause():

    global p
    global g_7digital_cur
    global g_song_features

    print "bandura_pause"

    context = packContext(0)

    if 1: #request.method == "POST":

        #updateParamsFromSite( request.form )

        # the one field I'm nulling is the URL        
        context['song_url'] = ""
        context['id_7digital'] = g_7digital_cur
        context['title'] = g_song_features[p['invkey']['title']]
        context['artist'] = g_song_features[p['invkey']['artist_name']]

    else:
        print "'bandura_pause' called by GET"

    return render_template("bandura.html", **context);


@app.route("/bandura_lucky", methods=["GET","POST"])
def bandura_lucky():
    global g_7digital_cur
    global g_7digital_nexts
    global g_song_features
    global g_nexts_features

    print "bandura_lucky"

    context = packContext( 0 );

    if 1: #request.method == "POST":
        #if request.method == "POST":
        #    updateParamsFromSite( request.form )

        random_match = MX_traverse.pickRandomSong()

        g_next_choice = 0
        g_7digital_nexts = [[random_match]]
        g_nexts_features = list()
        print g_7digital_nexts[0][g_next_choice]
        g_nexts_features.append( tuple(MX_traverse.get_song_by_7digital( g_7digital_nexts[0][g_next_choice] )) )
        print "random choice: " + g_nexts_features[g_next_choice][0]

    render_template("bandura.html", **context);
    return redirect("/bandura")


@app.errorhandler(404)
def page_not_found(error):
    return "Sorry not sorry - this page was NOT found", 404  


# always the last function !!!!!!
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("4070"))
