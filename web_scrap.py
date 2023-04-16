import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests


def get_full_url(link):
    #   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    chrome_options = Options()
    #    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(10)
    try:
        driver.get(link)
        full_url = driver.current_url
    except TimeoutException:
        full_url = link
    return full_url

def get_full_url_2(link):
    session = requests.session()
    resp = session.head(link, allow_redirects=True)
    full_url = resp.url
    return full_url


def web_scrape(counter, link):
#   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    chrome_options = Options()
#    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(30)
    driver.get(link)
    page_rect = driver.execute_cdp_cmd('Page.getLayoutMetrics', {})
    screenshot_config = {'captureBeyondViewport': True,
                         'fromSurface': True,
                         'clip': {'width': page_rect['contentSize']['width'],
                                  'height': page_rect['contentSize']['height'],
                                  'x': 0,
                                  'y': 0,
                                  'scale': 1},
                         }
    base_64_png = driver.execute_cdp_cmd('Page.captureScreenshot', screenshot_config)
    ScreenShot_path = str("Screen_Captures/ScreenShot_" + str(counter))
    with open(f"{ScreenShot_path}.png", "wb") as fh:
        fh.write(base64.urlsafe_b64decode(base_64_png['data']))
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        text = text.replace("'", "")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text_list = text.split("\n")
        for index, text in enumerate(text_list):
            text = r"%r" % text
            text_list[index] = str(text.replace("\\", ""))[1:-1]
    except Exception as e:
        print(str(e))
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        link_list = []
        for links in soup.find_all("a"):
            link_list.append(links.get("href"))
    except Exception as e:
        print(str(e))
        pass
    return text_list, link_list
