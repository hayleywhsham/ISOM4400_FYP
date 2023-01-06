from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from MainPageUI import Ui_MainWindow
from fb_scraper_with_dict import get_all_urls


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
        self.ui.input_search_page_from_fb_page.returnPressed.connect(self.ui.button_search_page_search_marketing_sites.click)
        # reset Max from_date when to_date is changed
        self.ui.input_search_page_to_date.dateChanged.connect(lambda: self.ui.input_search_page_from_date.setMaximumDate(self.ui.input_search_page_to_date.date()))



    def search_urls(self):

        # PlaceHolder
        start_date = self.ui.input_search_page_from_date.date().toPyDate()
        end_date = self.ui.input_search_page_to_date.date().toPyDate()

        user_input: str = self.ui.input_search_page_from_fb_page.text()
        urls_dict_list = None

        if user_input != "":
            urls_dict_list = get_all_urls(user_input, start_date, end_date)
            self.ui.stackedWidget.setCurrentWidget(self.ui.links_page)
            self.init_links_page(urls_dict_list)
        else:
            self.ui.lbl_search_page_from_fb_page_error_msg.setStyleSheet("""
            color: rgb(255, 0, 0);
            background-color: transparent;
            font: 75 10pt "Arial";
            """)
            self.ui.lbl_search_page_from_fb_page_error_msg.setText("Please input Facebook Page tag!")

    def init_links_page(self, urls_dict_list):
        self.ui.table_links_page_link_list.verticalHeader().setVisible(True)
        self.ui.table_links_page_link_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for url_dict in urls_dict_list:
            rowPosition = self.ui.table_links_page_link_list.rowCount()
            self.ui.table_links_page_link_list.insertRow(rowPosition)
            self.ui.table_links_page_link_list.setItem(rowPosition, 0, QTableWidgetItem(url_dict["Brand"]))
            self.ui.table_links_page_link_list.setItem(rowPosition, 1, QTableWidgetItem(url_dict["Source"]))
            self.ui.table_links_page_link_list.setItem(rowPosition, 2, QTableWidgetItem(url_dict["PostTime"]))
            self.ui.table_links_page_link_list.setItem(rowPosition, 3, QTableWidgetItem(url_dict["ShortLink"]))

    # def to_date_changed(self, new_to_date):



def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
