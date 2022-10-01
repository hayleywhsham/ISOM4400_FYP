import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    link = "https://www.cityline.com/Register.do"
    driver.get(link)
    html = driver.page_source
    driver.close()
    soup = bs4.BeautifulSoup(html, "html.parser")
    #print("================")
    #print("found by span")
    #items = soup.find_all("span")
    #for item in items:
    #    print(item.getText().strip())

    print("================")
    print("found by h4")
    items1 = soup.find_all("h4")
    for item1 in items1:
        print(item1.getText())


    print("================")
    print("found by aria-label")

    items2 = soup.find_all("input", attrs={"aria-label": True})
    for item2 in items2:
        if "name" in item2.attrs: #excluding intersetArea items
            if "interestArea" in item2.attrs["name"]:
                continue
        print(item2["aria-label"])


if __name__ == "__main__":
    main()