import json

class CategoryList:
    """
    self.categories -> dictionary {category: str : category_names: list[str]}

    """

    def __init__(self):
        # get predefined category list from Wordlist.txt
        self.categories = {}
        with open("WordList.txt", "r", encoding="utf8") as word_file:
            # dictionary: {category: str : category_names: list[str]}

            self.categories = json.loads(word_file.readline().replace("'", '"'))

    def update_defined_category(self, new_category_names: str, new_category: str):
        # Update predefined category list Wordlist.txt by user input
        new_category_names = r"%r" % new_category_names
        new_category_names = str(new_category_names.replace("\\", ""))[1:-1]

        new_category = r"%r" % new_category
        new_category = str(new_category.replace("\\", ""))[1:-1]


        if new_category != "Unrelated":
            isChanged = False

            '''
            # create a new cat. and new item (not applicable for dropdown box)
            if new_category not in self.categories:
                self.categories[new_category] = [new_category_names]
                isChanged = True
            '''

            # append new item in an existing cat.
            if new_category_names.casefold() not in [c.casefold() for c in self.categories[new_category]]:
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

            # update Wordlist.txt if any value is changed
            if isChanged:
                with open("WordList.txt", "w", encoding="utf8") as word_file:
                    new_line =str(self.categories)
                    # new_line = r"%r" % new_line
                    # new_line = new_line.replace("\\", "")
                    word_file.write(new_line)

    def check_word_list(self, scraped_list: list):
        # check for keywords (exact match) and categories
        Label_Category_dict = {"Label": [],  "Category": []}
        Keywords_Exist_dict = {"Keyword": ["T&C", "P.I.C.S.", "Opt-in/Opt-out"], "Exist?": ["Default", "Default", "Default"]}
        for item in scraped_list:
            Category_Matched = False
            Label_Category_dict["Label"].append(item)
            for defined_categories, category_texts in self.categories.items():
                for defined_text in category_texts:
                    if Category_Matched == False:
                        if item.casefold() == defined_text.casefold():
                            Label_Category_dict["Category"].append(defined_categories)
                            Category_Matched = True

            # check for keywords (not exact match) : lengthy labels may be wrongly categorized, further development
            if len(Label_Category_dict["Category"]) < len(Label_Category_dict["Label"]):
                '''
                for defined_categories, category_texts in self.categories.items():
                    for defined_text in category_texts:
                        if Category_Matched == False:
                            if defined_text.casefold() in item.casefold():
                                Label_Category_dict["Category"].append(defined_categories)
                                Category_Matched = True
                '''

                # if no match at all then empty
                if Category_Matched == False:
                    Label_Category_dict["Category"].append("")

        # Convert from category list to keyword list
        for category in Label_Category_dict["Category"]:
            if category == "T&C":
                Keywords_Exist_dict["Exist?"][0] = "Yes"
            elif category == "P.I.C.S.":
                Keywords_Exist_dict["Exist?"][1] = "Yes"
            elif category == "Opt-in/Opt-out":
                Keywords_Exist_dict["Exist?"][2] = "Yes"

        return Label_Category_dict, Keywords_Exist_dict
