import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Define the stock symbol and timeframe
ticker = 'PYFA.JK'
start_date = '2025-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')

# Download historical data
data = yf.download(ticker, start=start_date, end=end_date)

# Check if data is available
if data.empty:
    raise ValueError('No data found for the specified period.')

# Plot trading volume and closing price
data[['Close', 'Volume']].plot(subplots=True, figsize=(12, 8), title=['Closing Price', 'Trading Volume'])
plt.tight_layout()
plt.show()

# Forecasting next 7 days closing price using Holt-Winters Exponential Smoothing
model = ExponentialSmoothing(data['Close'], trend='add', seasonal=None, initialization_method='estimated')
fit = model.fit()
forecast = fit.forecast(7)

# Plot the forecast
plt.figure(figsize=(10, 5))
plt.plot(data.index, data['Close'], label='Historical Close')
plt.plot(pd.date_range(data.index[-1] + pd.Timedelta(days=1), periods=7, freq='B'), forecast, label='7-Day Forecast', linestyle='--')
plt.title('PYFA.JK Closing Price Forecast (Next 7 Business Days)')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Note: yfinance does not provide direct data on foreign investor activity. For a more accurate prediction considering foreign investment, you would need access to specialized data sources (e.g., IDX, Bloomberg, or local brokerage reports). This script forecasts based on price and volume only.