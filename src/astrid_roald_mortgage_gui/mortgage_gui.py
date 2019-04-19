import sys
import datetime

from PySide2 import QtWidgets
# from PySide2 import QtCore, QtGui

from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost, AnalysisStartValues
from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input
from astrid_roald_mortgage_gui.matplotlib_widget import MyMplCanvas


class AnalysisVariables():
    def __init__(self, analysis_start_values: AnalysisStartValues, callback, input_data_layout,
                 use_bsu_as_security_widget, mortgage_date_widget):
        self.housing_money_widgets = {}

        self.use_bsu_as_security_widget = use_bsu_as_security_widget
        self.use_bsu_as_security_widget.stateChanged.connect(callback)
        self.mortgage_date_widget = mortgage_date_widget
        self.mortgage_date_widget.setDate(analysis_start_values.simulation_start_date + datetime.timedelta(days=73))
        self.mortgage_date_widget.dateChanged.connect(callback)
        input_data_layout.addRow('mortgage date', self.mortgage_date_widget)

        for person in analysis_start_values.persons:
            widget = QtWidgets.QLineEdit(str(person.housing_money))
            widget.textChanged.connect(callback)
            self.housing_money_widgets[person.name] = widget
            input_data_layout.addRow(f'Housing money {person.name}', widget)

        for field in ['mortgage_goal', 'top_loan_interest_percentage', 'mortgage_interest_percentage']:
            widget = QtWidgets.QLineEdit(str(getattr(analysis_start_values, field)))
            setattr(self, f'{field}_widget', widget)
            widget.textChanged.connect(callback)
            input_data_layout.addRow(field.replace('_', ' '), getattr(self, f'{field}_widget'))

    @property
    def total_housing_money(self):
        return sum(float(widget.text()) for widget in self.housing_money_widgets.values())

    @property
    def use_bsu_as_security(self):
        return bool(self.use_bsu_as_security_widget.checkState())

    @property
    def mortgage_date(self):
        return self.mortgage_date_widget.date().toPython()

    @property
    def mortgage_goal(self):
        return float(self.mortgage_goal_widget.text())

    @property
    def top_loan_interest_percentage(self):
        return float(self.top_loan_interest_percentage_widget.text())

    @property
    def mortgage_interest_percentage(self):
        return float(self.mortgage_interest_percentage_widget.text())


class MortgagePlotter(QtWidgets.QDialog):
    def __init__(self, analysis_start_values: AnalysisStartValues, parent=None):
        super(MortgagePlotter, self).__init__(parent)
        # Set start and ending date for calculation
        self.analysis_start_values = analysis_start_values
        self.starting_date = self.analysis_start_values.simulation_start_date
        self.ending_date = QtWidgets.QDateEdit()
        self.ending_date.setDate(self.starting_date + datetime.timedelta(days=360*7.5))
        self.ending_date.dateChanged.connect(self.change_current_cost_line)

        # Create layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        top_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(top_layout)

        graphs_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(graphs_layout)

        static_info_layout = QtWidgets.QVBoxLayout()
        top_layout.addLayout(static_info_layout)

        input_data_layout = QtWidgets.QFormLayout()

        options_layout = QtWidgets.QGridLayout()
        top_layout.addLayout(options_layout)

        # Create widgets and add then to layout
        self.analysis_variables = AnalysisVariables(analysis_start_values, self.change_current_cost_line, input_data_layout,
                                                    QtWidgets.QCheckBox('Use BSU as security'), QtWidgets.QDateEdit())
        self.button = QtWidgets.QPushButton("Save current cost calculation")
        self.button.clicked.connect(self.add_cost_line)

        self.cost_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        self.debt_canvas = MyMplCanvas(width=5, height=4, dpi=100)
        graphs_layout.addWidget(self.cost_canvas)
        graphs_layout.addWidget(self.debt_canvas)

        # Add static info
        bsu_total = sum(person.bsu + person.bsu2 for person in analysis_start_values.persons)
        info_labels = [f'The starting date for the input data is {self.analysis_start_values.simulation_start_date}',
                       f'The value for rent at the starting date is {analysis_start_values.rent} NOK',
                       f'The value for deposit at the starting date is {analysis_start_values.deposit} NOK',
                       f'The total bsu value at the starting date is {bsu_total} NOK']
        [static_info_layout.addWidget(QtWidgets.QLabel(info_label)) for info_label in info_labels]
        static_info_layout.addLayout(input_data_layout)

        for i, widget in enumerate([self.ending_date, self.analysis_variables.use_bsu_as_security_widget, self.button]):
            options_layout.addWidget(widget, i, 0)

        # Do first simulation
        self.cur_lines = [None, None]
        self.add_cost_line()

    def set_legend_labels(self, top_loan):
        label = f"d: {self.analysis_variables.mortgage_date.strftime('%d/%m/%Y')}, " \
            f"h: {self.analysis_variables.total_housing_money}, " \
            f"g: {self.analysis_variables.mortgage_goal}, " \
            f"t%: {self.analysis_variables.top_loan_interest_percentage}, " \
            f"m%: {self.analysis_variables.mortgage_interest_percentage}, " \
            f"{'BSU security' if self.analysis_variables.use_bsu_as_security else 'BSU popped'}, " \
            f"Toploan: {top_loan}"
        self.cur_lines[0].set_label(label)
        self.cur_lines[1].set_label(label)
        self.cost_canvas.axes.legend()
        self.debt_canvas.axes.legend()

    def redraw_canvasses(self):
        for canvas in [self.cost_canvas, self.debt_canvas]:
            canvas.axes.relim()
            canvas.axes.autoscale_view()
            canvas.draw()

    def add_cost_line(self):
        time, cost_list, total_debt, top_loan = self.get_cost()
        self.cost_canvas.axes.plot(time, cost_list)
        self.cur_lines[0] = self.cost_canvas.axes.lines[-1]
        self.debt_canvas.axes.plot(time, total_debt)
        self.cur_lines[1] = self.debt_canvas.axes.lines[-1]
        self.set_legend_labels(top_loan)
        self.redraw_canvasses()

    def change_current_cost_line(self):
        time, cost_list, total_debt, top_loan = self.get_cost()
        self.cur_lines[0].set_xdata(time)
        self.cur_lines[0].set_ydata(cost_list)
        self.cur_lines[1].set_xdata(time)
        self.cur_lines[1].set_ydata(total_debt)
        self.set_legend_labels(top_loan)
        self.redraw_canvasses()

    def get_cost(self):
        # return [0,1], [1,2], [3,1], 100
        number_of_months = round((self.ending_date.date().toPython() - self.starting_date).days / 365 * 12)
        return calculate_cost(number_of_months, self.analysis_variables, self.analysis_start_values)


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
