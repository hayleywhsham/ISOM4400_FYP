## this can only scrap links in description starting with "http"
## post['link'] will only return the first link in that post

from facebook_scraper import get_posts

def get_only_url(text):
    start = text.find('http')
    if start == -1:
        return "", -1

    #TODO
    # add "bit.ly" as valid link start
    # for loop, find min of ['bit.ly', 'http', ...] and is not -1 as starting point -> must-have
    # this list should be cumulative (non-volatile) -> good to have

    #start_pos =

    space_pos = text[start:].find(" ") + start if text[start:].find(" ") != -1 else len(text)
    next_row_pos = text[start:].find("\n") + start if text[start:].find("\n") != -1 else len(text)
    end = min(space_pos,next_row_pos)
    return text[start:end], end

def get_all_url(text):
    urls = []
    while len(text)>0:
        url, end = get_only_url(text)
        if len(url)<=0:
            break
        urls.append(url)
        text = text[end:]
        #print(text)
        #print("="*10)
    return urls


def main():
    #print(get_all_url("http:aaaaaa\n  and ahahha ahhaha http:wtf"))
    url_pool = []

    for post in get_posts('hktvmall', pages=3):

        print(post['time'])
        urls = [i for i in list(dict.fromkeys(get_all_url(post['text']))) if i not in url_pool]
        url_pool.extend(urls)
        print(urls)
        print(post['link'])
        print("==============")

if __name__ == "__main__":
    main()