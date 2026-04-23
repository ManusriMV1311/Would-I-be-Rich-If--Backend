class LumpSumSimulator:
    def __init__(self, price_data: list[dict], initial_amount: float):
        self.price_data = price_data
        self.initial_amount = initial_amount

    def run(self) -> dict:
        if not self.price_data:
            raise ValueError("No price data provided")

        first_price = self.price_data[0]["price"]
        last_price = self.price_data[-1]["price"]

        # Buy at first price
        shares = self.initial_amount / first_price

        # Final value
        final_value = shares * last_price

        profit = final_value - self.initial_amount
        growth_percent = (profit / self.initial_amount) * 100

        # Chart data (portfolio value over time)
        chart_data = []
        for point in self.price_data:
            value = shares * point["price"]
            chart_data.append({
                "date": point["date"],
                "value": value
            })

        return {
            "initial": self.initial_amount,
            "final": round(final_value, 2),
            "profit": round(profit, 2),
            "growth_percent": round(growth_percent, 2),
            "chart_data": chart_data
        }