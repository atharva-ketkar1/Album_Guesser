from requests import get
import json
import random

# Methods that are the backend for the game
class BackendMethods:
    def __init__(self, token):
        self.token = token

    # Authorization for Spotify API using the token
    def get_auth_header(self):
        return {"Authorization": "Bearer " + self.token}

    # Search for a specific artist 
    def search_for_artist(self, artist_name):
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        query = f"?q={artist_name}&type=artist&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        try:
            json_result = json.loads(result.content)["artists"]["items"]
        except KeyError:
            print("Error: Failed to retrieve artist information.")
            return None

        if len(json_result) == 0:
            print("No artist with this name exists")
            return None

        return json_result[0]

    # Gets a random album from a specific artist
    def get_random_album(self, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["items"]
        if len(json_result) == 0:
            print("No albums were found for this artist")
            return None

        albums = [album for album in json_result if album["album_type"] == "album"]
        if len(albums) == 0:
            print("No qualifying albums were found for this artist")
            return None
        random_album = random.choice(albums)
        return random_album

    # Gets random songs from the random album
    def get_random_songs_from_album(self, album_id, num_songs):
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit=50"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["items"]
        if len(json_result) == 0:
            print("No tracks found for this album")
            return None

        if num_songs > len(json_result):
            num_songs = len(json_result)

        random_songs = random.sample(json_result, num_songs)

        return random_songs

    # Gets the ID associated with a specific album
    def get_album_id(self, album_name):
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        query = f"?q={album_name}&type=album&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        try:
            json_result = json.loads(result.content)["albums"]["items"]
        except KeyError:
            print("Error: Failed to retrieve album information.")
            return None

        if len(json_result) == 0:
            print("No album with this name exists")
            return None

        return json_result[0]["id"]

    # Gets the url for the album cover
    def get_album_cover_url(self, album_id):
        url = f"https://api.spotify.com/v1/albums/{album_id}"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        if "images" in json_result and len(json_result["images"]) > 0:
            return json_result["images"][0]["url"]
        return None

    # Gets the Spotify profile picture for an artist
    def get_artist_image_url(self, artist_name):
        artist = self.search_for_artist(artist_name)
        if artist and "images" in artist and len(artist["images"]) > 0:
            return artist["images"][0]["url"]
        return None

    # The method that combines the previous methods
    def get_random_songs_by_artist(self, artist_name, num_songs):
        result = self.search_for_artist(artist_name)
        if result:
            artist_id = result["id"]
            random_album = self.get_random_album(artist_id)
            if random_album:
                album_id = random_album["id"]
                random_songs = self.get_random_songs_from_album(album_id, num_songs)
                if random_songs:
                    if len(random_songs) == 1:
                        return self.get_random_songs_by_artist(artist_name, num_songs)
                    album_name = random_album["name"]
                    album_cover = self.get_album_cover_url(album_id)
                    return random_songs, album_name, album_cover

        return None, None, None
