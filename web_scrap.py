import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.chrome.options import Options
url_1 = "https://www.hktvmall.com/hktv/zh/%E8%B6%85%E7%B4%9A%E5%B7%BF%E5%A0%B4/%E8%B6%85%E7%B4%9A%E5%B8%82%E5%A0%B4/%E9%87%8D%E9%87%8F%E7%B4%9A%E6%8E%A8%E4%BB%8B/%E6%B0%B4%E6%9E%9C-%E8%94%AC%E8%8F%9C/main/search?q=%3Arelevance%3Astreet%3Amain%3Acategory%3AAA11030500001"
url_2 = "https://www.adidas.com.hk/?gclid=Cj0KCQiA4aacBhCUARIsAI55maGm-unelpPysvpPAh_IOH7QZ6bkTznwgCzN8fyMNLXWeCRKfkKM8cMaAsEwEALw_wcB&gclsrc=aw.ds"
url_3 = "https://docs.google.com/forms/d/e/1FAIpQLSfBQQF14CCzq4c_mRDDNZSQMcobJBX4fOqXZ1bkeYSvs5iPnw/viewform"
url_4 = "https://forms.gle/PxHxoVDDsgvmftg98"

username = "hugofyptest@gmail.com"
password = "FYP4400test"

def main(link):
#    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    chrome_options = Options()
    chrome_options.add_extension("GoFullPageFull-Page-Screen-Capture.crx")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(link)
    html = driver.page_source
    driver.maximize_window()

#    for Google forms may require login, work-in-progress
#    username_input = driver.find_element("IdentifierID")
#    login = driver.find_element(By.ID("IdentifierNext"))
#    username_input.send_keys(username)
#    login.click()
#    password_input = driver.find_element(By.NAME("Passwd"))
#    password_input.send_keys(password)
#    login = driver.find_element(By.ID("passwordNext"))
#    login.click()

    try:
        driver.get(link)
        sleep(5)
        driver.get_screenshot_as_file("test.png")
        print("Saved as: test.png")
    except Exception as e:
        print(str(e))
        sleep(5)
        driver.get_screenshot_as_file("test.png")
        print("Saved as: "+"test.png")
#    driver.close()
    soup = bs4.BeautifulSoup(html,"html.parser")
    products = soup.find("div",{"role":"list"}).find_all("div",{"role":"listitem"})
    for product in products:
        print(product.find("span",{"class":"M7eMe"}).text)

#       read category from WordList by read text files
#          change the output from printing labels to categorising labels

#if __name__ == "__main__":
main(url_3)