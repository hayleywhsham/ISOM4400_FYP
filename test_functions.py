t = ["a","a","b","a","a","c","c","d"]
#["a","b","c","d"]

def unique(urls):
    return list(dict.fromkeys(urls))

print(unique(t))