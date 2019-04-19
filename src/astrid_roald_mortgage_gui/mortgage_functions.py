import copy
import datetime


class Person():
    def __init__(self, birth_date, name, housing_money, bsu, bsu2, bsu_left_to_fill, bsu2_left_to_fill):
        self.birth_date = birth_date
        self.name = name
        self.housing_money = housing_money
        self.bsu = bsu
        self.bsu2 = bsu2
        self.bsu_left_to_fill = bsu_left_to_fill
        self.bsu2_left_to_fill = bsu2_left_to_fill


class AnalysisStartValues():
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


def get_monthly_interest_from_yearly(yearly_interest_percentage: float) -> float:
    return (1+(yearly_interest_percentage/100))**(1/12)-1


class SavingsSimulation():
    def __init__(self, analysis_variables, analysis_start_values: AnalysisStartValues):
        self.mortgage_goal = analysis_variables.mortgage_goal
        self.mortgage = 0
        self.top_loan = 0

        self.rent = analysis_start_values.rent
        self.regular_savings = analysis_start_values.deposit

        self.persons = {person.name: copy.deepcopy(person) for person in analysis_start_values.persons}
        for name, person in self.persons.items():
            person.housing_money = float(analysis_variables.housing_money_widgets[name].text())
        self.total_housing_money = analysis_variables.total_housing_money

        self.bsu_interest = get_monthly_interest_from_yearly(analysis_start_values.bsu_interest_percentage)
        self.mortgage_interest = get_monthly_interest_from_yearly(analysis_variables.mortgage_interest_percentage)
        self.top_loan_interest = get_monthly_interest_from_yearly(analysis_variables.top_loan_interest_percentage)

    def get_total_bsu_value(self):
        return sum(person.bsu + person.bsu2 for person in self.persons.values())

    def get_bsu_interest_for_one_month(self, interest_so_far):
        return interest_so_far + ((self.get_total_bsu_value() + interest_so_far) * self.bsu_interest)

    def get_bsu_interest_for_several_months(self, months):
        return self.get_total_bsu_value() * ((1 + self.bsu_interest) ** months - 1)

    def get_month_cost(self, got_mortgage, this_months_money):
        if got_mortgage:
            interest_cost = self.mortgage * self.mortgage_interest + self.top_loan * self.top_loan_interest
            for name, month_money in list(this_months_money.items()):
                this_months_money[name] = month_money - interest_cost * month_money / self.total_housing_money
            return interest_cost, this_months_money
        else:
            for name, month_money in list(this_months_money.items()):
                this_months_money[name] = month_money - self.rent / len(this_months_money)
            return self.rent, this_months_money

    def top_up_bsus(self, this_months_money):
        for name, month_money in list(this_months_money.items()):
            if self.persons[name].bsu_left_to_fill > 0:
                this_months_money[name], self.persons[name].bsu, self.persons[name].bsu_left_to_fill = \
                    self.do_bsu_fill(month_money, self.persons[name].bsu, self.persons[name].bsu_left_to_fill)
            if self.persons[name].bsu2_left_to_fill > 0:
                this_months_money[name], self.persons[name].bsu2, self.persons[name].bsu2_left_to_fill = \
                    self.do_bsu_fill(month_money, self.persons[name].bsu2, self.persons[name].bsu2_left_to_fill)
        return this_months_money

    @staticmethod
    def do_bsu_fill(month_leftover_money, bsu, bsu_left_to_fill):
        if bsu_left_to_fill - month_leftover_money > 0:
            bsu += month_leftover_money
            bsu_left_to_fill -= month_leftover_money
            month_leftover_money = 0
        else:
            bsu += bsu_left_to_fill
            month_leftover_money -= bsu_left_to_fill
            bsu_left_to_fill = 0
        return month_leftover_money, bsu, bsu_left_to_fill

    def empty_savings(self):
        total_savings = self.get_total_bsu_value() + self.regular_savings
        for name in list(self.persons.keys()):
            self.persons[name].bsu2 = 0
            self.persons[name].bsu = 0
        self.regular_savings = 0
        return total_savings

    def start_mortgage(self, use_bsu_as_security):
        if use_bsu_as_security:
            security = self.mortgage_goal + self.get_total_bsu_value()
            self.mortgage = min(security * .85, self.mortgage_goal - self.regular_savings)
            self.top_loan = max(self.mortgage_goal - self.regular_savings - security * .85, 0)
            self.regular_savings = 0
        else:
            security = self.mortgage_goal
            savings = self.empty_savings()
            self.mortgage = min(security * .85, self.mortgage_goal - savings)
            self.top_loan = max(self.mortgage_goal - savings - security * .85, 0)

    def pay_down_debt(self, this_months_money):
        combined_money = sum(this_months_money.values())
        if self.top_loan > combined_money:
            self.top_loan -= combined_money
        elif self.top_loan <= combined_money and self.top_loan != 0:
            self.mortgage += self.top_loan - combined_money
            self.top_loan = 0
        elif self.mortgage > combined_money:
            self.mortgage -= combined_money
        elif self.mortgage <= combined_money and self.mortgage != 0:
            self.mortgage = 0
        else:
            self.regular_savings += combined_money

    def new_bsu_year(self):
        bsu_tax_rebate = sum(25000 - person.bsu_left_to_fill for person in self.persons.values() if person.bsu > 0)
        for name in list(self.persons.keys()):
            self.persons[name].bsu_left_to_fill = 25000
            self.persons[name].bsu2_left_to_fill = 25000
        return bsu_tax_rebate * .2


def date_range(start_date, months):
    if start_date.day > 28:
        raise ValueError('This date cannot be consistently increased with one month since the day is more than 28')
    for n in range(1, months):
        yield datetime.date(start_date.year + int((start_date.month + n - 1) / 12),
                                (start_date.month + n - 1) % 12 + 1, start_date.day)


def calculate_cost(number_of_months, analysis_variables, analysis_start_values: AnalysisStartValues):
    saving_simulation = SavingsSimulation(analysis_variables, analysis_start_values)
    cumulative_cost, total_debt, time = [0], [0], [analysis_start_values.simulation_start_date]
    bsu_interest_this_year = saving_simulation.get_bsu_interest_for_several_months(time[0].month)
    started_mortgage = False

    for pay_date in date_range(analysis_start_values.simulation_start_date, number_of_months):
        if pay_date.month == 1:
            bsu_tax_rebate = saving_simulation.new_bsu_year()
            cumulative_cost[-1] = cumulative_cost[-1]-bsu_interest_this_year - bsu_tax_rebate
            bsu_interest_this_year = 0
        else:
            bsu_interest_this_year = saving_simulation.get_bsu_interest_for_one_month(bsu_interest_this_year)
        this_months_money = {name: person.housing_money for name, person in saving_simulation.persons.items()}
        time.append(pay_date)

        this_months_cost, this_months_money = saving_simulation.get_month_cost(started_mortgage, this_months_money)
        cumulative_cost.append(this_months_cost + cumulative_cost[-1])

        # If saving, save up the money in the regular savings, otherwise pay down mortgage
        if pay_date < analysis_variables.mortgage_date_widget.date().toPython():
            this_months_money = saving_simulation.top_up_bsus(this_months_money)
            saving_simulation.regular_savings += sum(this_months_money.values())
            total_debt.append(0)
        else:
            if not started_mortgage:
                saving_simulation.start_mortgage(analysis_variables.use_bsu_as_security)
                started_mortgage = True
                top_loan = saving_simulation.top_loan
            if analysis_variables.use_bsu_as_security:
                this_months_money = saving_simulation.top_up_bsus(this_months_money)
            saving_simulation.pay_down_debt(this_months_money)
            total_debt.append(saving_simulation.mortgage + saving_simulation.top_loan)
    return time, cumulative_cost, total_debt, top_loan


def main():
    pass


if __name__ == '__main__':
    main()
