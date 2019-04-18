import sys
import datetime

from PySide2 import QtWidgets
# from PySide2 import QtCore, QtGui

from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost_with_top_loan, calculate_cost_while_saving,\
    get_monthly_interest_from_yearly
from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input
from astrid_roald_mortgage_gui.matplotlib_widget import MyMplCanvas


class MortgagePlotter(QtWidgets.QDialog):
    def __init__(self, input_dict, parent=None):
        super(MortgagePlotter, self).__init__(parent)
        # Set start and ending date for calculation
        self.starting_date = input_dict['date of creation']
        self.ending_date = QtWidgets.QDateEdit()
        self.ending_date.setDate(self.starting_date+datetime.timedelta(days=360*5.5))

        # Create widgets
        self.button = QtWidgets.QPushButton("Save current cost calculation")
        self.value_widgets = {k: QtWidgets.QLineEdit(str(v)) for k, v in input_dict.items()}
        self.mpl_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        self.cur_line = None
        self.use_bsu_check_box = QtWidgets.QCheckBox('Use BSU as security')
        self.use_toploan = QtWidgets.QCheckBox('Take out toploan')

        # Create layout and add widgets
        layout = QtWidgets.QVBoxLayout()
        top_layout = QtWidgets.QHBoxLayout()
        top_left_layout = QtWidgets.QVBoxLayout()
        input_data_layout = QtWidgets.QFormLayout()
        for k, v in self.value_widgets.items():
            if k == 'date of creation':
                top_left_layout.addWidget(QtWidgets.QLabel(
                    f'The starting date for the input data is {self.starting_date}'))
                self.mortgage_date = QtWidgets.QDateEdit()
                self.mortgage_date.setDate(input_dict[k]+datetime.timedelta(days=65))

                input_data_layout.addRow('mortgage date', self.mortgage_date)
            elif k in ['rent per month', 'deposit', 'bsu savings', 'bsu2 savings']:
                top_left_layout.addWidget(QtWidgets.QLabel(
                    f'The value for {k} at the starting date is {input_dict[k]} NOK'))
            elif k in ['mortgage goal', 'housing money',
                       'top loan interest percentage', 'mortgage interest percentage']:
                input_data_layout.addRow(k, v)
                v.textChanged.connect(self.change_current_cost_line)
            else:
                raise KeyError(f'Unaccounted for key in input_dict: {k}')

        options_layout = QtWidgets.QGridLayout()
        for i, widget in enumerate([self.ending_date, self.use_bsu_check_box,
                                    self.use_toploan, self.button]):
            options_layout.addWidget(widget, i, 0)
        top_left_layout.addLayout(input_data_layout)
        top_layout.addLayout(top_left_layout)
        top_layout.addLayout(options_layout)
        layout.addLayout(top_layout)
        layout.addWidget(self.mpl_canvas)
        self.setLayout(layout)

        # Connect callbacks
        self.button.clicked.connect(self.add_cost_line)
        for callback in [self.mortgage_date.dateChanged, self.ending_date.dateChanged,
                         self.use_bsu_check_box.stateChanged, self.use_toploan.stateChanged]:
            callback.connect(self.change_current_cost_line)
        self.add_cost_line()

    def get_current_values(self):
        return {'starting date': self.starting_date,
                'rent per month': float(self.value_widgets['rent per month'].text()),
                'deposit': float(self.value_widgets['deposit'].text()),
                'bsu savings': float(self.value_widgets['bsu savings'].text()),
                'bsu2 savings': float(self.value_widgets['bsu2 savings'].text()),
                'mortgage date': self.mortgage_date.date().toPython(),
                'mortgage goal': float(self.value_widgets['mortgage goal'].text()),
                'housing money': float(self.value_widgets['housing money'].text()),
                'top loan monthly interest': get_monthly_interest_from_yearly(float(
                    self.value_widgets['top loan interest percentage'].text())),
                'mortgage monthly interest': get_monthly_interest_from_yearly(float(
                    self.value_widgets['mortgage interest percentage'].text()))}

    def set_cost_line_label(self):
        self.cur_line.set_label(f"d: {self.mortgage_date.date().toString('yyyy/MM/dd')}, "
                                f"h: {self.value_widgets['housing money'].text()}, "
                                f"g: {self.value_widgets['mortgage goal'].text()}, "
                                f"t%: {self.value_widgets['top loan interest percentage'].text()}, "
                                f"m%: {self.value_widgets['mortgage interest percentage'].text()}, "
                                f"BSU: {bool(self.use_bsu_check_box.checkState())}, "
                                f"Top: {bool(self.use_toploan.checkState())}")
        self.mpl_canvas.axes.legend()

    def add_cost_line(self):
        time, cost_list = self.get_cost()
        self.mpl_canvas.axes.plot(time, cost_list)
        self.cur_line = self.mpl_canvas.axes.lines[-1]
        self.set_cost_line_label()

        self.mpl_canvas.draw()

    def change_current_cost_line(self):
        time, cost_list = self.get_cost()
        self.cur_line.set_ydata(cost_list)
        self.cur_line.set_xdata(time)
        self.set_cost_line_label()
        self.mpl_canvas.axes.relim()
        self.mpl_canvas.axes.autoscale_view()

        self.mpl_canvas.draw()

    def get_cost(self):
        number_of_months = round((self.ending_date.date().toPython() - self.starting_date.date()).days / 365 * 12)
        if bool(self.use_toploan.checkState()):
            return calculate_cost_with_top_loan(number_of_months, self.get_current_values())
        else:
            return calculate_cost_while_saving(number_of_months, self.get_current_values())


def run_app():
    app = QtWidgets.QApplication([])
    # from astrid_roald_mortgage_gui.mortgage_functions import example_input
    # widget = MortgagePlotter(example_input)
    widget = MortgagePlotter(astrid_roald_input)
    widget.resize(1200, 900)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
