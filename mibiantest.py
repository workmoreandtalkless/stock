import mibian
try:
	from scipy.stats import norm
except ImportError:
	print('Mibian requires scipy to work properly')
# Given parameters
underlying_price = 100  # Current price of the underlying asset
strike_price = 100      # Strike price of the option
risk_free_rate = 0.01   # Annual risk-free interest rate (1%)
days_to_expiration = 30  # Days until the option expires
market_price_of_call = 2.5  # Observed market price of the call option

# Using mibian to calculate implied volatility for a call option
# BS([Underlying Price, Strike Price, Interest Rate * 100, Days until expiration], callPrice=Market price of call)
c = mibian.BS([underlying_price, strike_price, risk_free_rate * 100, days_to_expiration], callPrice=market_price_of_call)

print(f"Implied Volatility: {c.impliedVolatility}%")
