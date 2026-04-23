import pandas as pd

def simulate_dca(data: list[dict], monthly_investment: float):
    # Convert list → DataFrame
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    # Resample monthly (last price of month)
    monthly = df.resample('ME').last()

    total_units = 0
    total_invested = 0

    portfolio_values = []
    invested_values = []

    for date, row in monthly.iterrows():
        price = row['price']

        units = monthly_investment / price
        total_units += units
        total_invested += monthly_investment

        portfolio_value = total_units * price

        portfolio_values.append(portfolio_value)
        invested_values.append(total_invested)

    monthly['portfolio'] = portfolio_values
    monthly['invested'] = invested_values

    return monthly