import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def create_folder(folder_name, base_path=None):
    if base_path is None:
        base_path = os.getcwd()  
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True) 
    return folder_path

def valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_all_links(url, visited):
    if url in visited:
        return []
    print(f"Visiting: {url}")
    visited.add(url)
    try:
        response = requests.get(url)
        response.raise_for_status()  
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)
        if valid_url(full_url):
            links.append(full_url)

    return links

def download_pdf_from_url(url, download_folder):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        pdf_filename = os.path.join(download_folder, os.path.basename(urlparse(url).path))
        with open(pdf_filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {pdf_filename}")
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")

def scrape_pdfs(start_url, folder_path):
    visited = set()
    queue = [start_url]

    while queue:
        current_url = queue.pop(0)
        for link in get_all_links(current_url, visited):
            if link.endswith('.pdf'):
                download_pdf_from_url(link, folder_path)
            elif link not in visited:
                queue.append(link)


url = 'https://lawcommission.gov.np/np/'
folder_name = 'documents'
base_path = os.path.dirname(os.path.realpath(__file__))
download_folder = create_folder(folder_name, base_path)
scrape_pdfs(url, download_folder)
