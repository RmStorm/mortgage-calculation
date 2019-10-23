import copy
import datetime

from astrid_roald_mortgage_gui.mortgage_objects import AnalysisStartValues, AnalysisVariables


def get_monthly_interest_from_yearly(yearly_interest_percentage: float) -> float:
    return (1+(yearly_interest_percentage/100))**(1/12)-1


class SavingsSimulation:
    def __init__(self, analysis_variables: AnalysisVariables, analysis_start_values: AnalysisStartValues):
        self.property_value = analysis_variables.property_value
        self.mortgage = 0
        self.top_loan = 0

        self.rent = analysis_start_values.rent
        self.regular_savings = analysis_start_values.deposit

        self.persons = {person.name: copy.deepcopy(person) for person in analysis_start_values.persons}
        for name, person in self.persons.items():
            person.housing_money = analysis_variables.housing_money[name]
        self.total_housing_money = analysis_variables.total_housing_money

        self.bsu_interest = get_monthly_interest_from_yearly(analysis_start_values.bsu_interest_percentage)
        self.mortgage_interest = get_monthly_interest_from_yearly(analysis_variables.mortgage_interest_percentage)
        self.top_loan_interest = get_monthly_interest_from_yearly(analysis_variables.top_loan_interest_percentage)

    def get_total_bsu_value(self):
        return sum(person.bsu for person in self.persons.values()), sum(person.bsu2 for person in self.persons.values())

    def get_bsu_interest_for_one_month(self, interest_so_far):
        return interest_so_far + ((sum(self.get_total_bsu_value()) + interest_so_far) * self.bsu_interest)

    def get_bsu_interest_for_several_months(self, months):
        return sum(self.get_total_bsu_value()) * ((1 + self.bsu_interest) ** months - 1)

    def get_month_cost(self, got_mortgage, this_months_money):
        if got_mortgage:
            interest_cost = (self.mortgage * self.mortgage_interest + self.top_loan * self.top_loan_interest)*.78
            for name, month_money in list(this_months_money.items()):
                this_months_money[name] = month_money - interest_cost * month_money / self.total_housing_money
            return interest_cost, this_months_money
        else:
            for name, month_money in list(this_months_money.items()):
                this_months_money[name] = month_money - self.rent / len(this_months_money)
            return self.rent, this_months_money

    def top_up_bsus(self, this_months_money):
        for name, month_money in list(this_months_money.items()):
            if self.persons[name].bsu_left_to_fill > 0 and self.persons[name].bsu_active:
                this_months_money[name], self.persons[name].bsu, self.persons[name].bsu_left_to_fill = \
                    self.do_bsu_fill(month_money, self.persons[name].bsu, self.persons[name].bsu_left_to_fill)
            if self.persons[name].bsu2_left_to_fill > 0 and self.persons[name].bsu2_active:
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

    def empty_savings(self, pop_bsu, pop_bsu2):
        spendable_savings = self.regular_savings
        self.regular_savings = 0
        for name in list(self.persons.keys()):
            if pop_bsu:
                spendable_savings += self.persons[name].bsu
                self.persons[name].bsu = 0
                self.persons[name].bsu_active = False
            if pop_bsu2:
                spendable_savings += self.persons[name].bsu2
                self.persons[name].bsu2 = 0
                self.persons[name].bsu2_active = False
        return spendable_savings

    def start_mortgage(self, pop_bsu, pop_bsu2):
        maximum_mortgage = self.property_value * .85 + (0 if pop_bsu else self.get_total_bsu_value()[0])
        spendable_savings = self.empty_savings(pop_bsu, pop_bsu2)
        self.mortgage = min(maximum_mortgage, self.property_value - spendable_savings)
        self.top_loan = max(self.property_value - spendable_savings - maximum_mortgage, 0)


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
        bsu_tax_rebate = {name: (person.maximum_bsu_left_to_fill_this_year - person.bsu_left_to_fill) * .2
                          for name, person in self.persons.items() if person.bsu > 0}
        for name in list(self.persons.keys()):
            if self.persons[name].bsu_active:
                self.persons[name].bsu = self.persons[name].bsu * ((1 + self.bsu_interest) ** 12)
                self.persons[name].bsu_left_to_fill = min(25000, max(300000 - self.persons[name].bsu, 0))
                self.persons[name].maximum_bsu_left_to_fill_this_year = self.persons[name].bsu_left_to_fill
            if self.persons[name].bsu2_active:
                self.persons[name].bsu2 = self.persons[name].bsu2 * ((1 + self.bsu_interest) ** 12)
                self.persons[name].bsu2_left_to_fill = min(25000, max(300000 - self.persons[name].bsu2, 0))
        return bsu_tax_rebate

    def kill_bsus(self, name):
        extra_money = self.persons[name].bsu + self.persons[name].bsu2
        self.persons[name].bsu = 0
        self.persons[name].bsu2 = 0
        self.persons[name].bsu_active = False
        self.persons[name].bsu2_active = False
        return extra_money

    def get_total_wealth(self, started_mortgage):
        savings = self.regular_savings + sum(self.get_total_bsu_value())
        if not started_mortgage:
            return savings
        return savings + self.property_value - self.mortgage - self.top_loan


def date_range(start_date, months):
    if start_date.day > 28:
        raise ValueError('This date cannot be consistently increased with one month since the day is more than 28')
    for n in range(1, months):
        yield datetime.date(start_date.year + int((start_date.month + n - 1) / 12),
                            (start_date.month + n - 1) % 12 + 1, start_date.day)


def calculate_cost(number_of_months, analysis_variables: AnalysisVariables, analysis_start_values: AnalysisStartValues):
    saving_simulation = SavingsSimulation(analysis_variables, analysis_start_values)
    cumulative_cost, total_debt, time = [0], [0], [analysis_start_values.simulation_start_date]
    bsu_interest_this_year = saving_simulation.get_bsu_interest_for_several_months(time[0].month)
    started_mortgage = False
    total_wealth = [saving_simulation.get_total_wealth(started_mortgage)]

    for pay_date in date_range(analysis_start_values.simulation_start_date, number_of_months):
        time.append(pay_date)
        this_months_money = {name: person.housing_money for name, person in saving_simulation.persons.items()}
        this_months_cost, this_months_money = saving_simulation.get_month_cost(started_mortgage, this_months_money)
        cumulative_cost.append(this_months_cost + cumulative_cost[-1])

        if pay_date.month == 1:
            bsu_tax_rebate = saving_simulation.new_bsu_year()
            cumulative_cost[-1] = cumulative_cost[-1] - bsu_interest_this_year - sum(bsu_tax_rebate.values())
            bsu_interest_this_year = 0
            for name, tax_rebate in bsu_tax_rebate.items():
                this_months_money[name] += tax_rebate
        else:
            bsu_interest_this_year = saving_simulation.get_bsu_interest_for_one_month(bsu_interest_this_year)

        for name, person in saving_simulation.persons.items():
            if pay_date - person.birth_date > datetime.timedelta(days=34*365):
                extra_money = saving_simulation.kill_bsus(name)
                this_months_money[name] += extra_money

        # If saving, save up the money in the regular savings, otherwise pay down mortgage
        if pay_date < analysis_variables.mortgage_date:
            this_months_money = saving_simulation.top_up_bsus(this_months_money)
            saving_simulation.regular_savings += sum(this_months_money.values())
            total_debt.append(0)
        else:
            if not started_mortgage:
                saving_simulation.start_mortgage(analysis_variables.pop_bsu, analysis_variables.pop_bsu2)
                started_mortgage = True
                top_loan = saving_simulation.top_loan
            if not all([analysis_variables.pop_bsu, analysis_variables.pop_bsu2]):
                this_months_money = saving_simulation.top_up_bsus(this_months_money)
            saving_simulation.pay_down_debt(this_months_money)
            total_debt.append(saving_simulation.mortgage + saving_simulation.top_loan)
        total_wealth.append(saving_simulation.get_total_wealth(started_mortgage))
    return top_loan, time, cumulative_cost, total_debt, total_wealth


def main():
    pass


if __name__ == '__main__':
    main()
