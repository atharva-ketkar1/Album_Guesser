from flask import Flask, render_template, request
from auth import token
from main import BackendMethods
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Creates a flask application to put the game online 
class MusicGuessingGame:
    def __init__(self):
        self.api = BackendMethods(token)
        self.artist_name = None
        self.num_songs = 3
        self.random_songs = None
        self.album_name = None
        self.album_cover = None
        self.artist_image = None
        self.guesses_left = 3
        self.incorrect_guesses = 0
        self.correct_album = None

    # The method that starts the game
    def play_game(self):
        self.artist_name = request.form.get("artist_name")

        if self.artist_name:
            self.random_songs, self.album_name, self.album_cover = self.api.get_random_songs_by_artist(self.artist_name, self.num_songs)
            self.artist_image = self.api.get_artist_image_url(self.artist_name)  # Get artist image URL
            self.guesses_left = 3
            self.incorrect_guesses = 0
            self.correct_album = None  # Reset correct album

            if self.random_songs:
                for song in self.random_songs:
                    preview_url = song.get("preview_url")
                    if preview_url:
                        song["media_player_url"] = self.get_embedded_player_url(preview_url)
                return render_template(
                    "guess.html",
                    songs=self.random_songs,
                    album_name=self.album_name,
                    artist_image=self.artist_image,
                    guesses_left=self.guesses_left
                )

            return render_template("result.html", result="No random songs found for this artist.")

        return render_template("index.html")

    # The method that takes care of the guessing scope of the game
    def process_guess(self):
        user_guess = request.form.get("user_guess")

        if self.random_songs is None:
            return render_template("result.html", result="No random songs found for this artist.")

        if fuzz.ratio(user_guess.lower(), self.album_name.lower()) >= 85:
            self.correct_album = self.album_name
            album_id = self.api.get_album_id(self.album_name)  # Get album ID
            album_cover = self.api.get_album_cover_url(album_id)  # Get album cover image URL
            return render_template("result.html", result="Congratulations! You guessed the correct album.", album_cover=album_cover, correct_album=self.correct_album)

        self.guesses_left -= 1
        self.incorrect_guesses += 1

        if self.guesses_left == 0:
            album_id = self.api.get_album_id(self.album_name)  # Get album ID
            album_cover = self.api.get_album_cover_url(album_id)  # Get album cover image URL
            return render_template("result.html", result="Sorry, you have run out of guesses. The correct album is:", correct_album=self.album_name, album_cover=album_cover)

        result = "Incorrect album name. Try again!"  # Error message
        return render_template("guess.html", songs=self.random_songs, album_name=self.album_name, artist_image=self.artist_image, guesses_left=self.guesses_left, result=result)

    # If the songs have a media preview, this method gets that 
    def get_embedded_player_url(self, preview_url):
        return preview_url.replace("/track/", "/embed/track/")

    # Gets the ID of the specific album
    def get_album_id(self, album_name):
        result = self.api.search_for_album(album_name)
        if result:
            return result["id"]
        return None

game = MusicGuessingGame()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/play", methods=["POST"])
def play_artist():
    return game.play_game()

@app.route("/guess", methods=["POST"])  
def process_guess():
    return game.process_guess()

if __name__ == "__main__":
    app.run(debug=True)
