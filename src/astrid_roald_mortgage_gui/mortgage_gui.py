import sys
import datetime

from PySide2 import QtWidgets
# from PySide2 import QtCore, QtGui

from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost_with_top_loan, calculate_cost_while_saving,\
    get_monthly_interest_from_yearly, calculate_cost_while_saving_with_bsu_as_security
from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input
from astrid_roald_mortgage_gui.matplotlib_widget import MyMplCanvas


class MortgagePlotter(QtWidgets.QDialog):
    def __init__(self, input_dict, parent=None):
        super(MortgagePlotter, self).__init__(parent)
        # Set start and ending date for calculation
        self.starting_date = input_dict['date of creation']
        self.ending_date = QtWidgets.QDateEdit()
        self.ending_date.setDate(self.starting_date+datetime.timedelta(days=360*7.5))

        # Create widgets
        self.button = QtWidgets.QPushButton("Save current cost calculation")
        self.value_widgets = {k: QtWidgets.QLineEdit(str(v)) for k, v in input_dict.items()}
        self.cost_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        self.debt_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        self.cur_lines = [None, None]
        self.use_bsu_check_box = QtWidgets.QCheckBox('Use BSU as security')
        self.use_toploan = QtWidgets.QCheckBox('Take out toploan')

        # Create layout and add widgets
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        top_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(top_layout)

        graphs_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(graphs_layout)

        top_left_layout = QtWidgets.QVBoxLayout()
        top_layout.addLayout(top_left_layout)

        input_data_layout = QtWidgets.QFormLayout()
        top_left_layout.addLayout(input_data_layout)

        options_layout = QtWidgets.QGridLayout()
        top_layout.addLayout(options_layout)

        graphs_layout.addWidget(self.cost_canvas)
        graphs_layout.addWidget(self.debt_canvas)

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

        for i, widget in enumerate([self.ending_date, self.use_bsu_check_box,
                                    self.use_toploan, self.button]):
            options_layout.addWidget(widget, i, 0)

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
        # 'top loan monthly interest': (1 + (float(self.value_widgets['top loan interest percentage'].text())
        #                                    / 100)) ** (1 / 12) - 1,
        # 'mortgage monthly interest': (1 + (float(self.value_widgets['mortgage interest percentage'].text())
        #                                    / 100)) ** (1 / 12) - 1}

    def set_legend_labels(self):
        label = f"d: {self.mortgage_date.date().toString('yyyy/MM/dd')}, " \
            f"h: {self.value_widgets['housing money'].text()}, " \
            f"g: {self.value_widgets['mortgage goal'].text()}, " \
            f"t%: {self.value_widgets['top loan interest percentage'].text()}, " \
            f"m%: {self.value_widgets['mortgage interest percentage'].text()}, " \
            f"{'BSU security' if bool(self.use_bsu_check_box.checkState()) else 'BSU popped'}, " \
            f"{'Toploan' if bool(self.use_toploan.checkState()) else ''}"
        self.cur_lines[0].set_label(label)
        self.cur_lines[1].set_label(label)
        self.cost_canvas.axes.legend()
        self.debt_canvas.axes.legend()

    def redraw_canvasses(self):
        self.set_legend_labels()
        for canvas in [self.cost_canvas, self.debt_canvas]:
            canvas.axes.relim()
            canvas.axes.autoscale_view()
            canvas.draw()

    def add_cost_line(self):
        time, cost_list, total_debt = self.get_cost()
        self.cost_canvas.axes.plot(time, cost_list)
        self.cur_lines[0] = self.cost_canvas.axes.lines[-1]
        self.debt_canvas.axes.plot(time, total_debt)
        self.cur_lines[1] = self.debt_canvas.axes.lines[-1]
        self.redraw_canvasses()

    def change_current_cost_line(self):
        time, cost_list, total_debt = self.get_cost()
        self.cur_lines[0].set_xdata(time)
        self.cur_lines[0].set_ydata(cost_list)
        self.cur_lines[1].set_xdata(time)
        self.cur_lines[1].set_ydata(total_debt)
        self.redraw_canvasses()

    def get_cost(self):
        number_of_months = round((self.ending_date.date().toPython() - self.starting_date.date()).days / 365 * 12)
        if bool(self.use_bsu_check_box.checkState()):
            if bool(self.use_toploan.checkState()):
                raise RuntimeError('Method not yet implemented')
            else:
                return calculate_cost_while_saving_with_bsu_as_security(number_of_months, self.get_current_values())
        else:
            if bool(self.use_toploan.checkState()):
                return calculate_cost_with_top_loan(number_of_months, self.get_current_values())
            else:
                return calculate_cost_while_saving(number_of_months, self.get_current_values())


def run_app():
    app = QtWidgets.QApplication([])
    # from astrid_roald_mortgage_gui.mortgage_functions import example_input
    # widget = MortgagePlotter(example_input)
    widget = MortgagePlotter(astrid_roald_input)
    widget.resize(1200, 980)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
