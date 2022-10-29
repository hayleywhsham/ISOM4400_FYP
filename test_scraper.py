from facebook_scraper import get_posts

def get_only_url(text):
    start = text.find('http')
    if start == -1:
        return "", -1
    space_pos = text[start:].find(" ") + start if text[start:].find(" ") != -1 else len(text)
    nextrow_pos = text[start:].find("\n") + start if text[start:].find("\n") != -1 else len(text)
    end = min(space_pos,nextrow_pos)
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

    for post in get_posts('SHISEIDOHK', pages=3):

        print(post['time'])
        urls = [i for i in list(dict.fromkeys(get_all_url(post['text']))) if i not in url_pool]
        url_pool.extend(urls)
        print(urls)
        print("==============")

if __name__ == "__main__":
    main()