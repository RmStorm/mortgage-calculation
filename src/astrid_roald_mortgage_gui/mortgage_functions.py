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
        self.mortgage_goal =sim_values['mortgage goal']
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

    def start_mortgage(self, use_bsu_as_security):
        if use_bsu_as_security:
            security = self.mortgage_goal + self.bsu + self.bsu2
            self.mortgage = min(security * .85, self.mortgage_goal - self.regular_savings)
            self.top_loan = max(self.mortgage_goal - self.regular_savings - security * .85, 0)
            self.regular_savings = 0
        else:
            security = self.mortgage_goal
            savings = self.empty_savings()
            self.mortgage = min(security * .85, self.mortgage_goal - savings)
            self.top_loan = max(self.mortgage_goal - savings - security * .85, 0)

    def get_total_savings(self):
        return self.bsu + self.bsu2 + self.regular_savings

    def get_month_cost(self, got_mortgage):
        if got_mortgage:
            return self.mortgage * self.mortgage_interest + self.top_loan * self.top_loan_interest
        else:
            return self.rent

    def pay_down_debt(self, month_leftover_money):
        if self.top_loan > month_leftover_money:
            self.top_loan -= month_leftover_money
        elif self.top_loan <= month_leftover_money and self.top_loan != 0:
            self.mortgage += self.top_loan - month_leftover_money
            self.top_loan = 0
        elif self.mortgage > month_leftover_money:
            self.mortgage -= month_leftover_money
        elif self.mortgage <= month_leftover_money and self.mortgage != 0:
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
        yield datetime.date(start_date.year + int((start_date.month + n - 1) / 12),
                                (start_date.month + n - 1) % 12 + 1, start_date.day)


def calculate_cost(number_of_months, current_values, use_bsu_as_security):
    saving_simulation = SavingsSimulation(current_values)
    cumulative_cost, total_debt, time = [0], [0], [current_values['starting date']]
    bsu_interest_this_year = saving_simulation.get_bsu_interest_for_several_months(time[0].month)
    got_mortgage = False

    for pay_date in date_range(current_values['starting date'], number_of_months):
        time.append(pay_date)
        this_months_cost = saving_simulation.get_month_cost(got_mortgage)
        cumulative_cost.append(this_months_cost + cumulative_cost[-1])
        month_leftover_money = current_values['housing money']-this_months_cost

        # If saving, save up the money in the regular savings, otherwise pay down mortgage
        if pay_date < current_values['mortgage date']:
            month_leftover_money = saving_simulation.top_up_bsus(month_leftover_money)
            saving_simulation.regular_savings += month_leftover_money
            total_debt.append(0)
        else:
            if not got_mortgage:
                saving_simulation.start_mortgage(use_bsu_as_security)
                got_mortgage = True
                top_loan = saving_simulation.top_loan
            if use_bsu_as_security:
                month_leftover_money = saving_simulation.top_up_bsus(month_leftover_money)
            saving_simulation.pay_down_debt(month_leftover_money)
            total_debt.append(saving_simulation.mortgage + saving_simulation.top_loan)

        bsu_interest_this_year += saving_simulation.get_bsu_interest_for_one_month()
        if pay_date.month == 1:
            bsu_tax_rebate = (50000-saving_simulation.bsu_left_to_fill)*.2 if saving_simulation.bsu != 0 else 0
            cumulative_cost[-1] = cumulative_cost[-1]-bsu_interest_this_year - bsu_tax_rebate
            bsu_interest_this_year = 0
            saving_simulation.new_bsu_year()
    return time, cumulative_cost, total_debt, top_loan


def main():
    pass


if __name__ == '__main__':
    main()
