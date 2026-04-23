from app.simulation.data_fetcher import fetch_data
from app.simulation.dca import simulate_dca

data = fetch_data("AAPL", "2015-01-01")

result = simulate_dca(data, monthly_investment=1000)

print(result.tail())