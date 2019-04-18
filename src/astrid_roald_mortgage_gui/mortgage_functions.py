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


def calculate_cost_while_saving(duration, housing_money, mortgage, mortgage_yearly_interest):
    pass


def calculate_cost_with_top_loan(duration, current_values):
    mortgage = current_values['mortgage goal']*.85
    top_loan = current_values['mortgage goal']*.15
    cumulative_cost = [0]
    for i in range(duration):
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
    return cumulative_cost


def main():
    pass


if __name__ == '__main__':
    main()
