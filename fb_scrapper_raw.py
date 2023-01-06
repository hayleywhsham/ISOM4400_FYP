## NOT DONE YET!
## this can only scrap links in description starting with "http" and "bit.ly"
## post['link'] will only return the first link in that post

from facebook_scraper import get_posts
import pandas as pd
import datetime
from dataclasses import dataclass

# @dataclass
# class MarkWeb:
#     brand: str
#     source: str
#     post_datetime: datetime.datetime
#     short_link: str
#     full_link: str

def get_all_url(string):
    urls = []

    target_list = ["http", "bit.ly"]
    end_target_list = ["\n", " ", "更多"]
    end_pos = 0

    while end_pos < len(string):
        pos_list = []
        string = string[end_pos:]
        for target in target_list:
            if (string.find(target) != -1):
                pos_list.append(string.find(target))

        if not (len(pos_list)):  # break if no URLs found
            return urls

        string = string[min(pos_list):]
        pos_list = []

        for target in end_target_list:
            if (string.find(target) != -1):
                pos_list.append(string.find(target))
        end_pos = min(pos_list) if len(pos_list) else len(string)
        urls.append(string[:end_pos])

    return urls

def main(fb_page_name):
    url_pool= set()

    for post in get_posts(fb_page_name, pages=3, options={"posts_per_page": 200}):
        #post_time = post['time']

        print("Post Time:",post['time'])
        urls = set(get_all_url(post['text'])) # set: unique per post
        url_pool.update(urls)
        print(urls)
        print("+++++++++++++++++++")



if __name__ == "__main__":
    main('hktvmall')