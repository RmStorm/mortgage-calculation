import sys
import datetime

from PySide2 import QtWidgets

from astrid_roald_mortgage_gui.mortgage_objects import AnalysisVariables, AnalysisStartValues, Person
from astrid_roald_mortgage_gui.mortgage_functions import calculate_cost
# from astrid_roald_mortgage_gui.secrets.astrid_roald_input import astrid_roald_input
from astrid_roald_mortgage_gui.matplotlib_widget import MyMplCanvas


class AnalysisVariableWidgets:
    def __init__(self, analysis_start_values: AnalysisStartValues, callback, input_data_layout):
        self.housing_money_widgets = {}

        self.use_bsu_as_security_widget = QtWidgets.QCheckBox('Use BSU as security')
        self.use_bsu_as_security_widget.stateChanged.connect(callback)
        self.mortgage_date_widget = QtWidgets.QDateEdit()
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


class MortgagePlotter(QtWidgets.QDialog):
    def __init__(self, analysis_start_values: AnalysisStartValues, parent=None):
        super(MortgagePlotter, self).__init__(parent)
        # Set start and ending date for calculation
        self.analysis_start_values = analysis_start_values
        self.starting_date = self.analysis_start_values.simulation_start_date
        self.ending_date = QtWidgets.QDateEdit()
        self.ending_date.setDate(self.starting_date + datetime.timedelta(days=360*12.5))
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
        self.analysis_variable_widgets = AnalysisVariableWidgets(analysis_start_values,
                                                                 self.change_current_cost_line, input_data_layout)
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

        for i, widget in enumerate([self.ending_date, self.analysis_variable_widgets.use_bsu_as_security_widget,
                                    self.button]):
            options_layout.addWidget(widget, i, 0)

        # Do first simulation
        self.cur_lines = [None, None]
        self.add_cost_line()

    def set_legend_labels(self, top_loan):
        analysis_variables = AnalysisVariables(self.analysis_variable_widgets)
        label = f"d: {analysis_variables.mortgage_date.strftime('%d/%m/%Y')}, " \
            f"h: {analysis_variables.total_housing_money}, " \
            f"g: {analysis_variables.mortgage_goal}, " \
            f"t%: {analysis_variables.top_loan_interest_percentage}, " \
            f"m%: {analysis_variables.mortgage_interest_percentage}, " \
            f"{'BSU security' if analysis_variables.use_bsu_as_security else 'BSU popped'}, " \
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
        number_of_months = round((self.ending_date.date().toPython() - self.starting_date).days / 365 * 12)
        return calculate_cost(number_of_months,
                              AnalysisVariables(self.analysis_variable_widgets),
                              self.analysis_start_values)


def run_app():
    app = QtWidgets.QApplication.instance() if QtWidgets.QApplication.instance() else QtWidgets.QApplication([])

    example_input = AnalysisStartValues([Person(datetime.date(1990, 1, 1), 'p1', 10000, 100000, 50000, 25000, 25000),
                                         Person(datetime.date(1990, 1, 1), 'p2', 10000, 100000, 50000, 25000, 25000)],
                                        datetime.date(2019, 1, 1), 15000, 3000000, 10, 4)
    widget = MortgagePlotter(example_input)
    # widget = MortgagePlotter(astrid_roald_input)
    widget.resize(1200, 980)
    widget.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(run_app())
