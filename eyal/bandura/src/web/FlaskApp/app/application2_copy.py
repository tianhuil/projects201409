import sys

from flask import Flask, jsonify, render_template, request, redirect
import requests

sys.path.append('/users/eyalshiv/DI/musixplore/src/7digital')
import OAuth

sys.path.append('/users/eyalshiv/DI/musixplore/src')
#from MX_traverse import pickNextSongWrapped
import MX_traverse

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])





app = Flask(__name__)
app.config.from_object('config')
#app.config["DEBUG"] = True  # Only include this while you are testing your app

@app.route("/")
def hello():
    return redirect("/play_test")



@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('submit.html', form=form)



#@app.route("/search/<search_query>")
#def search(search_query):
#  	url = "https://api.github.com/search/repositories?q=" + search_query
#  	response_dict = requests.get(url).json()
#  	return jsonify(response_dict)
#@app.route("/search")
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
    	print "lala"
        url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        print url
        response_dict = requests.get(url).json()
        #return jsonify(response_dict)
        return render_template("results.html", api_data=response_dict)
    else: # request.method == "GET"
    	print "moshe"
        return render_template("search.html")

	# Space%20Invaders%20HTML5




# SOBOAQC12A8C13E3E9
@app.route("/play_test", methods=["GET","POST"])
def play_test():
    if request.method == "POST":
#		if request.form["user_play"] == "PlayThis":
        print "this!"
#			echonest_id = request.form["user_play"]
#			id_7digital = get_7digital_id( echonext_id ) 
#			song_url = OAuth.get_song_url(id_7digital)
#			print song_url
#			return render_template("play_specific.html", api_data=song_url)
#	else:
        print "next! " + request.form["user_play"];
#			echonest_id = "SOBOAQC12A8C13E3E9"#request.form["user_play"]
#			echonest_id_next = MX_traverse.pickNextSongWrapped( echonest_id ) #echonext_id
#			print echonest_id, echonest_id_next
        id_7digital = request.form["user_play"]#MX_traverse.get_7digital_id( echonest_id_next ) 
        song_url = OAuth.get_song_url(id_7digital);
#        print song_url
        id_7digital_next = MX_traverse.pickNextSongWrapped( id_7digital );#echonext_id
        request.form["user_play"] = id_7digital_next
        return render_template("play_specific.html", api_data=song_url)
    else:
        print "moshe"
        return render_template("play_test.html")



@app.errorhandler(404)
def page_not_found(error):
    return "Sorry, this page was not found.", 404  




# always the last function !!!!!!
if __name__ == "__main__":
    print "init"
    MX_traverse.init_globals()
    app.run(host="0.0.0.0", port=int("4070"))
