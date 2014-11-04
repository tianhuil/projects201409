from flask import Flask, render_template, redirect, request, session
app = Flask(__name__)

@app.route('/devfest')
def devfest():
    return redirect('http://devfe.st/')

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html',
                               name = session['username'])
    return redirect('/test_play')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect('/')
    


@app.route('/test_play', methods=['GET', 'POST'])
def test_play():
    if request.method == 'GET':
        song_id = request.form["user_play"]

        #song_url = OAuth.get_song_url(song_id)
        return "let's play!"#song_url        
#        return render_template('login.html')
    elif request.method == 'POST':
        song_id = request.form["user_play"]

        #song_url = OAuth.get_song_url(song_id)
        return "let's play!"#song_url        
#        username = request.form['username']
#        session['username'] = username
#        return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'l34GE0q1l1U+4D8c4S/1Yg=='
    app.run(host="127.0.0.1", port=int("4080"), debug=True)



"""
    if request.method == "POST":
        url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        response_dict = requests.get(url).json()
        return jsonify(response_dict)
    else: # request.method == "GET"
        return render_template("search.html")
"""