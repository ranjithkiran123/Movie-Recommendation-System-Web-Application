import flask
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

app = flask.Flask(__name__, template_folder='templates')

# Create a TF-IDF vectorizer
tfidf = TfidfVectorizer(stop_words='english', analyzer='word')

# Define the TMDB API key
api_key = "c5feda7f1a63d647ffc2aea849372e1e"

def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        return movie_data
    else:
        return None

def get_recommendations(title):
    # Search for movies based on the given title
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    search_response = requests.get(search_url)
    if search_response.status_code == 200:
        search_results = search_response.json()
        if search_results["results"]:
            movie_id = search_results["results"][0]["id"]  # Retrieve the ID of the first search result
            movie_data = get_movie_details(movie_id)
            if movie_data:
                movie_overview = movie_data["overview"]
                movie_genres = get_genre_names(movie_data.get("genre_ids", []))
                movie_cast = get_movie_cast(movie_id)
                similar_movie_ids = get_similar_movies(movie_id)
                similar_movies = [get_movie_details(movie_id) for movie_id in similar_movie_ids]
                if similar_movies:
                    return {
                        "title": movie_data["title"],
                        "overview": movie_overview,
                        "genres": movie_genres,
                        "cast": movie_cast,
                        "similar_movies": similar_movies
                    }
                else:
                    return {
                        "title": movie_data["title"],
                        "overview": movie_overview,
                        "genres": movie_genres,
                        "cast": movie_cast
                    }
    
    return None


def get_genre_names(genre_ids):
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        genre_data = response.json()
        genres = genre_data["genres"]
        return [genre["name"] for genre in genres if genre["id"] in genre_ids]
    return []

def get_movie_cast(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        cast_data = response.json()
        cast = cast_data["cast"][:5]  # Retrieve the first 5 cast members
        return [actor["name"] for actor in cast]
    return []

def get_similar_movies(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        similar_data = response.json()
        similar_movies = similar_data.get("results", [])[:5]  # Retrieve the first 5 similar movies
        if not similar_movies:
            # If no similar movies are found, get a fallback set of similar movies
            fallback_url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}"
            fallback_response = requests.get(fallback_url)
            if fallback_response.status_code == 200:
                fallback_data = fallback_response.json()
                fallback_movies = fallback_data.get("results", [])[:5]  # Retrieve the first 5 popular movies
                return [movie["id"] for movie in fallback_movies]
        return [movie["id"] for movie in similar_movies]
    return []


@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return flask.render_template('index1.html')

    if flask.request.method == 'POST':
        m_name = " ".join(flask.request.form['movie_name'].title().split())
        movie_recommendations = get_recommendations(m_name)
        if movie_recommendations is None:
            return flask.render_template('index1.html', error_message="No recommendations found for the given movie.")
        else:
            return flask.render_template('index1.html', movie_recommendations=movie_recommendations)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
