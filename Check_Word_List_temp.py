import pandas as pd
defined_category_list = []
Label_Category_dict = {"Label": [],  "Category":[]}
Labels_Exists_dict = {""}


def import_categories():
    with open("PII_WordList", "r", encoding="utf8") as word_file:
        while True:
            categories = word_file.readline()
            defined_category_list.append(categories.replace(", ", ",").replace("\n", "").split(","))
            if not categories:
                break
    word_file.close()
    defined_category_list.pop()
    return defined_category_list


def update_defined_category(word, category):
    category_exist = False
    for defined_categories in defined_category_list:
        if category.casefold() == defined_categories[0].casefold():
            defined_categories.append(word)
            category_exist = True
    if not category_exist:
        defined_category_list.append([category, word])
    print(defined_category_list)
    with open("PII_WordList", "w", encoding="utf8") as word_file:
        for line in defined_category_list[:-1]:
            word_file.write(line[0])
            for item in line[1:]:
                word_file.write(str(", " + item))
            word_file.write("\n")
        word_file.write(defined_category_list[-1][0])
        for item in defined_category_list[-1][1:]:
            word_file.write(str(", " + item))
    word_file.close()
    return defined_category_list


def check_word_list(scraped_list):
    import_categories()
    item_count = 0
    for item in scraped_list:
        Label_Category_dict["Label"].append(item)
        item_count += 1
        for defined_categories in defined_category_list:
            for defined_text in defined_categories[1:]:
                if item.casefold() == defined_text.casefold():
                    Label_Category_dict["Category"].append(defined_categories[0])
        if len(Label_Category_dict["Category"]) < item_count:
            new_category = input(str("Category for " + item + " is:"))
            Label_Category_dict["Category"].append(new_category)
            update_defined_category(item, new_category)
    return Label_Category_dict


test_list = ["姓名", "address", "住", "密碼"]
df = pd.DataFrame(check_word_list(test_list))
print(df)
