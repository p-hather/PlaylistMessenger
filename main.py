import logging
from flask import Flask, render_template, request, redirect, session
import spotipy
import os
import requests
from playlist import PlaylistMessenger


CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET= os.environ.get('CLIENT_SECRET')
REDIRECT_URI= os.environ.get('REDIRECT_URI')
SCOPE = 'playlist-modify-public'


# create Flask app
app = Flask(__name__, template_folder='html')
app.secret_key = os.environ.get('FLASK_KEY')


@app.route("/")
def login():
    """
    authorization-code-flow - Step 1
    Redirect to Spotify Auth page, request authorisation from user.
    """
    auth_url = f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
    return redirect(auth_url)


@app.route("/callback")
def api_callback(): 
    """
    authorization-code-flow - Step 2
    Application requests refresh and access tokens, Spotify returns them.
    """
    session.clear()
    code = request.args.get('code')

    auth_token_url = f"https://accounts.spotify.com/api/token"
    data = {
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":REDIRECT_URI,
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET,
        }

    res = requests.post(auth_token_url, data=data)
    res_body = res.json()
    session["toke"] = res_body.get("access_token")

    # redirect to index.html after authorization is done
    return redirect("index")


@app.route('/index', methods=['POST', 'GET'])
def index():
    """
    authorization-code-flow - Step 3
    Use the access token from the previous step to access the Spotify API
    """
    output = ''
    playlist_id = ''
    
    if request.method == 'POST':
        client = spotipy.Spotify(auth=session['toke'])  # get token

        title = request.form['title']
        message = request.form['message']

        # instantiate python class and run process
        try:
            logging.info('Instantiating Python class')
            pm = PlaylistMessenger(client, title, message)
            pm.run()
            output = pm.status
            logging.info(f'Received status from Python script: {output}')
            playlist_id = pm.playlist_id
        except:
            logging.info('Error occurred in Python script')
            output = 'An error occurred'
    
    return render_template('index.html', output=output, playlist_id=playlist_id)


# run Flask app
if __name__ == '__main__':
    app.run()
