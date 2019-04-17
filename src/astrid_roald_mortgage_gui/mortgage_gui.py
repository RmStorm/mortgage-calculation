import sys
import datetime

from PySide2 import QtWidgets, QtCharts
# from PySide2 import QtCore, QtGui

from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost_with_top_loan, example_input
from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input
from astrid_roald_mortgage_gui.matplotlib_widget import MyMplCanvas

class Mortgage_plotter(QtWidgets.QDialog):
    def __init__(self, input_dict, parent=None):
        super(Mortgage_plotter, self).__init__(parent)
        # Create widgets
        self.button = QtWidgets.QPushButton("Calculate mortgage costs")
        self.edit_widgets = {k: QtWidgets.QLineEdit(str(v)) for k, v in input_dict.items()}

        self.chart_view = QtCharts.QtCharts.QChartView()
        self.chart_view.chart().createDefaultAxes()
        self.mpl_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        self.check_box = QtWidgets.QCheckBox('sometext')

        # Create layout and add widgets
        layout = QtWidgets.QVBoxLayout()
        input_layout = QtWidgets.QHBoxLayout()
        raw_data_layout = QtWidgets.QFormLayout()
        for k, v in self.edit_widgets.items():
            if k == 'date of creation':
                print(input_dict[k])
                raw_data_layout.addWidget(QtWidgets.QLabel(str(input_dict[k])))
                raw_data_layout.addRow('mortgage date', v)
            else:
                raw_data_layout.addRow(k, v)
        options_layout = QtWidgets.QGridLayout()
        options_layout.addWidget(self.check_box, 0, 0)
        input_layout.addLayout(raw_data_layout)
        input_layout.addLayout(options_layout)
        layout.addLayout(input_layout)
        layout.addWidget(self.button)
        layout.addWidget(self.mpl_canvas)

        # Set layout into widget
        self.setLayout(layout)

        self.button.clicked.connect(self.add_cost_line)
        self.add_cost_line()

    def add_cost_line(self):
        cost_list = calculate_cost_with_top_loan(100, float(self.edit_widgets['housing money'].text()),
                                                 float(self.edit_widgets['mortgage goal'].text()) * .85,
                                                 float(self.edit_widgets['mortgage goal'].text()) * .15,
                                                 float(self.edit_widgets['mortgage interest percentage'].text()),
                                                 float(self.edit_widgets['top loan interest percentage'].text()))

        self.mpl_canvas.axes.plot(range(len(cost_list)), cost_list)
        self.mpl_canvas.draw()


def run_app():
    app = QtWidgets.QApplication([])
    # widget = Mortgage_plotter(example_input)
    widget = Mortgage_plotter(astrid_roald_input)
    widget.resize(800, 700)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
