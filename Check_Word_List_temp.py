#TODO
# convert temp to finalise version with updating UI directly instead of generating list of labels and categories


import pandas as pd
import web_scrap
defined_category_list = []
text_list = []
url_list = []
Label_Category_dict = {"Label": [],  "Category": []}
Keywords_Exist_dict = {"Keyword": ["T&C", "P.I.C.S", "Opt-in/Opt-out"], "Exist?": ["No", "No", "No"]}
url_1 = "https://www.hktvmall.com/hktv/zh/%E8%B6%85%E7%B4%9A%E5%B7%BF%E5%A0%B4/%E8%B6%85%E7%B4%9A%E5%B8%82%E5%A0%B4/%E9%87%8D%E9%87%8F%E7%B4%9A%E6%8E%A8%E4%BB%8B/%E6%B0%B4%E6%9E%9C-%E8%94%AC%E8%8F%9C/main/search?q=%3Arelevance%3Astreet%3Amain%3Acategory%3AAA11030500001"


# categories are personal information and keywords such as T&C, P.I.C.S and opt-in/opt-out
def import_categories():
    with open("WordList", "r", encoding="utf8") as word_file:
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
# Checking if the category already exists in the predefined list, if yes then append list, if not then add new list
    for defined_categories in defined_category_list:
        if (category.casefold() == "" and defined_categories[0] == "Unrelated") or category.casefold() == defined_categories[0].casefold():
            defined_categories.append(word)
            category_exist = True
    if not category_exist:
        defined_category_list.append([category, word])
# Write the updated wordlist into the text file
    with open("WordList", "w", encoding="utf8") as word_file:
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
    item_list = scraped_list
    item_count = 0
    categories = str(defined_category_list[0][0])
# only for visualization without UI
    for category in defined_category_list[1:]:
        categories = str(categories + ", " + category[0])
    print("Categories include: " + categories)
# check for keywords (exact match) and categories
    for item in item_list:
        Label_Category_dict["Label"].append(item)
        item_count += 1
        for defined_categories in defined_category_list:
            for defined_text in defined_categories[1:]:
                if item.casefold() == defined_text.casefold():
                    Label_Category_dict["Category"].append(defined_categories[0])
# check for keywords (not exact match)
        if len(Label_Category_dict["Category"]) < item_count:
            for defined_categories in defined_category_list:
                for defined_text in defined_categories[1:]:
                    if defined_text.casefold() in item.casefold():
                        Label_Category_dict["Category"].append(defined_categories[0])
                        break
        if len(Label_Category_dict["Category"]) < item_count:
            new_category = input(str("Category for " + item + " is:"))
            Label_Category_dict["Category"].append(new_category)
            update_defined_category(item, new_category)
# Convert from category list to keyword list
    for i in range(len(Label_Category_dict["Category"])):
        match Label_Category_dict["Category"][i]:
            case "T&C":
                Keywords_Exist_dict["Exist?"][0] = "Yes"
            case "P.I.C.S":
                Keywords_Exist_dict["Exist?"][1] = "Yes"
            case "Opt-in/Opt-out":
                Keywords_Exist_dict["Exist?"][2] = "Yes"
    i = 0
# output excludes T&C, P.I.C.S, Opt-in/Opt-out, etc. as they would be separately outputted
    while i < len(Label_Category_dict["Category"]):
        if Label_Category_dict["Category"][i] == "T&C" or Label_Category_dict["Category"][i] == "P.I.C.S" or Label_Category_dict["Category"][i] == "Opt-in/Opt-out" or Label_Category_dict["Category"][i] == "Marketing Purpose" or Label_Category_dict["Category"][i] == "Expiry Date" or Label_Category_dict["Category"][i] == "Unrelated":
            Label_Category_dict["Category"].pop(i)
            Label_Category_dict["Label"].pop(i)
            i -= 1
        i += 1
    df1 = pd.DataFrame(Label_Category_dict)
    df2 = pd.DataFrame(Keywords_Exist_dict)
    return df1, df2


test_list = ["姓名", "address", "密碼", "Password", "購物金額", "本人已閱讀並同意是次推廣活動條款及細則，有關的個人資料收集聲明及XXX有限公司 個人資料私隱的政策和實踐", "本人同意接受由XXX有限公司發出之食品及飲品的宣傳及推廣資訊", "Last Name"]
text_list, url_list = web_scrap.web_scrape(url_1)
Category_Set, Keyword_Set = check_word_list(text_list)
print(Category_Set)
print()
print(Keyword_Set)
