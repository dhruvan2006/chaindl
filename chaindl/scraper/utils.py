import requests


def _get_page_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def _join_url(base_url, path):
    return base_url.rstrip("/") + "/" + path.lstrip("/")
