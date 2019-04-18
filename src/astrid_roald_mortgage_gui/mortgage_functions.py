import datetime

example_input = {'date of creation': datetime.datetime(2019, 3, 20),
                 'rent per month': 1000,
                 'housing money': 2000,
                 'deposit': 1000,
                 'bsu savings': 2000,
                 'bsu2 savings': 2000,
                 'mortgage goal': 400000,
                 'top loan interest percentage': 10,
                 'mortgage interest percentage': 1}


def get_monthly_interest_from_yearly(yearly_interest_percentage: float) -> float:
    return (1+(yearly_interest_percentage/100))**(1/12)-1


class SavingsSimulation():
    def __init__(self, sim_values):
        self.mortgage = 0
        self.top_loan = 0

        self.rent = sim_values['rent per month']
        self.regular_savings = sim_values['deposit']

        self.bsu = sim_values['bsu savings']
        self.bsu2 = sim_values['bsu2 savings']

        self.bsu_left_to_fill = 0
        self.bsu2_left_to_fill = 20000

        # These three interest values are all per month
        self.bsu_interest = get_monthly_interest_from_yearly(3.6)
        self.mortgage_interest = sim_values['mortgage monthly interest']
        self.top_loan_interest = sim_values['top loan monthly interest']

    def get_total_savings(self):
        return self.bsu + self.bsu2 + self.regular_savings

    def get_month_cost(self):
        if self.mortgage == 0:
            return self.rent
        else:
            return self.mortgage * self.mortgage_interest + self.top_loan * self.top_loan_interest

    def pay_down_mortgage(self, month_leftover_money):
        if self.mortgage > month_leftover_money:
            self.mortgage -= month_leftover_money
        elif self.mortgage <= month_leftover_money and self.mortgage != 0:
            self.regular_savings += month_leftover_money - self.mortgage
            self.mortgage = 0
        else:
            self.regular_savings += month_leftover_money

    def new_bsu_year(self):
        self.bsu_left_to_fill = 50000
        self.bsu2_left_to_fill = 50000

    def empty_savings(self):
        total_savings = self.get_total_savings()
        self.bsu = 0
        self.bsu2 = 0
        self.regular_savings = 0
        return total_savings

    def get_bsu_interest_for_one_month(self):
        return (self.bsu + self.bsu2) * self.bsu_interest

    def get_bsu_interest_for_several_months(self, months):
        return (self.bsu + self.bsu2) * ((1 + self.bsu_interest) ** months - 1)

    def top_up_bsus(self, month_leftover_money):
        if self.bsu_left_to_fill > 0:
            month_leftover_money, self.bsu, self.bsu_left_to_fill = \
                self.do_bsu_fill(month_leftover_money, self.bsu, self.bsu_left_to_fill)
        if self.bsu2_left_to_fill > 0:
            month_leftover_money, self.bsu2, self.bsu2_left_to_fill = \
                self.do_bsu_fill(month_leftover_money, self.bsu2, self.bsu2_left_to_fill)
        return month_leftover_money

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


def date_range(start_date, months):
    if start_date.day > 28:
        raise ValueError('This date cannot be consistently increased with one month since the day is more than 28')
    for n in range(1, months):
        yield datetime.datetime(start_date.year + int((start_date.month + n - 1) / 12),
                                (start_date.month + n - 1) % 12 + 1, start_date.day)


def calculate_cost_while_saving(number_of_months, current_values):
    saving_simulation = SavingsSimulation(current_values)
    cumulative_cost, total_debt, time = [0], [0], [current_values['starting date']]
    bsu_interest_this_year = saving_simulation.get_bsu_interest_for_several_months(time[0].month)

    for pay_date in date_range(current_values['starting date'], number_of_months):
        time.append(pay_date)
        this_months_cost = saving_simulation.get_month_cost()
        cumulative_cost.append(this_months_cost + cumulative_cost[-1])
        month_leftover_money = current_values['housing money']-this_months_cost

        # If saving, save up the money in the regular savings, otherwise pay down mortgage
        if saving_simulation.mortgage == 0:
            month_leftover_money = saving_simulation.top_up_bsus(month_leftover_money)
            saving_simulation.regular_savings += month_leftover_money
            total_debt.append(0)
            if saving_simulation.get_total_savings() >= current_values['mortgage goal'] * .15:
                saving_simulation.mortgage = current_values['mortgage goal'] - saving_simulation.empty_savings()
                total_debt[-1] = saving_simulation.mortgage
        else:
            saving_simulation.pay_down_mortgage(month_leftover_money)
            total_debt.append(saving_simulation.mortgage + saving_simulation.top_loan)

        bsu_interest_this_year += saving_simulation.get_bsu_interest_for_one_month()
        if pay_date.month == 1:
            bsu_tax_rebate = (50000-saving_simulation.bsu_left_to_fill)*.2 if saving_simulation.bsu != 0 else 0
            cumulative_cost[-1] = cumulative_cost[-1]-bsu_interest_this_year - bsu_tax_rebate
            bsu_interest_this_year = 0
            saving_simulation.new_bsu_year()
    return time, cumulative_cost, total_debt


def calculate_cost_while_saving_with_bsu_as_security(number_of_months, current_values):
    saving_simulation = SavingsSimulation(current_values)
    cumulative_cost, total_debt, time = [0], [0], [current_values['starting date']]
    bsu_interest_this_year = saving_simulation.get_bsu_interest_for_several_months(time[0].month)

    for pay_date in date_range(current_values['starting date'], number_of_months):
        time.append(pay_date)
        this_months_cost = saving_simulation.get_month_cost()
        cumulative_cost.append(this_months_cost + cumulative_cost[-1])
        month_leftover_money = current_values['housing money']-this_months_cost

        # If saving, save up the money in the regular savings, otherwise pay down mortgage
        if saving_simulation.mortgage == 0:
            month_leftover_money = saving_simulation.top_up_bsus(month_leftover_money)
            saving_simulation.regular_savings += month_leftover_money
            total_debt.append(0)
            if (current_values['mortgage goal'] + saving_simulation.bsu + saving_simulation.bsu2) * .85 >= \
                    current_values['mortgage goal'] - saving_simulation.regular_savings:
                saving_simulation.mortgage = current_values['mortgage goal']-saving_simulation.regular_savings
                saving_simulation.regular_savings = 0
                total_debt[-1] = saving_simulation.mortgage
        else:
            month_leftover_money = saving_simulation.top_up_bsus(month_leftover_money)
            saving_simulation.pay_down_mortgage(month_leftover_money)
            total_debt.append(saving_simulation.mortgage + saving_simulation.top_loan)

        bsu_interest_this_year += saving_simulation.get_bsu_interest_for_one_month()
        if pay_date.month == 1:
            bsu_tax_rebate = (50000-saving_simulation.bsu_left_to_fill)*.2 if saving_simulation.bsu != 0 else 0
            cumulative_cost[-1] = cumulative_cost[-1]-bsu_interest_this_year - bsu_tax_rebate
            bsu_interest_this_year = 0
            saving_simulation.new_bsu_year()
    return time, cumulative_cost, total_debt


def calculate_cost_with_top_loan(number_of_months, current_values):
    mortgage = current_values['mortgage goal']*.85
    top_loan = current_values['mortgage goal']*.15 - current_values['deposit'] - \
               current_values['bsu savings'] - current_values['bsu2 savings']
    cumulative_cost = [0]
    total_debt = [mortgage + top_loan]
    time = [current_values['starting date']]
    for pay_date in date_range(current_values['starting date'], number_of_months):
        month_cost = mortgage*current_values['mortgage monthly interest'] + \
                     top_loan*current_values['top loan monthly interest']
        cumulative_cost.append(month_cost + cumulative_cost[-1])
        pay_down = current_values['housing money'] - month_cost
        if top_loan > pay_down:
            top_loan = top_loan - pay_down
        elif top_loan <= pay_down and top_loan != 0:
            mortgage = mortgage + top_loan - pay_down
            top_loan = 0
        elif mortgage > pay_down:
            mortgage = mortgage - pay_down
        elif mortgage <= pay_down and mortgage != 0:
            mortgage = 0
        time.append(pay_date)
        total_debt.append(mortgage + top_loan)
    return time, cumulative_cost, total_debt


def main():
    pass


if __name__ == '__main__':
    main()
