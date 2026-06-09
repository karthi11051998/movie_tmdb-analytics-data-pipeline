import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import json
import boto3

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

url = "https://api.themoviedb.org/3/movie/popular"

all_movies = []

for page in range(1, 26):
    params = {
    "api_key": API_KEY,
    "language": "en-US",
    "page": 1
    }

response = requests.get(url, params=params)

response.raise_for_status()

movies = all_movies

all_movies.extend(movies)

print(f"Collected page {page}")

timestamp = datetime.now().strftime("%Y%m%d")

json_file = f"data/movies_{timestamp}.json"

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=4)

movie_data = []

for movie in movies:
    movie_data.append({
        "movie_id": movie["id"],
        "title": movie["title"],
        "release_date": movie["release_date"],
        "popularity": movie["popularity"],
        "vote_average": movie["vote_average"],
        "vote_count": movie["vote_count"],
        "adult": movie["adult"],
        "language": movie["original_language"]
    })

df = pd.DataFrame(movie_data)

csv_file = f"data/movies_{timestamp}.csv"

df.to_csv(csv_file, index=False)

bucket_name = "movie-tmdb-data-lake"

s3 = boto3.client("s3")

s3.upload_file(
    csv_file,
    bucket_name,
    f"raw/movies/{csv_file.split('/')[-1]}"
)

print("File uploaded to S3 successfully")