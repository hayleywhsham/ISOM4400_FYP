import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    link = "https://www.facebook.com/ViuTV.hk/"
    driver.get(link)
    html = driver.page_source
    time.sleep(2)
    driver.close()
    soup = bs4.BeautifulSoup(html, "html.parser")
    urls = soup.find_all("a")
    url_pool = []

    def is_http(text):
        return "http" in text

    def get_only_url(text):
        start = text.find('http')
        end = min(text[start:].find(" "), text[start:].find("\n"))
        if end == -1:
            end = len(text)
        return text[start:end]

    def is_unique(text):
        return not (text in url_pool)

    for url in urls:
        if url.has_attr('href') and "http" in url.get_text():
            lines = list(filter(is_http, url.get_text().split("\n")))
            all_urls = list(map(get_only_url, lines))
            unique_urls = list(filter(is_unique, all_urls))
            url_pool.extend(unique_urls)
    print(url_pool)

if __name__ == "__main__":
    main()

