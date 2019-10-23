import datetime


class Person:
    def __init__(self, birth_date, name, housing_money, bsu, bsu2, bsu_left_to_fill, bsu2_left_to_fill):
        self.birth_date = birth_date
        self.name = name
        self.housing_money = housing_money
        self.bsu = bsu
        self.bsu_active = True
        self.bsu2 = bsu2
        self.bsu2_active = True
        self.bsu_left_to_fill = bsu_left_to_fill
        self.maximum_bsu_left_to_fill_this_year = 25000
        self.bsu2_left_to_fill = bsu2_left_to_fill


class AnalysisStartValues:
    def __init__(self, persons, simulation_start_date, rent,
                 property_value, top_loan_interest_percentage, mortgage_interest_percentage):
        self.persons = persons
        self.simulation_start_date = simulation_start_date
        self.rent = rent
        self.deposit = 3*rent
        self.bsu_interest_percentage = 3.75
        self.property_value = property_value
        self.top_loan_interest_percentage = top_loan_interest_percentage
        self.mortgage_interest_percentage = mortgage_interest_percentage


class AnalysisVariables:
    def __init__(self, total_housing_money, pop_bsu, pop_bsu2, mortgage_date, property_value,
                 top_loan_interest_percentage, mortgage_interest_percentage, housing_money):
        self.total_housing_money = total_housing_money
        self.pop_bsu = pop_bsu
        self.pop_bsu2 = pop_bsu2
        self.mortgage_date = mortgage_date
        self.property_value = property_value
        self.top_loan_interest_percentage = top_loan_interest_percentage
        self.mortgage_interest_percentage = mortgage_interest_percentage
        self.housing_money = housing_money
