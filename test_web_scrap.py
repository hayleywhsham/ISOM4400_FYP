import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.hktvmall.com/hktv/zh/%E8%B6%85%E7%B4%9A%E5%B7%BF%E5%A0%B4/%E8%B6%85%E7%B4%9A%E5%B8%82%E5%A0%B4/%E9%87%8D%E9%87%8F%E7%B4%9A%E6%8E%A8%E4%BB%8B/%E6%B0%B4%E6%9E%9C-%E8%94%AC%E8%8F%9C/main/search?q=%3Arelevance%3Astreet%3Amain%3Acategory%3AAA11030500001")
    html = driver.page_source
    driver.close()
    soup = bs4.BeautifulSoup(html,"html.parser")
    products = soup.find("div",{"class":"product-brief-list"}).find_all("div",{"class":"brand-product-name"})
    for product in products:
        print(product.find("h4").text)


if __name__ == "__main__":
    main()