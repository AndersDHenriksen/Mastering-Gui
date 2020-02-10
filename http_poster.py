import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtNetwork as qtn


class Poster(qtc.QObject):
    replyReceived = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.nam = qtn.QNetworkAccessManager()
        self.nam.finished.connect(self.on_reply)

    def on_reply(self, reply):
        reply_bytes = reply.readAll()
        reply_string = bytes(reply_bytes).decode('utf-8')
        self.replyReceived.emit(reply_string)

    def make_request(self, url, data, filename):
        self.request = qtn.QNetworkRequest(url)
        self.multipart = qtn.QHttpMultiPart(qtn.QHttpMultiPart.FormDataType)
        for key, value in (data or {}).items():
            http_part = qtn.QHttpPart()
            http_part.setHeader(qtn.QNetworkRequest.ContentDispositionHeader, f'form-data; name="{key}"')
            http_part.setBody(value.encode('utf-8'))
            self.multipart.append(http_part)
        if filename:
            file_part = qtn.QHttpPart()
            file_part.setHeader(qtn.QNetworkRequest.ContentDispositionHeader, f'form-data; name="attachment"; filename="{filename}"')
            filedata = open(filename, 'rb').read()
            file_part.setBody(filedata)
            self.multipart.append(file_part)
        self.nam.post(self.request, self.multipart)


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here
        widget = qtw.QWidget(minimumWidth=600)
        self.setCentralWidget(widget)
        widget.setLayout(qtw.QVBoxLayout())
        self.url = qtw.QLineEdit()
        self.table = qtw.QTableWidget(columnCount=2, rowCount=5)
        self.table.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['key', 'value'])
        self.fname = qtw.QPushButton('(No File)', clicked=self.on_file_btn)
        submit = qtw.QPushButton('Submit Post', clicked=self.submit)
        response = qtw.QTextEdit(readOnly=True)
        for w in (self.url, self.table, self.fname, submit, response):
            widget.layout().addWidget(w)
        self.poster = Poster()
        self.poster.replyReceived.connect(self.response.setText)
        # End main UI code
        self.show()

    def on_file_btn(self):
        filename, accepted = qtw.QFileDialog.getOpenFileName()
        if accepted:
            self.fname.setText(filename)

    def submit(self):
        url = qtc.QUrl(self.url.text())

        filename = self.fname.text()
        if filename == '(No File)':
            filename = None
        data = {}
        for rownum in range(self.table.rowCount()):
            key_item = self.table.item(rownum, 0)
            key = key_item.text() if key_item else None
            if key:
                data[key] = self.table.item(rownum, 1).text()
        self.poster.make_request(url, data, filename)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())