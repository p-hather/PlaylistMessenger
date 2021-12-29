from dotenv import load_dotenv
import string
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


load_dotenv()
client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def get_track(search_term, pages=5):
    print(f"Looking for a track that matches '{search_term}'")

    for page in range(0, 50*pages, 50):  # maximum of 50 results per search - search more than once if necessary
        try:
            results = client.search(q=f'track:"{search_term}"', type='track', limit=50, offset=page)

            for n, item in enumerate(results['tracks']['items']):
                if item['name'].lower() == search_term.lower():
                    artists = [artist['name'] for artist in item['artists']]
                    name = item['name']
                    uri = item['uri']  # ['id'] also available
                    print(f"Found matching track on iteration {page+n+1} - {name} by {', '.join(artists)}")
        
                    return {
                        'artists': artists,
                        'name': name,
                        'uri': uri
                    }

        except spotipy.SpotifyException:
            print(f'Spotipy client raised error on iteration {page+n+1} - likely exceeded page limit')
            break
            
    print('No matching track found')
    return None


def offset_index(list_obj, index, max_offset=3):
    print(f"Offsetting list from index {index}, item '{list_obj[index]}'")
    offset_lists = []
    for n in range(2, max_offset+1):
      for i in range(1, n+1):
        start = index+(i-n)
        end = index+i
        if start >= 0 and end <= len(list_obj):
          offset_list = list_obj[start:end]
          offset_lists.append({
              "back": index-start,
              "forward": (end-index)-1,
              "sequence": offset_list})
    return offset_lists


def clean_input(sentence):
    remove_chars = string.punctuation.replace("'", "")  # all punctuation except apostrophe
    sentence = sentence.replace('-', ' ')  # replace hyphen with whitespace
    sentence = sentence.translate(str.maketrans('', '', remove_chars))  # remove special characters/punctuation
    sentence = sentence.replace('\n', ' ')  # replace newline character with whitespace
    return [word.strip() for word in sentence.split(' ') if word != '']  # split, strip leading/trailing whitespace


def build_sentence(sentence):
    words = clean_input(sentence)
    skip = 0

    items = []
    for n, word in enumerate(words):

        if skip:
            print(f'Skipping word {n} - {word}')
            skip -= 1
            continue

        print(f'Word {n} - {word}')
        track = get_track(word)

        if not track:
            word_offsets = offset_index(words, n)

            for offset in word_offsets:
                track = get_track(' '.join(offset['sequence']))

                if track:
                    print(offset)

                    if offset['back']:
                        print(f"Attempting to delete items {n-offset['back']}:{n} - {items[n-offset['back']:n]}")
                        del items[n-offset['back']:n]
                        print(f'New items looks like:\n{items}')

                    if offset['forward']:
                        skip = offset['forward']  # Skip the next n iterations

                    break
        
        if track:
            items.append(track)
        else:
            print(f'Could not find a track with the name {word}')
    
    return items

sentence = '''
fall in love with eyes closed
'''

tracks = build_sentence(sentence)
for track in tracks:
    print(track)
