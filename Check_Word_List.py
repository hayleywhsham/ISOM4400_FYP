import MainPageUI


def update_ui_labels(Label_Category_Dict):
    update_label = MainPageUI.Ui_MainWindow.lbl_info_edit_page_label
    update_category = MainPageUI.Ui_MainWindow.input_info_page_category
    for i in len(Label_Category_Dict["Label"]):
        if i != 0:
            update_label = MainPageUI.Ui_MainWindow.lbl_info_edit_page_label + "_" + i
            update_category = MainPageUI.Ui_MainWindow.input_info_page_category + "_" + i
        update_label.settext(Label_Category_Dict["Label"][i])
        update_category.text = Label_Category_Dict["Category"][i]


