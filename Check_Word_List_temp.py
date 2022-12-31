import MainPageUI
defined_category_list = []
label_list = []
category_list = []


def import_categories():
    with open("wordlist", "r", encoding="utf8") as word_file:
        while True:
            categories = word_file.readline()
            defined_category_list.append(categories.replace(", ", ",").replace("\n", "").split(","))
            if not categories:
                break
    word_file.close()
    return defined_category_list[:-1]


def update_defined_category(word, category):
    category_exist = False
    for defined_categories in defined_category_list:
        if category.casefold() == defined_categories[0].casefold():
            defined_categories.append(word)
            category_exist = True
    if not category_exist:
        defined_category_list.append([category, word])
    print(defined_category_list)
    with open("wordlist", "w", encoding="utf8") as word_file:
        for line in defined_category_list:
            word_file.write(line[0])
            for item in line[1:]:
                word_file.write(str(", " + item))
            word_file.write("\n")
    word_file.close()


def check_word_list(scraped_list):
    import_categories()
    item_count = 0
    for item in scraped_list:
        label_list.append(item)
        item_count += 1
        for defined_categories in defined_category_list:
            for defined_text in defined_categories[1:]:
                if item.casefold() == defined_text.casefold():
                    category_list.append(defined_categories[0])
        if len(category_list) < item_count:
            new_category = input(str("Category for " + item + " is:"))
            category_list.append(new_category)
            update_defined_category(item, new_category)
    return label_list, category_list


test_list = ["姓名", "address", "住", "密碼"]
print(check_word_list(test_list))
