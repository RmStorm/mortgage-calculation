import sys
import datetime

import matplotlib
from PySide2 import QtWidgets, QtCharts
# from PySide2 import QtCore, QtGui

from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost_with_top_loan, example_input
from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input
from astrid_roald_mortgage_gui.matplotlib_widget import MyMplCanvas

class Mortgage_plotter(QtWidgets.QDialog):
    def __init__(self, input_dict, parent=None):
        super(Mortgage_plotter, self).__init__(parent)
        # Create widgets
        self.button = QtWidgets.QPushButton("Save current cost calculation")
        self.edit_widgets = {k: QtWidgets.QLineEdit(str(v)) for k, v in input_dict.items()}
        self.mpl_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        self.check_box = QtWidgets.QCheckBox('sometext')

        # Create layout and add widgets
        layout = QtWidgets.QVBoxLayout()
        input_layout = QtWidgets.QHBoxLayout()
        raw_data_layout = QtWidgets.QVBoxLayout()
        raw_data_fields_layout = QtWidgets.QFormLayout()
        for k, v in self.edit_widgets.items():
            if k == 'date of creation':
                print(input_dict[k])
                raw_data_layout.addWidget(QtWidgets.QLabel(f'The starting date for the input data is {input_dict[k]}'))
                self.date_widget = QtWidgets.QDateEdit()
                self.date_widget.setDate(input_dict[k])

                raw_data_fields_layout.addRow('mortgage date', self.date_widget)
            elif k in ['rent per month', 'deposit', 'total savings']:
                raw_data_layout.addWidget(QtWidgets.QLabel(f'The value for {k} at the starting date is {input_dict[k]}'))
            elif k in ['mortgage goal', 'housing money',
                       'top loan interest percentage', 'mortgage interest percentage']:
                raw_data_fields_layout.addRow(k, v)
                v.textChanged.connect(self.change_current_cost_line)
            else:
                raise KeyError(f'Unaccounted for key in input_dict: {k}')

        options_layout = QtWidgets.QGridLayout()
        options_layout.addWidget(self.check_box, 0, 0)
        raw_data_layout.addLayout(raw_data_fields_layout)
        input_layout.addLayout(raw_data_layout)
        input_layout.addLayout(options_layout)
        layout.addLayout(input_layout)
        layout.addWidget(self.button)
        layout.addWidget(self.mpl_canvas)

        # Set layout into widget
        self.setLayout(layout)

        self.button.clicked.connect(self.add_cost_line)
        self.date_widget.dateChanged.connect(self.change_current_cost_line)
        self.add_cost_line()

    def set_cost_line_label(self):
        self.cur_line.set_label(f"d: {self.date_widget.date().toString('yyyy/MM/dd')}, "
                                f"h: {self.edit_widgets['housing money'].text()}, "
                                f"g: {self.edit_widgets['mortgage goal'].text()}, "
                                f"t%: {self.edit_widgets['top loan interest percentage'].text()}, "
                                f"m%: {self.edit_widgets['mortgage interest percentage'].text()}, ")
        self.mpl_canvas.axes.legend()
        pass

    def add_cost_line(self):
        cost_list = self.get_cost_list()
        self.mpl_canvas.axes.plot(range(len(cost_list)), cost_list)
        self.cur_line = self.mpl_canvas.axes.lines[-1]
        self.set_cost_line_label()

        self.mpl_canvas.draw()

    def change_current_cost_line(self):
        cost_list = self.get_cost_list()
        print('setting new info')
        self.cur_line.set_ydata(cost_list)
        self.cur_line.set_xdata(range(len(cost_list)))
        self.set_cost_line_label()
        self.mpl_canvas.axes.relim()
        self.mpl_canvas.axes.autoscale_view()

        self.mpl_canvas.draw()


    def get_cost_list(self):
        try:
            return calculate_cost_with_top_loan(100, float(self.edit_widgets['housing money'].text()),
                                                float(self.edit_widgets['mortgage goal'].text()) * .85,
                                                float(self.edit_widgets['mortgage goal'].text()) * .15,
                                                float(self.edit_widgets['mortgage interest percentage'].text()),
                                                float(self.edit_widgets['top loan interest percentage'].text()))
        except Exception:
            print('Fill in some valid values')

def run_app():
    app = QtWidgets.QApplication([])
    widget = Mortgage_plotter(example_input)
    # widget = Mortgage_plotter(astrid_roald_input)
    widget.resize(1200, 900)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
