from dotenv import load_dotenv
import string
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()


class PlaylistMessenger():
    
    def __init__(self, client, message):
        self.client = client
        self.message = message

    def get_track(self, search_term, pages=5):
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


    def offset_index(self, list_obj, start_index, max_offset=2):
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
                "offset": (end_index-start_index)-1,  # can be adapted in future to also look backwards
                "slice": list_obj[start_index:end_index]
            })
        return slices


    def process_message(self):
        remove_chars = string.punctuation.replace("'", "")  # all punctuation except apostrophe
        clean_message = self.message.replace('-', ' ')  # replace hyphen with whitespace
        clean_message = clean_message.translate(str.maketrans('', '', remove_chars))  # remove special characters/punctuation
        clean_message = clean_message.replace('\n', ' ')  # replace newline character with whitespace
        return [word.strip() for word in clean_message.split(' ') if word != '']  # split, strip leading/trailing whitespace


    def build_playlist(self):
        words = self.process_message()
        skip = 0

        items = []
        for n, word in enumerate(words):

            if skip:
                print(f'Skipping word {n} - {word}')
                skip -= 1
                continue

            track = self.get_track(word)

            if not track:
                word_offsets = self.offset_index(words, n)

                try:
                    for offset in word_offsets:
                        track = self.get_track(' '.join(offset['slice']))

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


if __name__ == '__main__':
    message = '''
    You need to let the little things that would ordinarily bore you suddenly thrill you.
    '''
    client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    pm = PlaylistMessenger(client, message)
    pm.build_playlist()
