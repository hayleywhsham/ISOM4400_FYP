import Check_Word_List_temp
import web_scrap
from Page_3_variables import *


url_list = [url_1, url_2, url_3, url_4]
for i in range(len(url_list)):
    scraped_text_list, scraped_link_text = web_scrap.web_scrape(i, url_list[i])
    Category_Set, Keyword_Set = Check_Word_List_temp.check_word_list(scraped_text_list)
    print(Category_Set)
    print()
    print(Keyword_Set)
