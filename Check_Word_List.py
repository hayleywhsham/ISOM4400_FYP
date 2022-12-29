import MainPageUI

def check_word_list(scraped_list):
    item_count = 0
    update_label = MainPageUI.Ui_MainWindow.lbl_info_edit_page_label
    for line in scraped_list:
        if item_count != 0:
            update_label = MainPageUI.Ui_MainWindow.lbl_info_edit_page_label + "_" + "item_count"
        update_label.settext(line)
        word_file = open("WordList", "r")
        for categories in word_file:
            if MainPageUI.Ui_MainWindow.lbl_info_edit_page_label.text.upper in categories.upper:
                MainPageUI.Ui_MainWindow.input_info_page_category = categories[0]


test_list = ["name", "name"]
check_word_list(test_list)
print(MainPageUI.Ui_MainWindow.lbl_info_edit_page_label.text)
print(MainPageUI.Ui_MainWindow.input_info_page_category)
