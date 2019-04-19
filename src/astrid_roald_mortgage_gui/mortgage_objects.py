import datetime


class Person:
    def __init__(self, birth_date, name, housing_money, bsu, bsu2, bsu_left_to_fill, bsu2_left_to_fill):
        self.birth_date = birth_date
        self.name = name
        self.housing_money = housing_money
        self.bsu = bsu
        self.bsu2 = bsu2
        self.bsu_left_to_fill = bsu_left_to_fill
        self.maximum_bsu_left_to_fill = 25000
        self.bsu2_left_to_fill = bsu2_left_to_fill


class AnalysisStartValues:
    def __init__(self, persons, simulation_start_date, rent,
                 mortgage_goal, top_loan_interest_percentage, mortgage_interest_percentage):
        self.persons = persons
        self.simulation_start_date = simulation_start_date
        self.rent = rent
        self.deposit = 3*rent
        self.bsu_interest_percentage = 3.6
        self.mortgage_goal = mortgage_goal
        self.top_loan_interest_percentage = top_loan_interest_percentage
        self.mortgage_interest_percentage = mortgage_interest_percentage


example_input = AnalysisStartValues([Person(datetime.date(1990, 1, 1), 'p1', 1000, 1000, 500, 1000, 1500),
                                     Person(datetime.date(1990, 1, 1), 'p2', 1200, 1000, 1000, 0, 0)],
                                    datetime.date(2019, 3, 20), 1000, 200000, 10, 1)


class AnalysisVariables:
    def __init__(self, widgets):
        self.total_housing_money = sum(float(widget.text()) for widget in widgets.housing_money_widgets.values())
        self.use_bsu_as_security = bool(widgets.use_bsu_as_security_widget.checkState())
        self.mortgage_date = widgets.mortgage_date_widget.date().toPython()
        self.mortgage_goal = float(widgets.mortgage_goal_widget.text())
        self.top_loan_interest_percentage = float(widgets.top_loan_interest_percentage_widget.text())
        self.mortgage_interest_percentage = float(widgets.mortgage_interest_percentage_widget.text())
        self.housing_money = {name: float(widget.text()) for name, widget in widgets.housing_money_widgets.items()}
