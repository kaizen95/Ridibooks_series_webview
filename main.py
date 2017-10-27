import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

import requests, subprocess, time, sys
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

ridi_id = "aaaaa"               #리디북스 아이디
ridi_passwd = "aaa123123aaa"    #리디북스 패스워드

login_form = {
    'cmd': 'login',
    'return_url': '',
    'return_query_string': '',
    'user_id': ridi_id,
    'passwd' : ridi_passwd
    }

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(30,30,1050,950)

        #Qt - QWebEngineView        
        self.webview = webview(self)
        self.webview.setGeometry(10,10,800,900)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.login_auto)
        self.timer.setSingleShot(True)
        
        #ListWidget
        self.book_list_widget = QListWidget(self)
        self.book_list_widget.setGeometry(820,10, 200,900)
        self.book_list_widget.itemDoubleClicked.connect(self.select_book_clicked)

        #requests
        self.sess = requests.Session()
        req = self.sess.get('https://ridibooks.com/account/login?is_modal=1')
        login_req = self.sess.post('https://ridibooks.com/account/login', data=login_form)
        req = self.sess.get('https://ridibooks.com/v2/Detail?id=1811049824') # "이것이 법이다" 연재본 링크 위치 => 이를 다른 연재본 링크로도 대처가 가능하나, 확인되지 않음
        soup = BeautifulSoup(req.text, 'html.parser')

        
        my_titles = soup.select( # "이것이 법이다 1xxx화" 를 가져오기 위한 파서
            '#SeriesListWrap > ul.module_compact_book_list.white_theme.js_compact_book_list > li > div > div > div.table_cell.book_info > h3 > span'
            )
        buy_check = soup.select( # "구매" == b' \xea\xb5\xac\xeb\xa7\xa4' , "보기" == b'\n \xeb\xb3\xb4\xea\xb8\xb0\n      ' 를 구분하기 위한 파서
            '#SeriesListWrap > ul.module_compact_book_list.white_theme.js_compact_book_list > li > div > div > div.table_cell.book_status.direct_view_wrapper > button'
            )        
        book_id = soup.select( # 책 ID를 가져오기 위한 파서, 단, 가져올 형식은 이래야함 book_id[i].get('data-book-id')
            '#SeriesListWrap > ul.module_compact_book_list.white_theme.js_compact_book_list > li > div > div > div.table_cell.book_status.direct_view_wrapper > button'
            )

        self.book_list = [] # [책 타이틀, 책 ID] 형식으로 넣기 위한 리스트

        for i in range(len(book_id)):
            try:
                if buy_check[i].text.encode() == b'\n \xeb\xb3\xb4\xea\xb8\xb0\n      ':        # 해당 화수가 구매한 책인 경우
                    item = QListWidgetItem(my_titles[i].text)                                   # 해당 화수를 리스트 아이템으로 제작
                    self.book_list.append([my_titles[i].text, book_id[i].get('data-book-id')])  # 리스트에 [책 타이틀, 책 ID] 형식으로 넣음
                    self.book_list_widget.addItem(item)                                         # 제작된 아이템을 리스트 위젯에 추가함
            except IndexError:
                pass

        self.timer.start(1500) # 자동 로그인 처리

    def select_book_clicked(self, item): #리스트의 아이템을 더블 클릭시 발생하는 이벤트
        self.book_list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)    # 선택된 아이템이 중앙으로 가게끔 스크롤을 자동 조정함
        index = self.book_list[self.book_list_widget.currentRow()][1]                   # 선택된 아이템의 인덱스 값의 책 ID값을 가져옴
        self.webview.load(QUrl('https://view.ridibooks.com/books/%s' %(index)))         # 해당 화수로 이동함
        
    def login_auto(self):
        self.webview.page().runJavaScript(
                """document.getElementsByName('user_id')[0].value = '%s';
                   document.getElementsByName('passwd')[0].value = '%s';
                   document.getElementById('login_form').submit();
                """ %(ridi_id, ridi_passwd))


class webview(QWebEngineView):
    def __init__(self, parent):
        super(webview, self).__init__(parent)
        
        globalSettings = self.settings().globalSettings()
        globalSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        globalSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.load(QUrl('https://ridibooks.com/account/login'))
        

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
