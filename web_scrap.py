import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

url_1 = "https://www.hktvmall.com/hktv/zh/%E8%B6%85%E7%B4%9A%E5%B7%BF%E5%A0%B4/%E8%B6%85%E7%B4%9A%E5%B8%82%E5%A0%B4/%E9%87%8D%E9%87%8F%E7%B4%9A%E6%8E%A8%E4%BB%8B/%E6%B0%B4%E6%9E%9C-%E8%94%AC%E8%8F%9C/main/search?q=%3Arelevance%3Astreet%3Amain%3Acategory%3AAA11030500001"
url_2 = "https://www.adidas.com.hk/?gclid=Cj0KCQiA4aacBhCUARIsAI55maGm-unelpPysvpPAh_IOH7QZ6bkTznwgCzN8fyMNLXWeCRKfkKM8cMaAsEwEALw_wcB&gclsrc=aw.ds"
url_3 = "https://docs.google.com/forms/d/e/1FAIpQLSfBQQF14CCzq4c_mRDDNZSQMcobJBX4fOqXZ1bkeYSvs5iPnw/viewform"
url_4 = "https://forms.gle/PxHxoVDDsgvmftg98"
url_5 = "https://vitasoy.vitavitasoy.com/sansuiluckydraw2022/index.php/tc/registration"

username = "hugofyptest@gmail.com"
password = "FYP4400test"


def main(link):
#   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    chrome_options = Options()
#    chrome_options.add_extension("GoFullPageFull-Page-Screen-Capture.crx")
    chrome_options.add_argument("start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(link)
#    driver.switch_to.window(driver.window_handles[1])
#    driver.close()
    driver.implicitly_wait(10)
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
    with open("test.png", "wb") as fh:
        fh.write(base64.urlsafe_b64decode(base_64_png['data']))
    sleep(2)

    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
    except Exception:
        print(Exception)
    return text


main(url_1)
