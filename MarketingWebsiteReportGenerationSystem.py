from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from MainPageUI import Ui_MainWindow
from fb_scraper_with_dict import get_all_url_from_string
from Check_Word_List import import_categories, update_defined_category, check_word_list, define_categories
from Page_3_variables import *
from web_scrap import *
import datetime
import csv
import tkinter
from tkinter import filedialog
import threading

from facebook_scraper import get_posts


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.stackedWidget.setCurrentWidget(self.ui.search_page)

        # default values for dates
        today_date = QDateTime.currentDateTime().date()
        self.ui.input_search_page_to_date.setDateTime(QDateTime.currentDateTime())
        self.ui.input_search_page_from_date.setDateTime(QDateTime.currentDateTime())
        self.ui.input_search_page_to_date.setMaximumDate(today_date)
        self.ui.input_search_page_from_date.setMaximumDate(today_date)

        # Connect Function: only connect once for each button
        self.ui.button_search_page_search_marketing_sites.clicked.connect(self.search_urls)
        self.ui.input_search_page_from_fb_page.returnPressed.connect(
            self.ui.button_search_page_search_marketing_sites.click)
        self.ui.button_search_page_import_csv.clicked.connect(self.search_urls_from_csv)
        self.ui.button_links_page_scrap_info.clicked.connect(self.scrape_website_page)
        self.ui.button_info_edit_page_next.clicked.connect(self.next_page)
        self.ui.button_info_edit_page_previous.clicked.connect(self.previous_page)
        self.ui.button_info_edit_page_save_all_edits.clicked.connect(self.preview_output)
        self.ui.button_report_page_back_edits.clicked.connect(self.back_to_edits)
#        self.ui.button_report_page_export_csv.clicked.connect()

        # reset Max from_date when to_date is changed
        self.ui.input_search_page_to_date.dateChanged.connect(
            lambda: self.ui.input_search_page_from_date.setMaximumDate(self.ui.input_search_page_to_date.date()))

        # update dropdown = update category list
#        self.ui.input_info_edit_page_category.currentTextChanged.connect(self.update_page)

        # change page when manually typed page number
        self.ui.input_info_edit_page_current_page.textChanged.connect(self.scrape_website_page)

    def search_urls_from_csv(self):
        tkinter.Tk().withdraw()
        csv_path = filedialog.askopenfilename(filetypes=[("Excel files", ".csv")])

        with open(csv_path, "r") as file:
            fb_names = list(csv.reader(file, delimiter=","))

        start_date = self.ui.input_search_page_from_date.date().toPyDate()
        end_date = self.ui.input_search_page_to_date.date().toPyDate()

        for fb_name in fb_names:
            print(fb_name[0])
            t = threading.Thread(target=self.init_links_page, args=(fb_name[0], start_date, end_date))
            t.start()

        self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)
    def search_urls(self):

        # PlaceHolder

        user_input: str = self.ui.input_search_page_from_fb_page.text()
        urls_dict_list = None

        if user_input != "":
            self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)
            start_date = self.ui.input_search_page_from_date.date().toPyDate()
            end_date = self.ui.input_search_page_to_date.date().toPyDate()
            t1 = threading.Thread(target=self.init_links_page, args=(user_input, start_date, end_date))
            t1.start()
        else:
            self.ui.lbl_search_page_from_fb_page_error_msg.setStyleSheet("""
            color: rgb(255, 0, 0);
            background-color: transparent;
            font: 75 10pt "Arial";
            """)
            self.ui.lbl_search_page_from_fb_page_error_msg.setText("Please input Facebook Page tag!")

    def init_links_page(self, fb_page_name: str, start_date: datetime.date, end_date: datetime.date):
        self.ui.table_links_page_link_list.verticalHeader().setVisible(True)
        self.ui.table_links_page_link_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.lbl_links_page_last_updated_datetime.setText("Loading")
        self.url_pool = set()
        fb_page_name = fb_page_name
        source = "Facebook"

        for post in get_posts(fb_page_name,
                              pages=10,

                              # Will be blocked easily by Facebook, Facebook API highly restricted
                              # Without cookie can only get 60 newest posts from page
                              # Source : https://developers.facebook.com/docs/graph-api/overview/rate-limiting/

                              # cookies="./fbUserToken.json",
                              options={
                                  "posts_per_page": 20
                              }):
            post_time = post['time']
            # print("Post Time:",type(post['time']))
            # print(f'data: start_date:{start_date},post_time: {post_time},end_date: {end_date}, \nlogic check {post_time < start_date}, {post_time <= end_date}, \npost text : {post["text"][:10]}\n')
            if(post_time.date() < start_date):
                break
            if (post_time.date() <= end_date):
                urls = set(get_all_url_from_string(post['text']))  # set: unique per post
                self.url_pool.update(urls)
                # print(urls)
                for url in urls:
                    rowPosition = self.ui.table_links_page_link_list.rowCount()
                    self.ui.table_links_page_link_list.insertRow(rowPosition)
                    self.ui.table_links_page_link_list.setItem(rowPosition, 0, QTableWidgetItem(fb_page_name))
                    self.ui.table_links_page_link_list.setItem(rowPosition, 1, QTableWidgetItem(source))
                    self.ui.table_links_page_link_list.setItem(rowPosition, 2,
                                                               QTableWidgetItem(post_time.strftime("%Y/%m/%d %H:%M")))
                    self.ui.table_links_page_link_list.setItem(rowPosition, 3, QTableWidgetItem(url))

        last_update_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        self.ui.lbl_links_page_last_updated_datetime.setText(last_update_time)

    def next_page(self):
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        max_pages = int(self.ui.lbl_info_edit_page_total_pages.text())
        if page_number < max_pages:
            self.ui.input_info_edit_page_current_page.setText(str(page_number + 1))
            self.update_page()

    def previous_page(self):
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        if page_number > 1:
            self.ui.input_info_edit_page_current_page.setText(str(page_number - 1))
            self.update_page()

    def update_page(self):
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        marketing_purpose = self.ui.input_info_edit_page_choose_marketing_purpose.currentText()
        exp_date = self.ui.input_info_edit_page_expiring_date.date()
        tnc = self.ui.input_info_edit_page_tnc.currentText()
        pics = self.ui.input_info_edit_page_pics.currentText()
        opt_in_out = self.ui.input_info_edit_page_choose_opt_in_out.currentText()
        remarks = self.ui.input_info_edit_page_remarks.toPlainText()
        self.ui.lbl_info_edit_page_full_url.setText(full_url_list[page_number - 1])
        self.ui.input_info_edit_page_choose_marketing_purpose.setCurrentIndex(0)
        self.ui.input_info_edit_page_expiring_date.date().toPyDate()
        self.ui.input_info_edit_page_tnc.setCurrentIndex(0)
        self.ui.input_info_edit_page_pics.setCurrentIndex(0)
        self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(0)
        self.ui.input_info_edit_page_remarks.clear()
        self.ui.lbl_info_edit_page_label.setText("label 1")
        self.ui.input_info_edit_page_category.setCurrentIndex(0)
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(f"Screen_Captures/ScreenShot_{page_number - 1}.png"))
        self.ui.graphicsView_info_edit_page_screenshot.setScene(scene)

    def scrape_website_page(self):
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        self.ui.stackedWidget.setCurrentWidget(self.ui.info_edit_page)
        try:
            #use url list
            url_list = list(self.url_pool)
            for url in url_list:
                if not url.startswith("http://"):
                    url = "http://" + url
            for i in range(len(url_list)):
                scraped_text_list, scraped_link_list, full_url = web_scrape(i, url_list[i])
                Label_Category_dict, Keywords_Exist_dict = check_word_list(scraped_text_list)
                all_Label_Category_dict.append(Label_Category_dict)
                all_Keywords_Exist_dict.append(Keywords_Exist_dict)
                full_url_list.append(full_url)
            self.ui.lbl_info_edit_page_full_url.setText(full_url_list[0])
            self.ui.lbl_info_edit_page_total_pages.setText(str(len(url_list)))
            Label_Category_dict = all_Label_Category_dict[0]
            print(full_url_list)
            for items_no in range(len(Label_Category_dict)):
                try:
                    # set labels and categories dynamically
                    if items_no == 0:
                        self.ui.input_info_edit_page_category.addItems(define_categories())
                        self.ui.lbl_info_edit_page_label.setText(Label_Category_dict["Label"][0])
                        if Label_Category_dict["Category"][0] == "":
                            self.ui.input_info_edit_page_category.setCurrentText("Choose Category")
                        else:
                            self.ui.input_info_edit_page_category.setCurrentText(all_Label_Category_dict[0]["Category"][0])
                    else:
                        #self.input_info_edit_page_category_3 = QtWidgets.QComboBox(self.formLayoutWidget)
                        setattr(f'self.ui.input_info_edit_page_category_{items_no}', "addItems", (define_categories()))
                        setattr(f'self.ui.lbl_info_edit_page_label_{items_no+1}', "setText", (self, Label_Category_dict["Label"][items_no]))
                        if Label_Category_dict["Category"][items_no] == "":
                            setattr(f'self.ui.input_info_edit_page_category_{items_no+1}', "setCurrentText", (self, "Choose Category"))
                        else:
                            setattr(f'self.ui.input_info_edit_page_category_{items_no+1}', "setCurrentText", (self, Label_Category_dict["Category"][items_no]))
                except Exception as e:
                    print(str(e))
                    continue
            if Keywords_Exist_dict["Exist?"][0] == "Yes":
                self.ui.input_info_edit_page_tnc.setCurrentIndex(1)
            else:
                self.ui.input_info_edit_page_tnc.setCurrentIndex(2)
            if Keywords_Exist_dict["Exist?"][1] == "Yes":
                self.ui.input_info_edit_page_pics.setCurrentIndex(1)
            else:
                self.ui.input_info_edit_page_pics.setCurrentIndex(2)
            if Keywords_Exist_dict["Exist?"][2] == "Yes":
                self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(1)
            else:
                self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(2)
            self.ui.lbl_info_page_error_msg.setVisible(False)
        except Exception as e:
            self.ui.lbl_info_page_error_msg.setText(str(e))
            self.ui.lbl_info_page_error_msg.setVisible(True)
            pass
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(f"Screen_Captures/ScreenShot_{page_number - 1}.png"))
        self.ui.graphicsView_info_edit_page_screenshot.setScene(scene)

    def update_category(self):
        update_defined_category(self.ui.lbl_info_edit_page_label, self.ui.input_info_edit_page_category)
    def preview_output(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.report_page)

    def back_to_edits(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.info_edit_page)

    def export_to_csv(self):
        pass
        # save scraped results from local variable to csv format



def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
