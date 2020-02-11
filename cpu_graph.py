import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from collections import deque
from psutil import cpu_percent


class GraphWidget(qtw.QWidget):
    """A widget to display a running graph of information"""
    crit_color = qtg.QColor(255, 0, 0)  # red
    warn_color = qtg.QColor(255, 255, 0)  # yellow
    good_color = qtg.QColor(0, 255, 0)  # green

    def __init__(self, *args, data_width=20, minimum=0, maximum=100, warn_val=50, crit_val=75, scale=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.minimum = minimum
        self.maximum = maximum
        self.warn_val = warn_val
        self.scale = scale
        self.crit_val = crit_val
        self.values = deque([self.minimum] * data_width, maxlen=data_width)
        self.setFixedWidth(data_width * scale)

    def add_value(self, value):
        value = max(value, self.minimum)
        value = min(value, self.maximum)
        self.values.append(value)
        self.update()

    def paintEvent(self, paint_event):  # Overwrite default
        painter = qtg.QPainter(self)

        brush = qtg.QBrush(qtg.QColor(48, 48, 48))
        painter.setBrush(brush)
        painter.drawRect(0, 0, self.width(), self.height())

        pen = qtg.QPen()
        pen.setDashPattern([1, 0])
        warn_y = self.val_to_y(self.warn_val)
        pen.setColor(self.warn_color)
        painter.setPen(pen)
        painter.drawLine(0, warn_y, self.width(), warn_y)

        crit_y = self.val_to_y(self.crit_val)
        pen.setColor(self.crit_color)
        painter.setPen(pen)
        painter.drawLine(0, crit_y, self.width(), crit_y)

        gradient = qtg.QLinearGradient(qtc.QPointF(0, self.height()), qtc.QPointF(0, 0))
        gradient.setColorAt(0, self.good_color)
        gradient.setColorAt(self.warn_val / (self.maximum - self.minimum), self.warn_color)
        gradient.setColorAt(self.crit_val / (self.maximum - self.minimum), self.crit_color)

        brush = qtg.QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(qtc.Qt.NoPen)

        self.start_value = getattr(self, 'start_value', self.minimum)
        last_value = self.start_value
        self.start_value = self.values[0]
        for indx, value in enumerate(self.values):
            x = (indx + 1) * self.scale
            last_x = indx * self.scale
            y = self.val_to_y(value)
            last_y = self.val_to_y(last_value)
            path = qtg.QPainterPath()
            path.moveTo(x, self.height())
            path.lineTo(last_x, self.height())
            path.lineTo(last_x, last_y)
            # path.lineTo(x, y)
            c_x = round(self.scale * .5) + last_x
            c1 = (c_x, last_y)
            c2 = (c_x, y)
            path.cubicTo(*c1, *c2, x, y)
            painter.drawPath(path)
            last_value = value


    def val_to_y(self, value):
        data_range = self.maximum - self.minimum
        value_fraction = value / data_range
        y_offset = round(value_fraction * self.height())
        y = self.height() - y_offset
        return y


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here
        self.graph = GraphWidget(self)
        self.setCentralWidget(self.graph)

        self.timer = qtc.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start()
        # End main UI code
        self.show()

    def update_graph(self):
        cpu_usage = cpu_percent()
        self.graph.add_value(cpu_usage)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())