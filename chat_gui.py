import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtNetwork as qtn


class ChatWindow(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QGridLayout())
        self.message_view = qtw.QTextEdit(readOnly=True)
        self.layout().addWidget(self.message_view, 1, 1, 1, 2)
        self.message_entry = qtw.QLineEdit()
        self.layout().addWidget(self.message_entry, 2, 1)
        self.send_btn = qtw.QPushButton('Send', clicked=self.send)
        self.layout().addWidget(self.send_btn, 2, 2)

    def write_message(self, username, message):
        self.message_view.append(f'<b>{username}: </b> {message}<br>')

    def send(self):
        message = self.message_entry.text().strip()
        if message:
            self.submitted.emit(message)
            self.message_entry.clear()


class UdpChatInterface(qtc.QObject):
    port = 7777
    delimiter = '||'
    received = qtc.pyqtSignal(str, str)
    error = qtc.pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.socket = qtn.QUdpSocket()
        self.socket.bind(qtn.QHostAddress.Any, self.port)
        self.socket.readyRead.connect(self.process_datagrams)
        self.socket.error.connect(self.on_error)

    def on_error(self, socket_error):
        error_index = qtn.QAbstractSocket.staticMetaObject.indexOfEnumerator('SocketError')
        error = qtn.QAbstractSocket.staticMetaObject.enumerator(error_index).valueToKey(socket_error)
        message = f"There was a network error: {error}"
        self.error.emit(message)

    def process_datagrams(self):
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            raw_message = bytes(datagram.data()).decode('utf-8')
            if self.delimiter not in raw_message:
                continue
            username, message = raw_message.split(self.delimiter, 1)
            self.received.emit(username, message)

    def send_message(self, message):
        msg_bytes = f'{self.username}{self.delimiter}{message}'.encode('utf-8')
        self.socket.writeDatagram(qtc.QByteArray(msg_bytes), qtn.QHostAddress.Broadcast, self.port)


class TcpChatInterface(qtc.QObject):
    port = 7777
    delimiter = '||'
    received = qtc.pyqtSignal(str, str)
    error = qtc.pyqtSignal(str)

    def __init__(self, username, recipient):
        super().__init__()
        self.username = username
        self.recipient = recipient

        self.listener = qtn.QTcpServer()
        self.listener.listen(qtn.QHostAddress.Any, self.port)
        self.listener.acceptError.connect(self.on_error)
        self.listener.newConnection.connect(self.on_connection)
        self.connections = []

        self.client_socket = qtn.QTcpSocket()
        self.client_socket.error.connect(self.on_error)

    def on_error(self, socket_error):
        error_index = qtn.QAbstractSocket.staticMetaObject.indexOfEnumerator('SocketError')
        error = qtn.QAbstractSocket.staticMetaObject.enumerator(error_index).valueToKey(socket_error)
        message = f"There was a network error: {error}"
        self.error.emit(message)

    def on_connection(self):
        connection = self.listener.nextPendingConnection()
        connection.readyRead.connect(self.process_datastream)
        self.connections.append(connection)

    def process_datastream(self):
        for socket in self.connections:
            self.datastream = qtc.QDataStream(socket)
            if not socket.bytesAvailable():
                continue
            raw_message = self.datastream.readQString()
            if raw_message and self.delimiter in raw_message:
                username, message = raw_message.split(self.delimiter, 1)
                self.received.emit(username, message)

    def send_message(self, message):
        raw_message = f'{self.username}{self.delimiter}{message}'
        socket_state = self.client_socket.state()
        if socket_state != qtn.QAbstractSocket.ConnectedState:
            self.client_socket.connectToHost(self.recipient, self.port)
            self.datastream = qtc.QDataStream(self.client_socket)
            self.datastream.writeQString(raw_message)
            self.received.emit(self.username, message)


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here
        self.cw = ChatWindow()
        self.setCentralWidget(self.cw)

        username = qtc.QDir.home().dirName()

        # # UDP
        # self.interface = UdpChatInterface(username)
        # self.cw.submitted.connect(self.interface.send_message)
        # self.interface.received.connect(self.cw.write_message)
        # self.interface.error.connect(lambda x: qtw.QMessageBox.critical(None, 'Error', x))

        # TCP
        recipient, _ = qtw.QInputDialog.getText(None, 'Recipient', 'Specify of the IP or hostname of the remote host.')
        if not recipient:
            sys.exit()
        self.interface = TcpChatInterface(username, recipient)
        self.cw.submitted.connect(self.interface.send_message)
        self.interface.received.connect(self.cw.write_message)
        self.interface.error.connect(lambda x: qtw.QMessageBox.critical(None, 'Error', x))

        # End main UI code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())