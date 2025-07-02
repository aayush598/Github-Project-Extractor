# github_search.py

import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def search_similar_repositories(query, max_results=5):
    url = f"https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": max_results}
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return [
        {"name": item["full_name"], "url": item["html_url"]}
        for item in resp.json().get("items", [])
    ]
