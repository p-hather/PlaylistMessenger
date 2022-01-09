# Playlist Messenger for Spotify

## Create a custom sentence playlist

Playlist Messenger is a Python and Flask based web app that creates a Spotify playlist where the tracks spell out a given sentence.

### About

The backend is purely Python based - this uses Spotipy package to call the Spotify API, search for tracks, and create a playlist. There's also some custom logic to clean and split the user input, and combine words when a matching track isn't found.

The frontend is Flask alongside simple HTML and CSS.

### Deployment

The beta app is currently deployed using Google Cloud App Engine, although the config files have not been included in this repository. A simple guide can be found for this [here](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab).

For development purposes, the app can be run locally (simply run `main.py` and make your redirect URI reference the local port).

### Prerequisites
* All packages in `requirements.txt` installed
* A Spotify app created
* A `.env` file created as per the example, and stored in the same directory as the other files