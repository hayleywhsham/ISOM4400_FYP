## this can only scrap links in description starting with "http" and "bit.ly"
## post['link'] will only return the first link in that post
import datetime

from facebook_scraper import get_posts


def get_all_url_from_string(string) -> list[str]:
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




