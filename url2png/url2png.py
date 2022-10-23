from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import argparse
import os

def get_subdomains_in_txt(textfile):
    with open (textfile) as f:
        subdomain_list=f.read().splitlines()
        for x in subdomain_list:
            url_pool.append('https://'+ x)


def get_urls_in_html(html_link):

    # Opening the html file
    HTMLFile = open("https://" + html_link, "r", encoding="utf8")
    
    # Reading the file
    html = HTMLFile.read()

    #print ("GET URLS IN HTML, ", url, html, baseurl, encoding)
    #soup = BeautifulSoup(html, 'html.parser', from_encoding=encoding)
    soup = BeautifulSoup(html, "html.parser")
    #soup = BeautifulSoup(html.decode(encoding,'ignore'), features="html.parser")
            
    for link in soup.find_all():
    #for link in soup.find_all('a'):
        path = link.get('href')
        if path and path.startswith('https') and (not 'facebook' in path) and (not 'fbcdn' in path):
            url_pool.append(path)

url_pool = [
]

parser = argparse.ArgumentParser(description='Filename:')
parser.add_argument("-u", "--htmlurl", help="URL")
parser.add_argument("-f", "--file", help="file")

args = parser.parse_args()
html_link = args.htmlurl
textfile = args.file

get_subdomains_in_txt(textfile)

#get_urls_in_html(html_link)
print (url_pool)
print (len(url_pool))

driver = webdriver.Chrome(executable_path=os.getcwd()+'/chromedriver.exe')
index=1425
driver.maximize_window()

for url in url_pool:
    print("Current url: "+url)
    try:
        driver.get(url)
        sleep(5)
        driver.get_screenshot_as_file(str(index)+".png")
        print("Saved as: "+str(index)+".png")
    except Exception as e:
        print(str(e))
        sleep(5)
        driver.get_screenshot_as_file(str(index)+".png")
        print("Saved as: "+str(index)+".png")
    index+=1
    
driver.quit()
