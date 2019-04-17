import datetime

example_input = {'date of creation': datetime.datetime(2019, 3, 20),
                 'rent per month': 1000,
                 'housing money': 2000,
                 'deposit': 1000,
                 'total savings': 2000,
                 'mortgage goal': 400000,
                 'top loan interest percentage': 10,
                 'mortgage interest percentage': 1}


def get_monthly_interest_from_yearly(yearly_interest_percentage: float) -> float:
    return (1+(yearly_interest_percentage/100))**(1/12)-1


def calculate_cost_with_top_loan(duration, housing_money, mortgage, top_loan,
                                 mortgage_yearly_interest, top_loan_yearly_interest):
    mortgage_monthly_interest = get_monthly_interest_from_yearly(mortgage_yearly_interest)
    top_loan_monthly_interest = get_monthly_interest_from_yearly(top_loan_yearly_interest)
    cumulative_cost = [0]
    for i in range(duration):
        month_cost = mortgage*mortgage_monthly_interest + top_loan*top_loan_monthly_interest
        cumulative_cost.append(month_cost + cumulative_cost[-1])
        pay_down = housing_money - month_cost
        if top_loan > pay_down:
            top_loan = top_loan - pay_down
        elif top_loan == 0:
            mortgage = mortgage - pay_down
        else:
            mortgage = mortgage - pay_down + top_loan
            top_loan = 0
    return cumulative_cost


def main():
    print(calculate_cost_with_top_loan(100, example_input['housing money'],
                                       example_input['mortgage goal'] * .85, example_input['mortgage goal'] * .15,
                                       example_input['mortgage interest percentage'],
                                       example_input['top loan interest percentage']))


if __name__ == '__main__':
    main()
