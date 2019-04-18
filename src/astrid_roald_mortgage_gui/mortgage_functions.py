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


def daterange(start_date, months):
    if start_date.day > 28:
        raise ValueError('This date cannot be consistently increased with one month since the day is more than 28')
    for n in range(1, months):
        yield datetime.datetime(start_date.year+int((start_date.month+n-1)/12),
                                (start_date.month+n-1)%12+1, start_date.day)


def get_monthly_interest_from_yearly(yearly_interest_percentage: float) -> float:
    return (1+(yearly_interest_percentage/100))**(1/12)-1


def calculate_cost_while_saving(number_of_months, current_values):
    rent = current_values['rent per month']
    required_savings = current_values['mortgage goal'] * .15
    current_savings = current_values['deposit'] + current_values['bsu savings'] + current_values['bsu2 savings']

    cumulative_cost = [0]
    time = [current_values['starting date']]
    for pay_date in daterange(current_values['starting date'], number_of_months):
        if current_savings<required_savings:
            cumulative_cost.append(rent + cumulative_cost[-1])
            current_savings = current_savings + current_values['housing money'] - rent
            if current_savings >= required_savings:
                mortgage = current_values['mortgage goal'] - current_savings
        else:
            month_cost = mortgage*current_values['mortgage monthly interest']
            cumulative_cost.append(month_cost + cumulative_cost[-1])
            pay_down = current_values['housing money'] - month_cost
            if mortgage > pay_down:
                mortgage = mortgage - pay_down
            elif mortgage <= pay_down and mortgage != 0:
                mortgage = 0
        time.append(pay_date)
    return time, cumulative_cost


def calculate_cost_with_top_loan(number_of_months, current_values):
    mortgage = current_values['mortgage goal']*.85
    top_loan = current_values['mortgage goal']*.15 - current_values['deposit'] - \
               current_values['bsu savings'] - current_values['bsu2 savings']
    cumulative_cost = [0]
    time = [current_values['starting date']]
    for pay_date in daterange(current_values['starting date'], number_of_months):
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
    return time, cumulative_cost


def main():
    pass


if __name__ == '__main__':
    main()
