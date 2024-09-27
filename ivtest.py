import QuantLib as ql
from datetime import datetime

# Parameters
underlying_price = 100
strike_price = 100
risk_free_rate = 0.01
dividend_yield = 0.02  # Assuming there's a dividend yield
volatility = 0.25
market_price = 10

# Option type
option_type = ql.Option.Call

# Dates
today = datetime.now()
valuation_date = ql.Date(today.day, today.month, today.year)
expiration_date = ql.Date(27, 10, 2024)
ql.Settings.instance().evaluationDate = valuation_date

# Payoff
payoff = ql.PlainVanillaPayoff(option_type, strike_price)

# American exercise
exercise = ql.AmericanExercise(valuation_date, expiration_date)
american_option = ql.VanillaOption(payoff, exercise)

# Process setup
spot_handle = ql.QuoteHandle(ql.SimpleQuote(underlying_price))
flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(valuation_date, risk_free_rate, ql.Actual365Fixed()))
div_yield = ql.YieldTermStructureHandle(ql.FlatForward(valuation_date, dividend_yield, ql.Actual365Fixed()))
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(valuation_date, ql.TARGET(), volatility, ql.Actual365Fixed()))
bs_process = ql.BlackScholesMertonProcess(spot_handle, div_yield, flat_ts, flat_vol_ts)

# Pricing engine
american_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bs_process))

# Implied volatility calculation
try:
    implied_vol = american_option.impliedVolatility(market_price, bs_process)
    print(f"The implied volatility is: {implied_vol:.4f} or {implied_vol * 100:.2f}%")
except RuntimeError as e:
    print(f"Error calculating IV: {e}")
