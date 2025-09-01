import requests
from bs4 import BeautifulSoup

def fetch_coca_cola_logo():
    url = "https://en.wikipedia.org/wiki/Coca-Cola"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Szukamy obrazka w infoboksie
    infobox = soup.find("table", class_="infobox")
    image_url = None
    if infobox:
        img_tag = infobox.find("img")
        if img_tag:
            src = img_tag.get("src")
            if src:
                image_url = "https:" + src
                if img_tag.has_attr("srcset"):
                    srcset_urls = [u.split(" ")[0] for u in img_tag["srcset"].split(",")]
                    if srcset_urls:
                        highres_src = srcset_urls[-1]
                        if highres_src.startswith("//"):
                            image_url = "https:" + highres_src

    image_filename = None
    if image_url:
        img_resp = requests.get(image_url, headers=headers, timeout=10)
        img_resp.raise_for_status()
        image_filename = "coca_cola_logo.jpg"
        with open(image_filename, "wb") as f:
            f.write(img_resp.content)

    return image_filename