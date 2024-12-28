import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import re
from flask import Flask, render_template, request

# Spotify API credentials
SPOTIFY_CLIENT_ID = 'cf191d4843ac49ab9b64db5cdb8598c1'
SPOTIFY_CLIENT_SECRET = '4f78cda1184748dfa7ecc8d2cceee369'

# YouTube API credentials
YOUTUBE_API_KEY = 'AIzaSyAhc5UARaLEjPUn-QKumV97dLHeL4h84zQ'

app = Flask(__name__)

def extract_playlist_id(url):
    """Extracts playlist ID from a Spotify playlist URL."""
    match = re.search(r"playlist/([\w\d]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Spotify playlist URL")

def get_spotify_playlist_tracks(playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results['items']:
            track = item['track']
            title = f"{track['name']} {track['artists'][0]['name']}"
            tracks.append(title)
        results = sp.next(results) if results['next'] else None
    return tracks

def search_youtube_video(title):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=title + " music video",
        part="snippet",
        maxResults=1,
        type="video"
    )
    response = request.execute()
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def spotify_to_youtube(playlist_url):
    playlist_id = extract_playlist_id(playlist_url)
    tracks = get_spotify_playlist_tracks(playlist_id)
    youtube_links = []
    for track in tracks:
        link = search_youtube_video(track)
        if link:
            youtube_links.append(link)
    return youtube_links

@app.route('/', methods=['GET', 'POST'])
def index():
    youtube_links = []
    if request.method == 'POST':
        spotify_playlist_url = request.form.get('spotify_url')
        if spotify_playlist_url:
            youtube_links = spotify_to_youtube(spotify_playlist_url)
    return render_template('index.html', youtube_links=youtube_links)

if __name__ == "__main__":
    app.run(debug=True)
