from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])   # QApplication object represents the state of our running application
window = QtWidgets.QWidget(windowTitle='Hello Qt')

window.show()
app.exec()