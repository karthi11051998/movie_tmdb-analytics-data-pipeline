import io
import os
from datetime import datetime

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_RAW_PREFIX")
TOTAL_PAGES = int(os.getenv("TMDB_PAGES", 25))
LANGUAGE = os.getenv("TMDB_LANGUAGE", "en-US")

if not API_KEY:
    raise ValueError("TMDB_API_KEY not configured")

if not BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME not configured")

if not S3_PREFIX:
    raise ValueError("S3_RAW_PREFIX not configured")

session = requests.Session()

retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)

url = "https://api.themoviedb.org/3/movie/popular"

all_movies = []

for page in range(1, TOTAL_PAGES + 1):

    response = session.get(
        url,
        params={
            "api_key": API_KEY,
            "language": LANGUAGE,
            "page": page
        },
        timeout=30
    )

    response.raise_for_status()

    all_movies.extend(
        response.json()["results"]
    )

movie_data = [
    {
        "movie_id": movie.get("id"),
        "title": movie.get("title"),
        "release_date": movie.get("release_date"),
        "popularity": movie.get("popularity"),
        "vote_average": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "adult": movie.get("adult"),
        "language": movie.get("original_language")
    }
    for movie in all_movies
]

df = pd.DataFrame(movie_data)

csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)

timestamp = datetime.utcnow().strftime("%Y%m%d")

s3_key = f"{S3_PREFIX}/movies_{timestamp}.csv"

boto3.client("s3").put_object(
    Bucket=BUCKET_NAME,
    Key=s3_key,
    Body=csv_buffer.getvalue()
)