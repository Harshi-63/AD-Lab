import requests
from bs4 import BeautifulSoup


def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error if request fails

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")

        text = "\n".join([p.get_text() for p in paragraphs])
        return text[:5000]  # Limit text size for processing
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
