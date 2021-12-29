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
            results = client.search(q=search_term, type='track', limit=50, offset=page)

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


def offset_index(list_obj, start_index, max_offset=2):
    """
    Splits a list into slices, looking ahead from a given index
    """

    max_index = min(start_index+max_offset, len(list_obj)-1)
    if start_index == max_index:
        print(f'Given index ({start_index}) is the end of the list, unable to offset')
        return
    
    print(f"Attempting to offset list from index {start_index}, item '{list_obj[start_index]}'")
    slices = []
    for end_index in range(start_index+2, max_index+2):  # +2 to account for range and list indexing
        slices.append({
            "offset": (end_index-start_index)-1,
            "slice": list_obj[start_index:end_index]
        })
    return slices


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

        track = get_track(word)

        if not track:
            word_offsets = offset_index(words, n)

            try:
                for offset in word_offsets:
                    track = get_track(' '.join(offset['slice']))

                    if track:
                        skip = offset['offset']  # Skip the next n iterations
                        break
            except TypeError as e:
                print(f"Error raised: {e} - likely caused by attempting to offset last item in list")
        
        if track:
            items.append(track)
        else:
            print(f'Could not find a track with the name {word}')
    
    return items

sentence = '''
You need to let the little things that would ordinarily bore you suddenly thrill you.
'''

tracks = build_sentence(sentence)
for track in tracks:
    print(track)
