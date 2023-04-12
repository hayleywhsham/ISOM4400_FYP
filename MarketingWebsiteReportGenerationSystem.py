from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
from MainPageUI import Ui_MainWindow
from fb_scraper_with_dict import get_all_url_from_string
from Check_Word_List import CategoryList
from web_scrap import *
import datetime
import csv
import tkinter
from tkinter import filedialog
import threading
from edit_information_pages import EditInformationPage

from facebook_scraper import get_posts
from facebook_scraper.exceptions import NotFound,TemporarilyBanned


def clear_screenshots():
    for screenshot in os.listdir("Screen_Captures"):
        os.remove("Screen_Captures/" + screenshot)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.categoryList = CategoryList()
        self.columnWidgets = []
        self.url_pool = set()
        self.edit_information_pages = []

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
        self.ui.button_links_page_back.clicked.connect(self.back_to_search_page)
        self.ui.button_links_page_scrap_info.clicked.connect(self.initial_edit_page)
        self.ui.button_info_edit_page_back.clicked.connect(self.back_to_links_page)
        self.ui.button_info_edit_page_next.clicked.connect(self.next_page)
        self.ui.button_info_edit_page_previous.clicked.connect(self.previous_page)
        self.ui.button_info_edit_page_save_all_edits.clicked.connect(self.preview_output)
        self.ui.button_report_page_back_edits.clicked.connect(self.back_to_edits)
        self.ui.button_report_page_export_csv.clicked.connect(self.export_to_csv)
        self.ui.button_report_page_export_csv.clicked.connect(self.reset_app)

        # reset Max from_date when to_date is changed
        self.ui.input_search_page_to_date.dateChanged.connect(
            lambda: self.ui.input_search_page_from_date.setMaximumDate(self.ui.input_search_page_to_date.date()))

        self.lock = threading.Lock()

        # change page when page number changed, currently debugging due to page number change
        #self.ui.input_info_edit_page_current_page.textEdited.connect(self.update_page)

    def back_to_search_page(self):
        while self.ui.table_links_page_link_list.rowCount() > 0:
            self.ui.table_links_page_link_list.removeRow(0)
        self.ui.stackedWidget.setCurrentWidget(self.ui.search_page)
        self.edit_information_pages.clear()

    def back_to_links_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)
    def search_urls_from_csv(self):
        tkinter.Tk().withdraw()
        csv_path = filedialog.askopenfilename(filetypes=[("Excel files", ".csv")])

        with open(csv_path, "r") as file:
            fb_names = list(csv.reader(file, delimiter=","))

        start_date = self.ui.input_search_page_from_date.date().toPyDate()
        end_date = self.ui.input_search_page_to_date.date().toPyDate()

        for fb_name in fb_names:
            t = threading.Thread(target=self.init_links_page, args=(fb_name[0], start_date, end_date))
            t.start()

        self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)

    def search_urls(self):

        # PlaceHolder

        self.user_input: str = self.ui.input_search_page_from_fb_page.text()
        urls_dict_list = None

        if self.user_input != "":
            self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)
            start_date = self.ui.input_search_page_from_date.date().toPyDate()
            end_date = self.ui.input_search_page_to_date.date().toPyDate()
            t1 = threading.Thread(target=self.init_links_page, args=(self.user_input, start_date, end_date))
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
        self.ui.table_links_page_link_list.horizontalHeader().setVisible(True)
        self.ui.table_links_page_link_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.lbl_links_page_last_updated_datetime.setText("Loading")
        fb_page_name = fb_page_name
        source = "Facebook"
        post_count = 0
        try:
            for post in get_posts(fb_page_name,
                                  pages=99999,

                              # Will be blocked easily by Facebook, Facebook API highly restricted
                              # Without cookie can only get 60 newest posts from page
                              # Source : https://developers.facebook.com/docs/graph-api/overview/rate-limiting/

                               cookies="./fbUserToken.json",):

                post_time = post['time']
                # print("Hi")
                # print("Post Time:",type(post['time'])) print(f'data: start_date:{start_date},post_time: {post_time},
                # end_date: {end_date}, \nlogic check {post_time < start_date}, {post_time <= end_date}, \npost text : {
                # post["text"][:10]}\n')
                if post_time.date() < start_date:
                    break
                if post_time.date() <= end_date:
                    urls = set(get_all_url_from_string(post['text']))  # set: unique per post
                    for url in urls:
                        if not (url.startswith("http://") or url.startswith("https://")):
                            new_url = "http://" + url
                            self.edit_information_pages.append(EditInformationPage(fb_page_name,
                                                                                   source,
                                                                                   post_time.strftime("%Y/%m/%d"),
                                                                                   new_url))
                    post_count += 1
        except NotFound:

            self.lock.acquire()
            error_msg = self.ui.lbl_links_page_error_msg.text()

            if error_msg == "":
                error_msg = f'{fb_page_name} doesn\'t not exist! Please check again!'
            else:
                error_msg = f'{fb_page_name}, {error_msg}'

            self.ui.lbl_links_page_error_msg.setText(error_msg)
            self.lock.release()

        except TemporarilyBanned:
            msg = "You being Temporarily Banned by facebook!"

            self.ui.lbl_links_page_error_msg_ban.setText(msg)

            msg_heading = "\nThe following page have not been searched: "

            self.lock.acquire()
            error_msg = self.ui.lbl_links_page_error_msg.text()

            if (msg_heading not in error_msg):
                error_msg = error_msg + msg_heading + fb_page_name
            else:
                error_msg = f'{error_msg},{fb_page_name}'

            self.ui.lbl_links_page_error_msg.setText(error_msg)
            self.lock.release()

        self.remove_dup_links()
        for pages in self.edit_information_pages:
            row_position = self.ui.table_links_page_link_list.rowCount()
            self.ui.table_links_page_link_list.insertRow(row_position)
            self.ui.table_links_page_link_list.setItem(row_position, 0, QTableWidgetItem(pages.fb_page_name))
            self.ui.table_links_page_link_list.setItem(row_position, 1, QTableWidgetItem(pages.source))
            self.ui.table_links_page_link_list.setItem(row_position, 2, QTableWidgetItem(pages.post_time))
            self.ui.table_links_page_link_list.setItem(row_position, 3, QTableWidgetItem(pages.url))
            self.ui.table_links_page_link_list.setItem(row_position, 4, QTableWidgetItem(pages.full_url))

        last_update_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        self.ui.lbl_links_page_last_updated_datetime.setText(last_update_time)
        print(f'Scrapped {post_count} post(s). Got {len(self.edit_information_pages)} link(s).')

    def remove_dup_links(self):
        full_url_list = []
        index = 0
        if len(self.edit_information_pages) > 0:
            while index < len(self.edit_information_pages):
                if self.edit_information_pages[index].full_url not in full_url_list:
                    full_url_list.append(self.edit_information_pages[index].full_url)
                    index += 1
                else:
                    del self.edit_information_pages[index]


    def next_page(self):
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        max_pages = int(self.ui.lbl_info_edit_page_total_pages.text())
        # Get current page information (i.e. selected dropdown items)
        try:
            self.get_combobox_data()
        except Exception as e:
            print(str(e))
            pass
        if page_number < max_pages:
            self.ui.input_info_edit_page_current_page.setText(str(page_number + 1))
            self.update_page()

    def previous_page(self):
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        # Get current page information (i.e. selected dropdown items)
        try:
            self.get_combobox_data()
        except Exception as e:
            print(str(e))
            pass
        if page_number > 1:
            self.ui.input_info_edit_page_current_page.setText(str(page_number - 1))
            self.ui.input_info_edit_page_remarks.setText(self.edit_information_pages[page_number - 2].remarks)
            self.update_page()

    def update_page(self):
        # Clear old label-categories pairs
        while self.ui.formLayout_info_edit_page_scrolling_content.rowCount() > 0:
            self.ui.formLayout_info_edit_page_scrolling_content.removeRow(0)
        self.columnWidgets.clear()

        # generate new list of label-categories
        self.generate_category_page()


    def initial_edit_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.info_edit_page)
        # use url from last step for scraping
        self.ui.lbl_info_edit_page_total_pages.setText(str(len(self.edit_information_pages)))
        first_page_thread = None
        for page_index, page in enumerate(self.edit_information_pages):
            t = threading.Thread(target=self.scrape_website_page, args=(page_index, page))
            t.start()
            if first_page_thread == None:
                first_page_thread = t
        first_page_thread.join()
        try:
            # put to new function and call for update and initialize
            self.update_page()
            self.ui.lbl_info_page_error_msg.setVisible(False)
        except Exception as e:
            self.ui.lbl_info_page_error_msg.setText(str(e))
            self.ui.lbl_info_page_error_msg.setVisible(True)
        self.ui.scrollArea_info_edit_page_categorisation_content.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.ui.scrollArea_info_edit_page_categorisation_content.update()

    def scrape_website_page(self, page_index, page_object):
        try:
            scraped_text_list, scraped_link_list = web_scrape(page_index, page_object.full_url)
            page_object.Label_Category_dict, page_object.Keywords_Exist_dict = self.categoryList.check_word_list(scraped_text_list)
            page_object.dict_to_output()
        except TimeoutException:
            page_object.remarks = "Connection failed - Timed out when fetching info"
        except Exception as e:
            print("debug scrape website", str(e))

    def generate_category_page(self):
        try:
            list_index = int(self.ui.input_info_edit_page_current_page.text()) - 1
            self.ui.input_info_edit_page_choose_marketing_purpose.setCurrentIndex(0)
            # self.ui.input_info_edit_page_expiring_date.date().toPyDate()
            self.ui.input_info_edit_page_expiring_date.setDateTime(QDateTime.currentDateTime())
            self.ui.input_info_edit_page_remarks.setText(self.edit_information_pages[list_index].remarks)
            self.ui.lbl_info_edit_page_full_url.setText(self.edit_information_pages[list_index].full_url)
            Label_Category_dict = self.edit_information_pages[list_index].Label_Category_dict
            if Label_Category_dict != []:
                try:
                    self.add_new_combobox(Label_Category_dict)
                except Exception as e:
                    print("some error", str(e))

                if self.edit_information_pages[list_index].TnC == "Yes":
                    self.ui.input_info_edit_page_tnc.setCurrentIndex(1)
                else:
                    self.ui.input_info_edit_page_tnc.setCurrentIndex(0)
                if self.edit_information_pages[list_index].PICS == "Yes":
                    self.ui.input_info_edit_page_pics.setCurrentIndex(1)
                else:
                    self.ui.input_info_edit_page_pics.setCurrentIndex(0)
                if self.edit_information_pages[list_index].Opt_in_out == "Yes":
                    self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(1)
                else:
                    self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(0)
                    self.ui.input_info_edit_page_choose_marketing_purpose.setCurrentText(self.edit_information_pages[list_index].purpose)
                self.ui.input_info_edit_page_expiring_date.date().toPyDate().today()
                self.scene_info_edit_page_screenshot = QGraphicsScene()
                if os.path.exists(f"Screen_Captures/ScreenShot_{list_index}.png"):
                    self.scene_info_edit_page_screenshot.addPixmap(
                        QPixmap(f"Screen_Captures/ScreenShot_{list_index}.png"))
                self.ui.graphicsView_info_edit_page_screenshot.verticalScrollBar().setSliderPosition(1)
                self.ui.graphicsView_info_edit_page_screenshot.horizontalScrollBar().setSliderPosition(1)
                self.ui.graphicsView_info_edit_page_screenshot.setScene(self.scene_info_edit_page_screenshot)
        except ValueError as e:
            print(str(e))
            pass
        print(Label_Category_dict)

    def preview_output(self):
        _translate = QtCore.QCoreApplication.translate
        self.get_combobox_data()
        while self.ui.table_report_page_report.rowCount() > 0:
            self.ui.table_report_page_report.removeRow(0)
            self.ui.table_report_page_report.horizontalHeader().setVisible(True)
            self.ui.table_report_page_report.verticalHeader().setVisible(True)
            self.ui.table_report_page_report.setColumnCount(12)
            item = QtWidgets.QTableWidgetItem()
            self.ui.table_report_page_report.setHorizontalHeaderItem(10, item)
            item = self.ui.table_report_page_report.horizontalHeaderItem(10)
            item.setText(_translate("MainWindow", "Remarks"))
            item = QtWidgets.QTableWidgetItem()
            self.ui.table_report_page_report.setHorizontalHeaderItem(11, item)
            item = self.ui.table_report_page_report.horizontalHeaderItem(11)
            item.setText(_translate("MainWindow", "PII"))
        for line in range(len(self.edit_information_pages)):
            row_position = self.ui.table_report_page_report.rowCount()
            self.ui.table_report_page_report.insertRow(row_position)
            self.ui.table_report_page_report.setItem(row_position, 0, QTableWidgetItem(self.edit_information_pages[line].fb_page_name))
            self.ui.table_report_page_report.setItem(row_position, 1, QTableWidgetItem(self.edit_information_pages[line].source))
            self.ui.table_report_page_report.setItem(row_position, 2, QTableWidgetItem(self.edit_information_pages[line].post_time))
            self.ui.table_report_page_report.setItem(row_position, 3, QTableWidgetItem(self.edit_information_pages[line].url))
            self.ui.table_report_page_report.setItem(row_position, 4, QTableWidgetItem(self.edit_information_pages[line].full_url))
            self.ui.table_report_page_report.setItem(row_position, 5, QTableWidgetItem(self.edit_information_pages[line].purpose))
            self.ui.table_report_page_report.setItem(row_position, 6, QTableWidgetItem(self.edit_information_pages[line].status))
            self.ui.table_report_page_report.setItem(row_position, 7, QTableWidgetItem(self.edit_information_pages[line].PICS))
            self.ui.table_report_page_report.setItem(row_position, 8, QTableWidgetItem(self.edit_information_pages[line].TnC))
            self.ui.table_report_page_report.setItem(row_position, 9, QTableWidgetItem(self.edit_information_pages[line].Opt_in_out))
            remarks = self.edit_information_pages[line].remarks
            if remarks == "":
                remarks = "NIL"
            self.ui.table_report_page_report.setItem(row_position, 10, QTableWidgetItem(remarks))
            PII = self.edit_information_pages[line].PII
            if PII == "":
                PII = "NIL"
            self.ui.table_report_page_report.setItem(row_position, 11, QTableWidgetItem(PII))
        self.ui.stackedWidget.setCurrentWidget(self.ui.report_page)

    def back_to_edits(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.info_edit_page)

    def add_new_combobox(self, Label_Category_dict):
        row = self.ui.formLayout_info_edit_page_scrolling_content.rowCount()
        while len(Label_Category_dict["Label"]) > row:
            self.ui.scrollArea_info_edit_page_categorisation_content.setWidgetResizable(True)
            self.ui.scrollArea_info_edit_page_categorisation_content.setSizeAdjustPolicy(
                QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.ui.scrollArea_info_edit_page_categorisation_content.update()
            if Label_Category_dict["Label"][0] != "":
                try:
                    Scraped_label_scroll = QScrollArea()
                    Scraped_label_scroll.setWidgetResizable(True)
                    Scraped_label_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    Scraped_label_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                    Scraped_label_scroll.setMaximumSize(180, 30)
                    Scraped_label = QLabel()
                    Scraped_label.setStyleSheet("color: rgb(255, 255, 255);")
                    Scraped_label.setWordWrap(True)
                    Scraped_label.setFixedWidth(160)
                    Scraped_label.setText(Label_Category_dict["Label"][row])
                    Scraped_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    Scraped_label_scroll.setWidget(Scraped_label)
                    Category = QComboBox()
                    font = QtGui.QFont()
                    font.setFamily("Arial Black")
                    font.setPointSize(10)
                    font.setBold(False)
                    font.setItalic(False)
                    font.setWeight(10)
                    Category.setFont(font)
                    Category.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
                    Category.setStyleSheet("QComboBox\n"
                                           "{\n"
                                           "    background-color: rgb(238, 238, 238);\n"
                                           "    color: rgb(98, 98, 98);\n"
                                           "    border-radius: 15px;\n"
                                           "    font-size: 15px;\n"
                                           "    padding-left: 20px;\n"
                                           "}\n"
                                           "\n"
                                           "QComboBox::down-arrow\n"
                                           "{\n"
                                           "    border-image: url(:/image/arrow_down_grey.png);\n"
                                           "    height: 15px;\n"
                                           "    width: 15px;\n"
                                           "}\n"
                                           "\n"
                                           "QComboBox::drop-down\n"
                                           "{\n"
                                           "    subcontrol-origin: padding;\n"
                                           "    subcontrol-position: top right;\n"
                                           "    width: 45px; \n"
                                           "    border-top-right-radius: 3px;\n"
                                           "    border-bottom-right-radius: 3px;\n"
                                           "}\n"
                                           "\n"
                                           "QComboBox QAbstractItemView\n"
                                           "{\n"
                                           "    color: rgb(98, 98, 98); /*dark grey*/\n"
                                           "    background-color: white;\n"
                                           "        selection-background-color: rgb(71, 10, 104); /*KPMG Purple*/\n"
                                           "    selection-color: white;\n"
                                           "    border-radius: 0px;\n"
                                           "}\n"
                                           "\n"
                                           "")
                    Category.setEditable(False)
                    Category.wheelEvent = lambda e: e.ignore
                    Category.addItem("Choose Category")
                    Category.addItems(list(self.categoryList.categories.keys()))
                    Category.setFixedSize(260, 30)
                    try:
                        if Label_Category_dict["Category"][row] == "":
                            Category.setCurrentText("Choose Category")
                        else:
                            Category.setCurrentText(Label_Category_dict["Category"][row])
                        self.ui.formLayout_info_edit_page_scrolling_content.addRow(Scraped_label_scroll, Category)
                        self.columnWidgets.append(Category)
                        self.ui.scrollArea_info_edit_page_categorisation_content.setWidget(self.ui.scrollAreaWidgetContents_info_edit_page)
                    except Exception as e:
                        print("debug a:", str(e))
                        self.ui.lbl_info_page_error_msg.setText(str(e))
                        self.ui.lbl_info_page_error_msg.setVisible(True)
                except Exception as e:
                    print("debug b:", str(e))
                    self.ui.lbl_info_page_error_msg.setText(str(e))
                    self.ui.lbl_info_page_error_msg.setVisible(True)
            else:
                try:
                    Empty_label = QLabel()
                    Empty_label.setMinimumSize(QtCore.QSize(100, 30))
                    Empty_label.setStyleSheet("color: rgb(255, 255, 255);")
                    Empty_label.setText("No items scraped")
                    self.ui.formLayout_info_edit_page_scrolling_content.addRow(Empty_label)
                    self.ui.scrollArea_info_edit_page_categorisation_content.setWidget(self.ui.scrollAreaWidgetContents_info_edit_page)
                except Exception as e:
                    print("debug c:", str(e))
            row += 1
        self.ui.scrollAreaWidgetContents_info_edit_page.setLayout(self.ui.formLayout_info_edit_page_scrolling_content)

    def get_combobox_data(self):
        Label_Category_dict = self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].Label_Category_dict
        if Label_Category_dict["Label"] == [""]:
            print("debug test - no items scraped")
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].remarks = "no text scraped"
        elif len(Label_Category_dict["Category"]) == len(self.columnWidgets):
            if self.columnWidgets:
                changed_category = [t.currentText() for t in self.columnWidgets]
                for index, item in enumerate(changed_category):
                    if item == "Choose Category":
                        item = "Unrelated"
                    if item != Label_Category_dict["Category"][index]:
                        self.categoryList.update_defined_category(Label_Category_dict["Label"][index], item)
                        Label_Category_dict["Category"][index] = item

        else:
            print("debug test")

        # Get current page data
        self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].purpose = self.ui.input_info_edit_page_choose_marketing_purpose.currentText()
        if self.ui.input_info_edit_page_expiring_date.date().toPyDate() < datetime.date.today():
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].status = 'Expired'
        elif (self.ui.input_info_edit_page_expiring_date.date().toPyDate() - datetime.date.today()).days > 90:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].status = 'Ongoing'
        else:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].status = 'Expire soon'
        if int(self.ui.input_info_edit_page_tnc.currentIndex()) == 1:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].TnC = "Yes"
        else:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].TnC = "No"
        if int(self.ui.input_info_edit_page_pics.currentIndex()) == 1:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].TnC = "Yes"
        else:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].TnC = "No"
        if int(self.ui.input_info_edit_page_choose_opt_in_out.currentIndex()) == 1:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].Opt_in_out = "Yes"
        else:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].Opt_in_out = "No"
        if self.ui.input_info_edit_page_remarks.toPlainText():
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].remarks = self.ui.input_info_edit_page_remarks.toPlainText()
        else:
            self.edit_information_pages[int(self.ui.input_info_edit_page_current_page.text()) - 1].remarks = ""

    def export_to_csv(self):
        save_to_path = filedialog.asksaveasfilename(defaultextension=".csv")
        with open(save_to_path, "w", encoding="utf8", newline="") as word_file:
            word_file.write(
                "Brand,Source,Post Date,Link,Full True Path,Purpose,Status,PIC?,T&C?,Opt-in/Opt-out,remarks,PII\n")
            writecsv = csv.writer(word_file)
            export_info = []
            for pages in self.edit_information_pages:
                export_info.append(pages.export())
            writecsv.writerows(export_info)
        word_file.close()
        # save scraped results from local variable to csv format

    def reset_app(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.search_page)
        self.edit_information_pages.clear()
        self.columnWidgets.clear()
        clear_screenshots()
        while self.ui.table_links_page_link_list.rowCount() > 0:
            self.ui.table_links_page_link_list.removeRow(0)
        while self.ui.table_report_page_report.rowCount() > 0:
            self.ui.table_report_page_report.removeRow(0)


def main():
    clear_screenshots()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
