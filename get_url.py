import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    link = "https://www.facebook.com/ViuTV.hk/"
    driver.get(link)
    html = driver.page_source
    driver.close()
    soup = bs4.BeautifulSoup(html, "html.parser")
    soup(text=lambda t: "http" in t.text)

    url_pool = soup.find_all("a")

    for url in url_pool:
    #    #if url and ('https' in url) and (not 'facebook' in url) and (not 'fbcdn' in url):
        print(url.get_text())

if __name__ == "__main__":
    main()

