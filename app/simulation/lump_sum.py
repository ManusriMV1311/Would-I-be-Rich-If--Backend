class LumpSumSimulator:
    def __init__(self, ticker: str, start_date: str, price_data: list[dict], live_price: float, initial_amount: float):
        self.ticker = ticker
        self.start_date = start_date
        self.price_data = price_data
        self.live_price = live_price
        self.initial_amount = initial_amount

    def run(self) -> dict:
        if not self.price_data:
            raise ValueError("No price data provided")

        # 1. Fetch historical price explicitly based on the array
        buy_price = self.price_data[0]["price"]

        # 3. Compute precise unit ownership scaling
        units = self.initial_amount / buy_price
        current_value = units * self.live_price

        # Diff metrics
        difference = current_value - self.initial_amount
        growth_percentage = (difference / self.initial_amount) * 100

        # Exact Debug Log Verification 
        print(f"Asset: {self.ticker}")
        print(f"Start Date: {self.start_date}")
        print(f"Buy Price: {buy_price}")
        print(f"Current Price: {self.live_price}")
        print(f"Units: {units}")
        print(f"Final Value: {current_value}")

        # Map dynamic simulation values across the historic footprint array
        # Optimization: Downsample if too many points (e.g. > 500) to keep Recharts snappy
        chart_data = []
        step = 1
        if len(self.price_data) > 500:
            step = len(self.price_data) // 500

        for i in range(0, len(self.price_data), step):
            point = self.price_data[i]
            value = units * point["price"]
            chart_data.append({
                "date": point["date"],
                "value": round(value, 2)
            })
        
        # Ensure the last point is always included for accuracy
        if step > 1 and chart_data[-1]["date"] != self.price_data[-1]["date"]:
            last_point = self.price_data[-1]
            chart_data.append({
                "date": last_point["date"],
                "value": round(units * last_point["price"], 2)
            })

        return {
            "alternate_value": round(current_value, 2),
            "real_value": round(self.initial_amount, 2),
            "difference": round(difference, 2),
            "growth_percentage": round(growth_percentage, 2),
            "buy_price": round(buy_price, 2),
            "current_price": round(self.live_price, 2),
            "chart_data": chart_data
        }