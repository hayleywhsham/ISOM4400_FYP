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
from myException import GetFullURLFail

from facebook_scraper import get_posts
from facebook_scraper.exceptions import NotFound, TemporarilyBanned


def clear_screenshots():
    # remove screenshots from last run of system
    for screenshot in os.listdir("Screen_Captures"):
        os.remove("Screen_Captures/" + screenshot)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Will be blocked easily by Facebook, Facebook API highly restricted
        # Without cookie can only get 60 newest posts from page
        # Source : https://developers.facebook.com/docs/graph-api/overview/rate-limiting/

        # If do not want cookie can change here, but will scrape less posts
        self.cookie_mode = True     # Can choose cookie_mode = False

        # Importing initial information and instantiating system
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

        # reset Max from_date when to_date is changed
        self.ui.input_search_page_to_date.dateChanged.connect(
            lambda: self.ui.input_search_page_from_date.setMaximumDate(self.ui.input_search_page_to_date.date()))

        self.error_message_lock = threading.Lock()
        self.add_content_lock = threading.Lock()
        self.add_table_row_lock = threading.Lock()

        # Change page when new page number typed, currently not applicable (i.e. need to use buttons)
        # self.ui.input_info_edit_page_current_page.textEdited.connect(self.update_page)

    def search_urls(self):
        # Single input for Facebook Page Name in page 1
        self.user_input: str = self.ui.input_search_page_from_fb_page.text()

        # Error message for empty input string
        if self.user_input != "":
            self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)
            start_date = self.ui.input_search_page_from_date.date().toPyDate()
            end_date = self.ui.input_search_page_to_date.date().toPyDate()

            t1 = threading.Thread(target=self.multi_thread_search, args=([self.user_input], start_date, end_date))
            t1.start()
        else:
            self.ui.lbl_search_page_from_fb_page_error_msg.setStyleSheet("""
            color: rgb(255, 0, 0);
            background-color: transparent;
            font: 75 10pt "Arial";
            """)
            self.ui.lbl_search_page_from_fb_page_error_msg.setText("Please input Facebook Page tag!")

    def search_urls_from_csv(self):
        # Bulk input for Facebook Page Names in page 1
        tkinter.Tk().withdraw()
        csv_path = filedialog.askopenfilename(filetypes=[("Excel files", ".csv")])

        if csv_path:
            with open(csv_path, "r") as file:
                fb_names_csv_reader = csv.reader(file, delimiter=",")
                fb_names = []
                for fb_name in fb_names_csv_reader:
                    if type(fb_name) == list:
                        fb_names.append(fb_name[0])
                    else:
                        fb_names.append(fb_name)

            start_date = self.ui.input_search_page_from_date.date().toPyDate()
            end_date = self.ui.input_search_page_to_date.date().toPyDate()

            t = threading.Thread(target=self.multi_thread_search, args=(fb_names, start_date, end_date))
            t.start()

            self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)

    def init_links_page(self, fb_page_name: str, start_date: datetime.date, end_date: datetime.date):
        # Instantiate page 2
        self.ui.table_links_page_link_list.verticalHeader().setVisible(True)
        self.ui.table_links_page_link_list.horizontalHeader().setVisible(True)
        self.ui.table_links_page_link_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.lbl_links_page_last_updated_datetime.setText("Loading")
        full_urls = []
        fb_page_name = fb_page_name
        source = "Facebook"
        post_count = 0
        total_number_of_link = 0
        number_of_link = 0

        # Scrape Facebook Page posts from Facebook Page Name
        try:
            posts = get_posts(fb_page_name, pages=99999, cookies="./fbUserToken.json") if self.cookie_mode else \
                get_posts(fb_page_name, pages=99999)

            for post in posts:
                post_time = post['time']

                if post_time is not None and post_time.date() < start_date:
                    if post_count == 0:
                        post_count += 1
                        continue  # for skipping the (first) pinned post
                    else:
                        break
                if post_time is None or post_time.date() <= end_date:
                    urls = set(get_all_url_from_string(post['text']))  # set: unique per post
                    for url in urls:

                        # convert short url to valid links (e.g. bit.ly  with http:// as network resource allocator)
                        if not (url.startswith("http://") or url.startswith("https://")):
                            url = "http://" + url
                        post_time_str = post_time.strftime("%Y/%m/%d") if post_time is not None else ""
                        link_object = EditInformationPage(fb_page_name,
                                                          source,
                                                          post_time_str,
                                                          url)
                        total_number_of_link += 1
                        if link_object.full_url not in full_urls:
                            number_of_link += 1
                            full_urls.append(link_object.full_url)

                            self.add_content_lock.acquire()
                            self.edit_information_pages.append(link_object)
                            self.add_content_lock.release()

                            self.add_table_row_lock.acquire()

                            # Generate table in page 2
                            row_position = self.ui.table_links_page_link_list.rowCount()
                            self.ui.table_links_page_link_list.insertRow(row_position)
                            self.ui.table_links_page_link_list.setItem(row_position, 0,
                                                                       QTableWidgetItem(link_object.fb_page_name))
                            self.ui.table_links_page_link_list.setItem(row_position, 1,
                                                                       QTableWidgetItem(link_object.source))
                            self.ui.table_links_page_link_list.setItem(row_position, 2,
                                                                       QTableWidgetItem(link_object.post_time))
                            self.ui.table_links_page_link_list.setItem(row_position, 3,
                                                                       QTableWidgetItem(link_object.url))
                            self.ui.table_links_page_link_list.setItem(row_position, 4,
                                                                       QTableWidgetItem(link_object.full_url))

                            last_update_time = datetime.datetime.now().strftime("%H:%M")
                            self.ui.lbl_links_page_last_updated_datetime.setText(f'Loading - {last_update_time}')

                            self.add_table_row_lock.release()
                    post_count += 1

        # Error message - Facebook Page not found (i.e. wrong input)
        except NotFound:
            self.error_message_lock.acquire()
            error_msg = self.ui.lbl_links_page_error_msg.text()

            if error_msg == "":
                error_msg = f'{fb_page_name} doesn\'t not exist! Please check again!'
            else:
                error_msg = f'{fb_page_name}, {error_msg}'

            self.ui.lbl_links_page_error_msg.setText(error_msg)
            self.error_message_lock.release()

        # Error message - Temporarily banned by Facebook
        except TemporarilyBanned:
            msg = "You being Temporarily Banned by Facebook!"

            self.ui.lbl_links_page_error_msg_ban.setText(msg)

            msg_heading = "\nThe following page have not been searched: "

            self.error_message_lock.acquire()
            error_msg = self.ui.lbl_links_page_error_msg.text()

            if (msg_heading not in error_msg):
                error_msg = error_msg + msg_heading + fb_page_name
            else:
                error_msg = f'{error_msg},{fb_page_name}'

            self.ui.lbl_links_page_error_msg.setText(error_msg)
            self.error_message_lock.release()

        # Debug message - only for back-end users
        print(f'Scrapped {post_count} post(s) for {fb_page_name}. Got {total_number_of_link} link(s). '
              f'Got {number_of_link} unique links.')

    def multi_thread_search(self, fb_names, start_date, end_date):
        # Multi-threading function for scraping posts in multiple Facebook Pages
        threads = []
        for fb_name in fb_names:
            t = threading.Thread(target=self.init_links_page, args=(fb_name, start_date, end_date))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        last_update_time = datetime.datetime.now().strftime("%H:%M")
        self.ui.lbl_links_page_last_updated_datetime.setText(f'Done - {last_update_time}')

    def back_to_search_page(self):
        # Back button from page 2 to page 1
        while self.ui.table_links_page_link_list.rowCount() > 0:
            self.ui.table_links_page_link_list.removeRow(0)
        self.ui.stackedWidget.setCurrentWidget(self.ui.search_page)
        self.edit_information_pages.clear()
        self.ui.lbl_links_page_error_msg.setText(None)
        self.ui.lbl_links_page_error_msg_ban.setText(None)

    def initial_edit_page(self):
        # Instantiate Page 3
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
            self.update_page()
            self.ui.lbl_info_page_error_msg.setVisible(False)
        except Exception as e:
            self.ui.lbl_info_page_error_msg.setText(str(e))
            self.ui.lbl_info_page_error_msg.setVisible(True)
        self.ui.scrollArea_info_edit_page_categorisation_content.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.ui.scrollArea_info_edit_page_categorisation_content.update()

    def scrape_website_page(self, page_index, page_object):
        # Conduct Marketing Website scraping for page 3
        try:
            scraped_text_list, scraped_link_list = web_scrape(page_index, page_object.full_url)
            page_object.Label_Category_dict, page_object.Keywords_Exist_dict = self.categoryList.check_word_list(
                scraped_text_list)
            page_object.dict_to_output()
        except TimeoutException:
            page_object.remarks = "Connection failed - Timed out when fetching info"
        except GetFullURLFail as error :
            page_object.remarks = f'URL Error - The full URL is empty. Maybe the shorten url ({error.short_URL}) is already broken.'

    def generate_category_page(self):
        # Display current Marketing Website Information
        try:
            list_index = int(self.ui.input_info_edit_page_current_page.text()) - 1
            self.ui.input_info_edit_page_choose_marketing_purpose.setCurrentIndex(0)
            self.ui.input_info_edit_page_expiring_date.setDate(self.edit_information_pages[list_index].expire_date)
            if self.edit_information_pages[list_index].remarks != "NIL":
                self.ui.input_info_edit_page_remarks.setText(self.edit_information_pages[list_index].remarks)
            else:
                self.ui.input_info_edit_page_remarks.setText("")
            self.ui.lbl_info_edit_page_full_url.setText(self.edit_information_pages[list_index].full_url)
            Label_Category_dict = self.edit_information_pages[list_index].Label_Category_dict

            try:
                self.add_new_combobox(Label_Category_dict)
            except Exception:
                pass

            if self.edit_information_pages[list_index].TnC == "Default":
                self.ui.input_info_edit_page_tnc.setCurrentIndex(0)
            elif self.edit_information_pages[list_index].TnC == "Yes":
                self.ui.input_info_edit_page_tnc.setCurrentIndex(1)
            else:
                self.ui.input_info_edit_page_tnc.setCurrentIndex(2)

            if self.edit_information_pages[list_index].PICS == "Default":
                self.ui.input_info_edit_page_pics.setCurrentIndex(0)
            elif self.edit_information_pages[list_index].PICS == "Yes":
                self.ui.input_info_edit_page_pics.setCurrentIndex(1)
            else:
                self.ui.input_info_edit_page_pics.setCurrentIndex(2)

            if self.edit_information_pages[list_index].Opt_in_out == "Default":
                self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(0)
            elif self.edit_information_pages[list_index].Opt_in_out == "Yes":
                self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(1)
            else:
                self.ui.input_info_edit_page_choose_opt_in_out.setCurrentIndex(2)

            self.ui.input_info_edit_page_choose_marketing_purpose.setCurrentText(
                self.edit_information_pages[list_index].purpose)
            self.scene_info_edit_page_screenshot = QGraphicsScene()
            if os.path.exists(f"Screen_Captures/ScreenShot_{list_index}.png"):
                self.scene_info_edit_page_screenshot.addPixmap(
                    QPixmap(f"Screen_Captures/ScreenShot_{list_index}.png"))
            self.ui.graphicsView_info_edit_page_screenshot.verticalScrollBar().setSliderPosition(0)
            self.ui.graphicsView_info_edit_page_screenshot.horizontalScrollBar().setSliderPosition(0)
            self.ui.graphicsView_info_edit_page_screenshot.setScene(self.scene_info_edit_page_screenshot)
        except ValueError:
            pass

    def update_page(self):
        # Clear current Marketing Website Information
        while self.ui.formLayout_info_edit_page_scrolling_content.rowCount() > 0:
            self.ui.formLayout_info_edit_page_scrolling_content.removeRow(0)
        self.columnWidgets.clear()
        self.update_categories()

        # Create new page for Marketing Website Information
        self.generate_category_page()

    def update_categories(self):
        # Updates in one Marketing Website will cause update in other Marketing Websites if applicable
        try:
            max_pages = int(self.ui.lbl_info_edit_page_total_pages.text())
            for page in range(max_pages):
                page_object = self.edit_information_pages[page]
                page_object.Label_Category_dict, Keywords_Exist_dict = self.categoryList.check_word_list(
                    page_object.Label_Category_dict["Label"])
                page_object.dict_to_output()
                if (page_object.Label_Category_dict["Label"] == [""]) and (page_object.remarks == ""):
                    page_object.remarks = "No text scraped"
        except Exception:
            pass

    def add_new_combobox(self, Label_Category_dict):
        # Create dynamic length Personal Information Categorization list display in page 3
        self.ui.formLayout_info_edit_page_scrolling_content.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        row = self.ui.formLayout_info_edit_page_scrolling_content.rowCount()
        self.ui.scrollArea_info_edit_page_categorisation_content.setWidgetResizable(True)
        self.ui.scrollArea_info_edit_page_categorisation_content.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)

        while len(Label_Category_dict["Label"]) > row:
            if (Label_Category_dict["Label"]) and (Label_Category_dict["Label"][0] != ""):
                try:
                    # Create scrollable text lable for lengthy text values
                    Scraped_label_scroll = QScrollArea()
                    Scraped_label_scroll.setWidgetResizable(True)
                    Scraped_label_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    Scraped_label_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                    Scraped_label_scroll.setMaximumSize(180, 30)
                    Scraped_label_scroll.setMinimumSize(160, 30)
                    Scraped_label = QLabel()
                    Scraped_label.setStyleSheet("color: rgb(255, 255, 255);")
                    Scraped_label.setWordWrap(True)
                    Scraped_label.setFixedWidth(160)
                    Scraped_label.setText(Label_Category_dict["Label"][row])
                    Scraped_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    Scraped_label_scroll.setWidget(Scraped_label)

                    # Create category dropdown box
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

                    # Disabled typing new value
                    Category.setEditable(False)

                    # Disabled mouse scrolling to affect dropdown value
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
                        self.ui.scrollArea_info_edit_page_categorisation_content.setWidget(
                            self.ui.scrollAreaWidgetContents_info_edit_page)
                    except Exception as e:
                        self.ui.lbl_info_page_error_msg.setText(str(e))
                        self.ui.lbl_info_page_error_msg.setVisible(True)
                except Exception as e:
                    self.ui.lbl_info_page_error_msg.setText(str(e))
                    self.ui.lbl_info_page_error_msg.setVisible(True)
            else:
                try:
                    # Create empty label indicating no text labels scraped
                    Empty_label = QLabel()
                    Empty_label.setMinimumSize(QtCore.QSize(100, 30))
                    Empty_label.setStyleSheet("color: rgb(255, 255, 255);")
                    Empty_label.setText("No items scraped")
                    self.ui.formLayout_info_edit_page_scrolling_content.addRow(Empty_label)
                    self.ui.scrollArea_info_edit_page_categorisation_content.setWidget(
                        self.ui.scrollAreaWidgetContents_info_edit_page)
                except Exception as e:
                    self.ui.lbl_info_page_error_msg.setText(str(e))
                    self.ui.lbl_info_page_error_msg.setVisible(True)
            row += 1
        self.ui.scrollAreaWidgetContents_info_edit_page.setLayout(self.ui.formLayout_info_edit_page_scrolling_content)
        self.ui.scrollArea_info_edit_page_categorisation_content.update()
        self.ui.scrollAreaWidgetContents_info_edit_page.update()

    def get_combobox_data(self):
        # Get current page text label categorization information (i.e. selected dropdown items)
        page_index = int(self.ui.input_info_edit_page_current_page.text()) - 1
        Label_Category_dict = self.edit_information_pages[page_index].Label_Category_dict

        if Label_Category_dict["Label"] == [""]:
            self.edit_information_pages[page_index].remarks = "no text scraped"
        elif len(Label_Category_dict["Category"]) == len(self.columnWidgets):

            if self.columnWidgets:
                changed_category = [t.currentText() for t in self.columnWidgets]

                for index, item in enumerate(changed_category):
                    if item == "Choose Category":
                        item = "Unrelated"
                    if item != Label_Category_dict["Category"][index]:
                        self.categoryList.update_defined_category(Label_Category_dict["Label"][index], item)
                        Label_Category_dict["Category"][index] = item

        # Update new values to current Marketing Website class object
        self.edit_information_pages[page_index].Label_Category_dict = Label_Category_dict

        # Get current page information other than text label categorization (i.e. user inputs)
        # Get Marketing Purpose
        self.edit_information_pages[
            page_index].purpose = self.ui.input_info_edit_page_choose_marketing_purpose.currentText()

        # Get Expiry Status from Expiring Date
        self.edit_information_pages[
            page_index].expire_date = self.ui.input_info_edit_page_expiring_date.date().toPyDate()
        if self.ui.input_info_edit_page_expiring_date.date().toPyDate() < datetime.date.today():
            self.edit_information_pages[page_index].status = 'Expired'
        elif (self.ui.input_info_edit_page_expiring_date.date().toPyDate() - datetime.date.today()).days > 90:
            self.edit_information_pages[page_index].status = 'Ongoing'
        else:
            self.edit_information_pages[
                int(self.ui.input_info_edit_page_current_page.text()) - 1].status = 'Expire soon'

        # Get Keywords user input (i.e. T&C, P.I.C.S., Opt-in / Opt-out)
        if int(self.ui.input_info_edit_page_tnc.currentIndex()) == 0:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][0] = "Default"
        elif int(self.ui.input_info_edit_page_tnc.currentIndex()) == 1:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][0] = "Yes"
        else:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][0] = "No"

        if int(self.ui.input_info_edit_page_pics.currentIndex()) == 0:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][1] = "Default"
        elif int(self.ui.input_info_edit_page_pics.currentIndex()) == 1:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][1] = "Yes"
        else:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][1] = "No"

        if int(self.ui.input_info_edit_page_choose_opt_in_out.currentIndex()) == 0:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][2] = "Default"
        elif int(self.ui.input_info_edit_page_choose_opt_in_out.currentIndex()) == 1:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][2] = "Yes"
        else:
            self.edit_information_pages[page_index].Keywords_Exist_dict["Exist?"][2] = "No"

        # Get Remarks
        if self.ui.input_info_edit_page_remarks.toPlainText():
            self.edit_information_pages[page_index].remarks = self.ui.input_info_edit_page_remarks.toPlainText()
        else:
            self.edit_information_pages[page_index].remarks = ""

    def next_page(self):
        # Button to navigate to next page of Marketing Website
        page_number = int(self.ui.input_info_edit_page_current_page.text())
        max_pages = int(self.ui.lbl_info_edit_page_total_pages.text())

        try:
            self.get_combobox_data()
        except Exception as e:
            pass

        # Validity check - only if this is not last page
        if page_number < max_pages:
            self.ui.input_info_edit_page_current_page.setText(str(page_number + 1))
            self.update_page()

    def previous_page(self):
        # Button to navigate to previous page of Marketing Website
        page_number = int(self.ui.input_info_edit_page_current_page.text())

        # Get current page information (i.e. selected dropdown items)
        try:
            self.get_combobox_data()
        except Exception as e:
            pass

        # Validity check - only if this is not first page
        if page_number > 1:
            self.ui.input_info_edit_page_current_page.setText(str(page_number - 1))
            self.ui.input_info_edit_page_remarks.setText(self.edit_information_pages[page_number - 2].remarks)
            self.update_page()

    def back_to_links_page(self):
        # Back button from page 3 to page 2
        self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)

    def preview_output(self):
        # Instantiate page 4 preview report
        _translate = QtCore.QCoreApplication.translate
        self.get_combobox_data()
        self.update_page()
        while self.ui.table_report_page_report.rowCount() > 0:
            self.ui.table_report_page_report.removeRow(0)
        self.ui.table_report_page_report.horizontalHeader().setVisible(True)
        self.ui.table_report_page_report.verticalHeader().setVisible(True)
        self.ui.table_report_page_report.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.table_report_page_report.setColumnCount(12)
        self.ui.table_report_page_report.horizontalHeaderItem(7).setText(_translate("MainWindow", "P.I.C.S."))
        item = QtWidgets.QTableWidgetItem()
        self.ui.table_report_page_report.setHorizontalHeaderItem(10, item)
        self.ui.table_report_page_report.horizontalHeaderItem(10).setText(_translate("MainWindow", "Remarks"))
        item = QtWidgets.QTableWidgetItem()
        self.ui.table_report_page_report.setHorizontalHeaderItem(11, item)
        self.ui.table_report_page_report.horizontalHeaderItem(11).setText(_translate("MainWindow", "PII"))

        # Generate Page 4 report table
        for line in range(len(self.edit_information_pages)):
            self.edit_information_pages[line].dict_to_output()
            row_position = self.ui.table_report_page_report.rowCount()
            self.ui.table_report_page_report.insertRow(row_position)
            self.ui.table_report_page_report.setItem(row_position, 0,
                                                     QTableWidgetItem(self.edit_information_pages[line].fb_page_name))
            self.ui.table_report_page_report.setItem(row_position, 1,
                                                     QTableWidgetItem(self.edit_information_pages[line].source))
            self.ui.table_report_page_report.setItem(row_position, 2,
                                                     QTableWidgetItem(self.edit_information_pages[line].post_time))
            self.ui.table_report_page_report.setItem(row_position, 3,
                                                     QTableWidgetItem(self.edit_information_pages[line].url))
            self.ui.table_report_page_report.setItem(row_position, 4,
                                                     QTableWidgetItem(self.edit_information_pages[line].full_url))
            self.ui.table_report_page_report.setItem(row_position, 5,
                                                     QTableWidgetItem(self.edit_information_pages[line].purpose))
            self.ui.table_report_page_report.setItem(row_position, 6,
                                                     QTableWidgetItem(self.edit_information_pages[line].status))

            if self.edit_information_pages[line].PICS == "Default":
                self.ui.table_report_page_report.setItem(row_position, 7, QTableWidgetItem("No"))
            else:
                self.ui.table_report_page_report.setItem(row_position, 7,
                                                         QTableWidgetItem(self.edit_information_pages[line].PICS))

            if self.edit_information_pages[line].TnC == "Default":
                self.ui.table_report_page_report.setItem(row_position, 8, QTableWidgetItem("No"))
            else:
                self.ui.table_report_page_report.setItem(row_position, 8,
                                                         QTableWidgetItem(self.edit_information_pages[line].TnC))

            if self.edit_information_pages[line].Opt_in_out == "Default":
                self.ui.table_report_page_report.setItem(row_position, 9, QTableWidgetItem("No"))
            else:
                self.ui.table_report_page_report.setItem(row_position, 9,
                                                         QTableWidgetItem(self.edit_information_pages[line].Opt_in_out))

            if self.edit_information_pages[line].remarks == "":
                self.edit_information_pages[line].remarks = "NIL"
            self.ui.table_report_page_report.setItem(row_position, 10,
                                                     QTableWidgetItem(self.edit_information_pages[line].remarks))

            if self.edit_information_pages[line].PII == "":
                self.edit_information_pages[line].PII = "NIL"
            self.ui.table_report_page_report.setItem(row_position, 11,
                                                     QTableWidgetItem(self.edit_information_pages[line].PII))

        last_update_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        self.ui.lbl_report_page_last_updated_datetime.setText(last_update_time)
        self.ui.stackedWidget.setCurrentWidget(self.ui.report_page)

    def back_to_edits(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.info_edit_page)
        while self.ui.table_report_page_report.rowCount() > 0:
            self.ui.table_report_page_report.removeRow(0)

    def export_to_csv(self):
        # Export report to csv format
        tkinter.Tk().withdraw()
        save_to_path = filedialog.asksaveasfilename(defaultextension=".csv")
        if save_to_path:
            with open(save_to_path, "w", encoding="utf8", newline="") as word_file:
                word_file.write(
                    "Brand,Source,Post Date,Link,Full True Path,Purpose,Status,PIC?,T&C?,Opt-in/Opt-out,remarks,PII\n")
                writecsv = csv.writer(word_file)
                export_info = []
                for pages in self.edit_information_pages:
                    export_info.append(pages.export())
                writecsv.writerows(export_info)
            word_file.close()
            self.reset_app()

    def reset_app(self):
        # Reset system to page 1 clean state
        self.ui.stackedWidget.setCurrentWidget(self.ui.search_page)
        self.ui.input_search_page_from_fb_page.clear()
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
