import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

NAMESPACES = {
    'tmdb': 'https://themoviedb.org',
    'letterboxd': 'https://letterboxd.com'
}
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def fetch_rss_feed(url):
    response = requests.get(url)
    response.raise_for_status()
    return ET.fromstring(response.text)

        

def parse_movie_data(item):
    title = item.find('letterboxd:filmTitle', NAMESPACES).text
    description = BeautifulSoup(item.find('description').text, 'html.parser').find_all('p')[1].get_text()
    return {
        'title': title,
        'logDate': item.find('letterboxd:watchedDate', NAMESPACES).text,
        'memberRating': item.find('letterboxd:memberRating', NAMESPACES).text,
        'tmdb_id': item.find('tmdb:movieId', NAMESPACES).text,
        'description': description
    }

def fetch_tmdb_movie_data(tmdb_id):
    tmdb_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}'
    tmdb_movie_response = requests.get(tmdb_url).json()
    return {
        'id': tmdb_id,
        'original_title': tmdb_movie_response['original_title'],
        'runtime': tmdb_movie_response['runtime'],
        'genres': [v['name'] for v in tmdb_movie_response['genres']],
        'release_date': tmdb_movie_response['release_date'],
        'original_language': tmdb_movie_response['original_language'],
        'poster_url': f"https://image.tmdb.org/t/p/w1280{tmdb_movie_response['poster_path']}"
    }

def get_movie_data_from_rss_feed(url, year=None):
    root = fetch_rss_feed(url)
    letterboxd_data = [parse_movie_data(item) for item in root.findall('.//item')]
    
    letterboxd_df = pd.DataFrame(letterboxd_data)
    letterboxd_df['logDate'] = pd.to_datetime(letterboxd_df['logDate'], format='ISO8601', utc=True)
    letterboxd_df['memberRating'] = letterboxd_df['memberRating'].astype(float)
    
    if year:
        letterboxd_df = letterboxd_df[letterboxd_df['logDate'].dt.year == year]
    
    tmdb_ids = letterboxd_df['tmdb_id'].unique()
    
    tmdb_data = []
    for tmdb_id in tmdb_ids:
        tmdb_data.append(fetch_tmdb_movie_data(tmdb_id))
    
    tmdb_df = pd.DataFrame(tmdb_data)
    tmdb_df['release_date'] = pd.to_datetime(tmdb_df['release_date'], format='ISO8601', utc=True)

    merged_df = letterboxd_df.merge(tmdb_df, left_on='tmdb_id', right_on='id')
    
    return merged_df

# Usage
# url = 'https://letterboxd.com/username/rss/'
# letterboxd_df, tmdb_df = get_movie_data_from_rss_feed(url, year=2023)