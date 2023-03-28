import pandas as pd
from Page_3_variables import *
import json


class CategoryList:
    """
    self.categories -> dictionary {category: str : category_names: list[str]}

    """

    def __init__(self):
        self.categories = {}
        with open("WordList.txt", "r", encoding="utf8") as word_file:
            # dictionary: {category: str : category_names: list[str]}

            self.categories = json.loads(word_file.readline().replace("'", '"'))

    def update_defined_category(self, new_category_names: str, new_category: str):
        isChanged = False

        # create a new cat. and new item
        if new_category not in self.categories:
            self.categories[new_category] = [new_category_names]
            isChanged = True

        # append new item in an existing cat.
        elif new_category_names.casefold() not in [c.casefold() for c in self.categories[new_category]]:
            self.categories[new_category].append(new_category_names)
            isChanged = True

        # remove existing word in the other cat.
        for category, category_names in self.categories.items():
            if category != new_category:
                try:
                    category_names.remove(new_category_names)
                    self.categories[category] = category_names
                    isChanged = True
                except ValueError:
                    pass

        # update Wordlist.txt
        if isChanged:
            with open("WordList.txt", "w", encoding="utf8") as word_file:
                word_file.write(str(self.categories))

    # categories are personal information and keywords such as T&C, P.I.C.S and opt-in/opt-out
    # def import_categories():
    #     with open("Wordlist.txt", "r", encoding="utf8") as word_file:
    #         while True:
    #             categories = word_file.readline()
    #             defined_category_list.append(categories.replace(", ", ",").replace("\n", "").split(","))
    #             if not categories:
    #                 break
    #     word_file.close()
    #     defined_category_list.pop()
    #     return defined_category_list
    #
    #
    # def define_categories():
    #     return [c[0] for c in import_categories()]
    #
    #
    # def update_defined_category(word, category):
    #     category_exist = False
    #
    #     # check if word already exists in other categories and remove it
    #     for defined_categories in defined_category_list:
    #         defined_categories.remove(word)
    #
    #     # Checking if the category already exists in the predefined list, if yes then append list, if not then add new list
    #     for defined_categories in defined_category_list:
    #         if (category.casefold() == "" and defined_categories[0] == "Unrelated") or category.casefold() == \
    #                 defined_categories[0].casefold():
    #             defined_categories.append(word)
    #             category_exist = True
    #             break
    #
    #     if not category_exist:
    #         defined_category_list.append([category, word])
    #     # Write the updated wordlist into the text file
    #     with open("Wordlist.txt", "w", encoding="utf8") as word_file:
    #         for line in defined_category_list[:-1]:
    #             word_file.write(line[0])
    #             for item in line[1:]:
    #                 word_file.write(str(", " + item))
    #             word_file.write("\n")
    #         word_file.write(defined_category_list[-1][0])
    #         for item in defined_category_list[-1][1:]:
    #             word_file.write(str(", " + item))
    #     word_file.close()
    #     return defined_category_list

    def check_word_list(self, scraped_list: list):
        # check for keywords (exact match) and categories
        Label_Category_dict = {"Label": [],  "Category": []}
        Keywords_Exist_dict = {"Keyword": ["T&C", "P.I.C.S", "Opt-in/Opt-out"], "Exist?": ["No", "No", "No"]}
        Category_Matched = False
        for item in scraped_list:
            Category_Matched = False
            Label_Category_dict["Label"].append(item)
            for defined_categories, category_texts in self.categories.items():
                for defined_text in category_texts:
                    if Category_Matched == False:
                        if item.casefold() == defined_text.casefold():
                            Label_Category_dict["Category"].append(defined_categories)
                            Category_Matched = True

# check for keywords (not exact match) : lengthy labels may be wrongly categorized, need consider
            #print(len(Label_Category_dict["Category"]), len(Label_Category_dict["Label"]))
            if len(Label_Category_dict["Category"]) < len(Label_Category_dict["Label"]):
                #for defined_categories, category_texts in self.categories.items():
                    #for defined_text in category_texts:
                        #if Category_Matched == False:
                            #if defined_text.casefold() in item.casefold():
                                #Label_Category_dict["Category"].append(defined_categories)
                                #Category_Matched = True

# if no match at all then empty
                if Category_Matched == False:
                    Label_Category_dict["Category"].append("")
# Convert from category list to keyword list
        for category in Label_Category_dict["Category"]:
            if category == "T&C":
                Keywords_Exist_dict["Exist?"][0] = "Yes"
            elif category == "P.I.C.S":
                Keywords_Exist_dict["Exist?"][1] = "Yes"
            elif category == "Opt-in/Opt-out":
                Keywords_Exist_dict["Exist?"][2] = "Yes"

        return Label_Category_dict, Keywords_Exist_dict
