import requests

response = requests.get("https://api.themoviedb.org")

print(response.status_code)