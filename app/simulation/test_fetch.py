from app.simulation.data_fetcher import fetch_data
from app.simulation.lump_sum import LumpSumSimulator

# Step 1: fetch real data
data = fetch_data("BTC-USD", "2015-01-01")

# Step 2: run simulation
sim = LumpSumSimulator(data, 500)
result = sim.run()

# Step 3: print result
print("RESULT:\n")
print(result)

print("\nFIRST 5 CHART POINTS:\n")
print(result["chart_data"][:5])