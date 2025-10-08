import requests
import pandas as pd
import os
from dotenv import load_dotenv


def scrape(api_key: str, url: str, n_pages: int):
    movies = []
    for page in range(1, n_pages):
        print("parsing page", page)
        params = {
            'api_key': api_key,
            'language': 'en-US',
            'page': page
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for entry in data['results']:
                movie_details = requests.get(
                    f"https://api.themoviedb.org/3/movie/{entry['id']}?api_key={api_key}&page={page}&append_to_response=release_dates,credits,runtime,revenue,genres,production_countries")
                movie_details = movie_details.json()
                movies.append({
                    'title': entry.get('title'),
                    'genres': [genre['name'] for genre in movie_details.get('genres', [])],
                    'release_date': entry.get('release_date'),
                    'runtime': movie_details.get('runtime'),
                    'budget': movie_details.get('budget'),
                    'revenue': movie_details.get('revenue'),
                    'director': movie_details.get('credits', {}).get('crew', [])[0].get('name', '') if movie_details.get('credits', {}).get('crew', []) else '',
                    'popularity': movie_details.get('popularity'),
                    'vote_average': entry.get('vote_average'),
                    'vote_count': entry.get('vote_count'),
                    'overview': entry.get('overview'),
                })
        else:
            raise Exception(f"Error fetching data: {response.status_code}")
    return movies


if __name__ == '__main__':
    load_dotenv()
    movies_data = scrape(
        api_key=os.getenv('TMDB_API_KEY'),
        url='https://api.themoviedb.org/3/movie/popular',
        n_pages=300,
    )
    df = pd.DataFrame(movies_data)
    df.to_csv('tmdb_movies.csv', index=False)
