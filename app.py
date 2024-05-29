import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Function to fetch movie poster from TMDB API with retry logic
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=629367b79ed1a6cbc8fbfd6fe129fdc1&language=en-US'

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # Updated from method_whitelist to allowed_methods
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, timeout=20)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch poster: {e}")
        return None


# Function to recommend movies based on similarity
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    recommended_movies_poster = []
    for i in distances[1:11]:  # Top 10 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies_poster.append(poster_url)
        else:
            recommended_movies_poster.append(
                "https://via.placeholder.com/500x750?text=No+Image+Available")  # Placeholder image
    return recommended_movies, recommended_movies_poster


# Load movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit app interface
st.title('Movie Recommendation System')
selected_movie = st.selectbox('Select a movie:', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie)

    num_columns = 5
    num_recommendations = len(names)
    num_rows = (num_recommendations + num_columns - 1) // num_columns  # Calculate the number of rows needed

    for row in range(num_rows):
        with st.container():
            cols = st.columns(num_columns)
            for col in range(num_columns):
                index = row * num_columns + col
                if index < num_recommendations:
                    with cols[col]:
                        st.text(names[index])
                        st.image(posters[index])

