from selenium import webdriver
from selenium_stealth import stealth
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import newspaper
import re


def perform_google_search(query, n_pages=10, n_results=5):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    results = []
    counter = 0
    for page in range(1, n_pages):
        url = "http://www.google.com/search?q=" + \
            str(query) + "&start=" + str((page - 1) * 10)
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            search = soup.find_all('div', class_="yuRUbf")
            for h in search:
                counter = counter + 1
                title = h.a.h3.text
                link = h.a.get('href')
                rank = counter
                results.append({'title': h.a.h3.text, 'url': link,
                                'domain': urlparse(link).netloc, 'rank': rank})
        except WebDriverException as e:
            print(f"Error loading page {page}: {e}")
            continue
    return results[:n_results]


def get_brand_mentions(text, keyword):
    # Split the text into sentences
    sentences = re.split('(?<=[.!?]) +', text)

    # Find and return sentences that contain the keyword
    keyword_sentences = [
        sentence for sentence in sentences if keyword.lower() in sentence.lower()]

    return keyword_sentences


def get_article_from_url(url):
    try:
        # Scrape the web page for content using newspaper
        article = newspaper.Article(url)
        # Download the article's content with a timeout of 10 seconds
        article.download()
        # Check if the download was successful before parsing the article
        if article.download_state == 2:
            article.parse()
            # Get the main text content of the article
            article_text = article.text
            return article_text
        else:
            print('Error: Unable to download article from URL:', url)
            return None
    except Exception as e:
        print('An error occurred while processing the URL:', url)
        print(str(e))
        return None
