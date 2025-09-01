import requests
from bs4 import BeautifulSoup

def fetch_company_info():
    """Fetch company description and tagline from Coca-Cola's official site."""
    url = "https://investors.coca-colacompany.com/about"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()  # ensure we got a successful response
    soup = BeautifulSoup(resp.text, "html.parser")
    # Extract the main description (under "138 Years of Refreshment")
    # Find the section header first:
    header = soup.find(lambda tag: tag.name=="h2" and "138 Years of Refreshment" in tag.text)
    company_desc = ""
    if header:
        # Get all text elements until the next section (next h2)
        for elem in header.find_all_next():
            if elem.name == "h2":  # stop if a new section starts
                break
            # Get paragraph text and list items text
            if elem.name == "p":
                company_desc += elem.get_text(separator=" ", strip=True) + "\n"
            elif elem.name == "ul":
                # if there's a list of brands, you can skip or include it. We'll skip detailed brand list for brevity.
                continue

    # Extract the tagline (Refresh the World. Make a Difference.)
    tagline = ""
    tagline_tag = soup.find(lambda tag: tag.name=="h3" and "Refresh the World" in tag.text)
    if tagline_tag:
        tagline = tagline_tag.get_text(strip=True)

    # Clean up and return
    company_desc = company_desc.strip()
    return company_desc, tagline