import logging
import string
import spotipy


class PlaylistMessenger:
    """
    Creates a Spotify playlist where the tracks spell out a given message.

    Args:
    client (Spotify Client API object)
    playlist_name (str): the name of the playlist
    message (str): the message that will be turned into playlist tracks. 

    The instance 'status' attribute provides a user facing output from the process run,
    whereas the 'playlist_id' attribute provides the created playlist ID, if successful.
    """

    def __init__(self, client, playlist_name, message):
        self.client = client
        self.user_id = self.client.me()['id']
        self.playlist_name = playlist_name
        self.message = message
        self.all_words = []
        self.not_found_words = []
        self.playlist_id = None
        self.status = None

    def process_message(self):
        """
        Clean the message and split into a list of words.
        """
        remove_chars = string.punctuation.replace("'", "")  # all punctuation except apostrophe
        clean_message = self.message.replace('-', ' ')  # replace hyphen with whitespace
        clean_message = clean_message.translate(str.maketrans('', '', remove_chars))  # remove special characters/punctuation
        clean_message = clean_message.replace('\n', ' ')  # replace newline character with whitespace
        return [word.strip() for word in clean_message.split(' ') if word != '']  # split, strip leading/trailing whitespace

    def get_tracks(self):
        """
        Orchestrates finding a track for each word in the given message.
        """
        self.all_words = self.process_message()
        skip = 0  # If set, that iteration will be skipped (used if words are combined)

        items = []
        for n, word in enumerate(self.all_words):

            if skip:
                logging.info(f'Skipping word {n} - {word}')
                skip -= 1
                continue

            track = self.find_track(word)

            if not track:
                word_offsets = self.offset_index(self.all_words, n)

                try:
                    for offset in word_offsets:
                        track = self.find_track(' '.join(offset['slice']))

                        if track:
                            skip = offset['offset']  # Skip the next n iterations
                            break

                except TypeError as e:
                    logging.info(f"Error raised: {e} - likely caused by attempting to offset last item in list")
            
            if track:
                items.append(track)
            else:
                logging.info(f'Could not find a track with the name {word}')
                self.not_found_words.append(word)
        
        return items

    def find_track(self, search_term, pages=5):
        """
        Searches the Spotify API for a track matching a given search term - returns the track URI when found.
        """
        logging.info(f"Looking for a track that matches '{search_term}'")

        for page in range(0, 50*pages, 50):  # maximum of 50 results per search - search more than once if necessary
            try:
                results = self.client.search(q=search_term, type='track', limit=50, offset=page)

                for n, item in enumerate(results['tracks']['items']):
                    if item['name'].lower() == search_term.lower():
                        artists = [artist['name'] for artist in item['artists']]
                        name = item['name']
                        uri = item['uri']  # ['id'] also available
                        logging.info(f"Found matching track on iteration {page+n+1} - {name} by {', '.join(artists)}")
            
                        return uri

            except spotipy.SpotifyException:
                logging.info(f'Spotipy client raised error on iteration {page+n+1} - likely exceeded page limit')
                break
                
        logging.info('No matching track found')
        return None

    def offset_index(self, list_obj, start_index, max_offset=2):
        """
        Splits a list into slices, looking ahead from a given index
        """

        max_index = min(start_index+max_offset, len(list_obj)-1)
        if start_index == max_index:
            logging.info(f'Given index ({start_index}) is the end of the list, unable to offset')
            return
        
        logging.info(f"Attempting to offset list from index {start_index}, item '{list_obj[start_index]}'")
        slices = []
        for end_index in range(start_index+2, max_index+2):  # +2 to account for range and list indexing
            slices.append({
                "offset": (end_index-start_index)-1,  # can be adapted in future to also look backwards
                "slice": list_obj[start_index:end_index]
            })
        return slices

    def build_playlist(self, tracks):
        """
        Create an empty playlist and load the tracks.
        """
        logging.info(f'Creating playlist with name: {self.playlist_name}')
        playlist = self.client.user_playlist_create(user=self.user_id, name=self.playlist_name) # TODO add description
        self.playlist_id = playlist['id']
        logging.info(f'Playlist ID is {self.playlist_id}')

        logging.info(f'Attempting to add {len(tracks)} tracks')
        self.client.user_playlist_add_tracks(user=self.user_id, playlist_id=self.playlist_id, tracks=tracks)

    def run(self):
        """
        Orchestrate entire process, set 'status' attribute.
        """
        tracks = self.get_tracks()
        if tracks:
            self.build_playlist(tracks)
            self.status = f'Done! Found {len(self.all_words)-len(self.not_found_words)}/{len(self.all_words)} words'
        else:
            logging.info('No tracks found')
            self.status = 'Could not find any tracks'

        logging.info('Done')
