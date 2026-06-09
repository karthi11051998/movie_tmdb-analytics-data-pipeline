import os
import json
from datetime import datetime

import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")

# TMDB endpoint
url = "https://api.themoviedb.org/3/movie/popular"

# Store all movie records
all_movies = []

session = requests.Session()

retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)

# Collect 25 pages (~500 movies)
for page in range(1, 26):

    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": page
    }

    try:
        response = session.get(
        url,
        params=params,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
        )
        response.raise_for_status()

        movies = response.json()["results"]

        all_movies.extend(movies)

        time.sleep(1)

        print(f"Collected page {page} - {len(movies)} records")

    except Exception as e:
        print(f"Failed on page {page}")
        print(e)
        break

print(f"\nTotal movies collected: {len(all_movies)}")

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d")

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save JSON
json_file = f"data/movies_{timestamp}.json"

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(all_movies, f, indent=4)

print(f"JSON saved: {json_file}")

# Transform into tabular format
movie_data = []

for movie in all_movies:

    movie_data.append({
        "movie_id": movie.get("id"),
        "title": movie.get("title"),
        "release_date": movie.get("release_date"),
        "popularity": movie.get("popularity"),
        "vote_average": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "adult": movie.get("adult"),
        "language": movie.get("original_language")
    })

# Create DataFrame
df = pd.DataFrame(movie_data)

print(f"Rows in DataFrame: {len(df)}")

# Save CSV
csv_file = f"data/movies_{timestamp}.csv"

df.to_csv(csv_file, index=False)

print(f"CSV saved: {csv_file}")

# Upload to S3
bucket_name = "movie-tmdb-data-lake"

s3 = boto3.client("s3")

s3.upload_file(
    csv_file,
    bucket_name,
    f"raw/movies/{os.path.basename(csv_file)}"
)

print("CSV uploaded to S3 successfully")