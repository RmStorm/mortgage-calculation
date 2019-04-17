import sys

from PySide2 import QtWidgets, QtCharts
# from PySide2 import QtCore, QtGui

from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost_with_top_loan, example_input
from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input


class Mortgage_plotter(QtWidgets.QDialog):
    def __init__(self, input_dict, parent=None):
        super(Mortgage_plotter, self).__init__(parent)
        # Create widgets
        self.button = QtWidgets.QPushButton("Plot Graph")
        self.edit_widgets = {k: QtWidgets.QLineEdit(str(v)) for k, v in input_dict.items()}

        self.chart_view = QtCharts.QtCharts.QChartView()
        self.chart_view.chart().createDefaultAxes()

        # Create layout and add widgets
        layout = QtWidgets.QVBoxLayout()
        input_layout = QtWidgets.QFormLayout()
        for k, v in self.edit_widgets.items():
            input_layout.addRow(k, v)
        layout.addLayout(input_layout)
        layout.addWidget(self.button)
        layout.addWidget(self.chart_view)

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
        series = QtCharts.QtCharts.QLineSeries()
        for i, cost in enumerate(cost_list):
            series.append(i, cost)
        self.chart_view.chart().addSeries(series)
        print("Hello something")


def run_app():
    app = QtWidgets.QApplication([])
    # widget = Mortgage_plotter(example_input)
    widget = Mortgage_plotter(astrid_roald_input)
    widget.resize(800, 700)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
