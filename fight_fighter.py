import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import fight_fighter_resources as resources


class ColorButton(qtw.QPushButton):

    def _color(self):
        return self.palette().color(qtg.QPalette.ButtonText)

    def _setColor(self, qcolor):
        palette = self.palette()
        palette.setColor(qtg.QPalette.ButtonText, qcolor)
        self.setPalette(palette)

    color = qtc.pyqtProperty(qtg.QColor, _color, _setColor)

    @qtc.pyqtProperty(qtg.QColor)
    def backgroundColor(self):
        return self.palette().color(qtg.QPalette.Button)

    @backgroundColor.setter
    def backgroundColor(self, qcolor):
        palette = self.palette()
        palette.setColor(qtg.QPalette.Button, qcolor)
        self.setPalette(palette)


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here

        self.setWindowTitle('Fight Fighter Game Lobby')
        cx_form = qtw.QWidget()
        self.setCentralWidget(cx_form)
        cx_form.setLayout(qtw.QFormLayout())
        heading = qtw.QLabel("Fight Fighter!")
        cx_form.layout().addRow(heading)
        inputs = {
            'Server': qtw.QLineEdit(),
            'Name': qtw.QLineEdit(),
            'Password': qtw.QLineEdit(echoMode=qtw.QLineEdit.Password),
            'Team': qtw.QComboBox(),
            'Ready': qtw.QCheckBox('Check when ready')
        }
        teams = ('Crimson Sharks', 'Shadow Hawks',
                 'Night Terrors', 'Blue Crew')
        inputs['Team'].addItems(teams)
        for label, widget in inputs.items():
            cx_form.layout().addRow(label, widget)
        self.submit = qtw.QPushButton('Connect', clicked=lambda: qtw.QMessageBox.information(None, 'Connecting', 'Prepare for Battle!'))
        self.cancel = qtw.QPushButton('Cancel', clicked=self.close)
        cx_form.layout().addRow(self.submit, self.cancel)

        # Styling
        heading_font = qtg.QFont('Impact', 32, qtg.QFont.Bold)
        heading_font.setStretch(qtg.QFont.ExtraExpanded)
        heading.setFont(heading_font)

        button_font = qtg.QFont('Totally Nonexistant Font Family XYZ', 15.233)
        button_font.setStyleHint(qtg.QFont.Fantasy)  # If fall back font is bad, use below or similar
        button_font.setStyleStrategy(qtg.QFont.PreferAntialias | qtg.QFont.PreferQuality)
        actual_font = qtg.QFontInfo(button_font)
        print(f'Actual font used is {actual_font.family()}'
              f' {actual_font.pointSize()}')
        self.submit.setFont(button_font)
        self.cancel.setFont(button_font)

        logo = qtg.QPixmap('Mastering-GUI-Programming-with-Python/Chapter06/logo.png')
        if logo.width() > 400:
            logo = logo.scaledToWidth(400, qtc.Qt.SmoothTransformation)
        heading.setPixmap(logo)

        go_pixmap = qtg.QPixmap(qtc.QSize(32, 32))
        stop_pixmap = qtg.QPixmap(qtc.QSize(32, 32))
        go_pixmap.fill(qtg.QColor('green'))
        stop_pixmap.fill(qtg.QColor('red'))
        connect_icon = qtg.QIcon()
        connect_icon.addPixmap(go_pixmap, qtg.QIcon.Active)
        connect_icon.addPixmap(stop_pixmap, qtg.QIcon.Disabled)

        self.submit.setIcon(connect_icon)
        self.submit.setDisabled(True)
        inputs['Server'].textChanged.connect(lambda x: self.submit.setDisabled(x == ''))

        inputs['Team'].setItemIcon(0, qtg.QIcon(':/teams/crimson_sharks.png'))
        inputs['Team'].setItemIcon(1, qtg.QIcon(':/teams/shadow_hawks.png'))
        inputs['Team'].setItemIcon(2, qtg.QIcon(':/teams/night_terrors.png'))
        inputs['Team'].setItemIcon(3, qtg.QIcon(':/teams/blue_crew.png'))

        app = qtw.QApplication.instance()
        palette = app.palette()
        palette.setColor(qtg.QPalette.Button, qtg.QColor('#333'))
        palette.setColor(qtg.QPalette.ButtonText, qtg.QColor('#3F3'))
        self.submit.setPalette(palette)
        self.cancel.setPalette(palette)

        dotted_brush = qtg.QBrush(qtg.QColor('white'), qtc.Qt.Dense2Pattern)

        gradient = qtg.QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, qtg.QColor('navy'))
        gradient.setColorAt(0.5, qtg.QColor('darkred'))
        gradient.setColorAt(1, qtg.QColor('orange'))
        gradient_brush = qtg.QBrush(gradient)

        window_palette = app.palette()
        window_palette.setBrush(qtg.QPalette.Window, gradient_brush)
        window_palette.setBrush(qtg.QPalette.Active, qtg.QPalette.WindowText, dotted_brush)
        self.setPalette(window_palette)

        stylesheet = """
        QMainWindow {background-color: black;}
        QWidget {background-color: transparent;color: #3F3;}
        QLineEdit, QComboBox, QCheckBox {font-size: 16pt;}"""
        stylesheet += """
        QPushButton {background-color: #333;}
        QCheckBox::indicator:unchecked {border: 1px solid silver; background-color: darkred;}
        QCheckBox::indicator:checked {border: 1px solid silver; background-color: #3F3;}"""
        stylesheet += """
        .QWidget {background: url(Mastering-GUI-Programming-with-Python/Chapter06/tile.png);}"""    # . select specific class, but not subclass
        self.setStyleSheet(stylesheet)

        self.submit.setObjectName('SubmitButton')
        stylesheet += """
        #SubmitButton:disabled {background-color: #888;color: darkred;}"""

        for inp in ('Server', 'Name', 'Password'):
            inp_widget = inputs[inp]
            inp_widget.setStyleSheet('background-color: black')

        # End main UI code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())