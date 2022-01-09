# Playlist Messenger for Spotify

## Create a custom sentence playlist

Playlist Messenger is a Python and Flask based web app that creates a Spotify playlist where the tracks spell out a given sentence.

### About

The backend is purely Python based - this uses Spotipy package to call the Spotify API, search for tracks, and create a playlist. There's also some custom logic to clean and split the user input, and combine words when a matching track isn't found.

The frontend is Flask alongside simple HTML and CSS.

Auth is handled by redirecting the user to the Spotify app authorisation page, and passing a token back to Spotipy to create a client instance.

### Deployment

The beta app is currently deployed using Google Cloud App Engine, although the config files have not been included in this repository. A simple guide can be found for this [here](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab).

For development purposes, the app can be run locally (simply run `main.py` and make your redirect URI reference the local port).

### Prerequisites
* All packages in `requirements.txt` installed
* A Spotify app created
* A `.env` file created as per the example, and stored in the same directory as the other files

### Screenshots
<img width="750" alt="Screenshot 2022-01-09 at 18 23 27" src="https://user-images.githubusercontent.com/75444929/148695267-27f90393-06ae-4e1f-8821-4e49f33faadb.png">

<img width="750" alt="Screenshot 2022-01-09 at 18 20 09" src="https://user-images.githubusercontent.com/75444929/148695285-5002ad07-a2cf-490a-a176-a9184a6cf5f7.png">

<img width="750" alt="Screenshot 2022-01-09 at 18 20 37" src="https://user-images.githubusercontent.com/75444929/148695306-79663944-13b2-4bf4-9a84-573508e19711.png">





