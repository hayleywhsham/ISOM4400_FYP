def main():
    test_text = "3日內就要飲晒喇~\n Let’s Try👍🏻> http/123.com \n如果大家關於UK貨品有咩嘢想知~"
    http_pos = test_text.find("http")
    bitly_pos = test_text.find("bit.ly")
    print(http_pos)
    print(bitly_pos)
    if http_pos != -1 and bitly_pos != -1:
        start_pos = min(http_pos, bitly_pos)
    elif http_pos == -1:
        start_pos = bitly_pos
    elif bitly_pos == -1:
        start_pos = http_pos
    print(start_pos)

if __name__ == "__main__":
    main()