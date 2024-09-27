import sys
import requests
import math
import QuantLib as ql
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox
from PyQt5.QtGui import QFont, QColor  # Import QFont and QColor
from datetime import datetime

class OptionsViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Real-Time Options Data Viewer')
        self.setGeometry(100, 100, 1600, 800)  # x, y, width, height

        widget = QWidget(self)
        self.setCentralWidget(widget)
        vLayout = QVBoxLayout(widget)

        self.symbolInput = QLineEdit(self)
        self.symbolInput.setPlaceholderText('Enter ticker symbol...')
        vLayout.addWidget(self.symbolInput)

        # self.symbolInput = QLineEdit(self)
        # self.symbolInput.setPlaceholderText('Enter ticker symbol...')
        # vLayout.addWidget(self.symbolInput)
        # Other UI setup...

        self.rateInput = QLineEdit(self)
        self.rateInput.setPlaceholderText('Enter interest rate...')
        self.rateInput.setText("0.0")  # Default value for interest rate
        vLayout.addWidget(self.rateInput)




        self.expirationDropdown = QComboBox(self)
        self.expirationDropdown.addItem("2024-09-27")  # Test data
        self.expirationDropdown.addItem("2024-10-25")
        vLayout.addWidget(self.expirationDropdown)



        self.loadButton = QPushButton('Load Data', self)
        self.loadButton.clicked.connect(self.load_data)
        vLayout.addWidget(self.loadButton)

                        # Display Forward Price
        self.forwardPriceLabel = QLabel(self)
        self.forwardPriceLabel.setText("Forward Price: Calculating...")
        vLayout.addWidget(self.forwardPriceLabel)

        self.table = QTableWidget(self)
        self.table.setColumnCount(15)  # Number of columns as per requirements
        self.table.setHorizontalHeaderLabels([
            "Call Bid Size", "Call Bid Price", "Call Bid IV", "Call Ask IV",
            "Call Ask Price", "Call Ask Size", "Call IV", "Strike Price", 
            "Put Bid Size","Put Bid Price", "Put Bid IV", "Put Ask IV", "Put Ask Price", 
            "Put Ask Size","Put IV"
        ])
        vLayout.addWidget(self.table)

        self.show()

    def load_data(self):
        print("Load data called")  # Check if this prints when button is clicked
        symbol = self.symbolInput.text()
        rate = self.rateInput.text()
        # expiration = self.symbolInput.text()
        expiration = self.expirationDropdown.currentText()
        print(f"Fetching data for {symbol} with expiration {expiration} with rate {rate}")
        if symbol and expiration:
            data = self.get_option_prices(symbol, expiration)
            datastock = self.get_stock_prices(symbol)
            # print("Data received:", data)  # See what data is received
            self.update_table(data,rate,expiration,datastock)
            

    def get_option_prices(self,symbol, expiration):
        url = 'https://sandbox.tradier.com/v1/markets/options/chains'
        headers = {'Authorization': 'Bearer UuzyUcag13mauUfl9ATuyRvKSsxN', 'Accept': 'application/json'}
        params = {'symbol': symbol, 'expiration': expiration, 'greeks': 'true'}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_stock_prices(self, symbol):
        import requests  # Ensure requests is imported
        url = 'https://sandbox.tradier.com/v1/markets/quotes'
        headers = {
            'Authorization': 'Bearer UuzyUcag13mauUfl9ATuyRvKSsxN',
            'Accept': 'application/json'
        }
        params = {'symbols': symbol, 'greeks': 'false'}
        response = requests.get(url, headers=headers, params=params)
        # print('Status Code:', response.status_code)
        # print('Response Content:', response.content.decode('utf-8'))
        response.raise_for_status()
        return response.json()

    
    def update_table(self, data,rate,expiration,datastock):
        if datastock and 'quotes' in datastock and 'quote' in datastock['quotes']:
            quotes = datastock['quotes']['quote']
            underlying_price_origin = quotes.get('last')
        
        if data and 'options' in data and 'option' in data['options']:
            options = data['options']['option']
            # print(options)
            # print("********************************************")
            # for option in options:
                # Separate calls and puts
            calls = [opt for opt in options if opt.get('option_type') == 'call']
            puts = [opt for opt in options if opt.get('option_type') == 'put']
            # print(calls)
            # print("==========================================")
        # Initialize the options_data list to store the combined data
        options_data = []
               # Assuming each strike has both a call and a put
        self.table.setRowCount(0)  # Clear existing rows
        for call, put in zip(calls, puts):
            

            # Extract relevant data from the call and put dictionaries
            strike = call.get('strike', None)
    
            call_bid = call.get('bid', None)
            call_ask = call.get('ask', None)
    
            put_bid = put.get('bid', None)
            put_ask = put.get('ask', None)

            # Get today's date using datetime
            today = datetime.now()

            # Convert to QuantLib date
            valuation_date = ql.Date(today.day, today.month, today.year)
            # Set the evaluation date in QuantLib
            ql.Settings.instance().evaluationDate = valuation_date
            expiration_date = ql.Date(27, 10, 2024)
            risk_free_rate = float(rate)
            strike_price = strike
            underlying_price = underlying_price_origin
            dividend_yield = 0.0
            initial_volatility_estimate = 0.20
            call_market_price = (call_bid + call_ask)/2
            put_market_price = (put_bid + put_ask)/2

            # CALL
            # Option type and dates
            option_type = ql.Option.Call
            today = datetime.now()
            valuation_date = ql.Date(today.day, today.month, today.year)
            expiration_date = ql.Date(25, 10, 2024)
            ql.Settings.instance().evaluationDate = valuation_date

            # Setup option specifics
            payoff = ql.PlainVanillaPayoff(option_type, strike_price)
            exercise = ql.AmericanExercise(valuation_date, expiration_date)
            american_option = ql.VanillaOption(payoff, exercise)

            # Financial models setup
            # print("Valuation Date:", valuation_date)
            # print("Risk-Free Rate:", risk_free_rate)
            # print("Dividend Yield:", dividend_yield)

            spot_handle = ql.QuoteHandle(ql.SimpleQuote(underlying_price))
            flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(valuation_date, risk_free_rate, ql.Actual365Fixed()))
            div_yield = ql.YieldTermStructureHandle(ql.FlatForward(valuation_date, dividend_yield, ql.Actual365Fixed()))
            flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(valuation_date, ql.TARGET(), initial_volatility_estimate, ql.Actual365Fixed()))
            bs_process = ql.BlackScholesMertonProcess(spot_handle, div_yield, flat_ts, flat_vol_ts)

            # Pricing engine setup
            american_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bs_process))

            # Attempt to calculate implied volatility
            try:
                implied_vol_call = american_option.impliedVolatility(call_market_price, bs_process, 1.0e-4, 100, 0.01, 2.0)
                print(f"The implied volatility is: {implied_vol_call:.4f} or {implied_vol_call * 100:.2f}%")
            except RuntimeError as e:
                print(f"Error calculating IV: {str(e)}")

            #PUT
             # Option type and dates
            option_type = ql.Option.Put
            today = datetime.now()
            valuation_date = ql.Date(today.day, today.month, today.year)
            expiration_date = ql.Date(25, 10, 2024)
            ql.Settings.instance().evaluationDate = valuation_date

            # Setup option specifics
            payoff = ql.PlainVanillaPayoff(option_type, strike_price)
            exercise = ql.AmericanExercise(valuation_date, expiration_date)
            american_option = ql.VanillaOption(payoff, exercise)

            # Financial models setup
            spot_handle = ql.QuoteHandle(ql.SimpleQuote(underlying_price))
            flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(valuation_date, risk_free_rate, ql.Actual365Fixed()))
            div_yield = ql.YieldTermStructureHandle(ql.FlatForward(valuation_date, dividend_yield, ql.Actual365Fixed()))
            flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(valuation_date, ql.TARGET(), initial_volatility_estimate, ql.Actual365Fixed()))
            bs_process = ql.BlackScholesMertonProcess(spot_handle, div_yield, flat_ts, flat_vol_ts)

            # Pricing engine setup
            american_option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(bs_process))

            # Attempt to calculate implied volatility
            try:
                implied_vol_put = american_option.impliedVolatility(put_market_price, bs_process, 1.0e-4, 100, 0.01, 2.0)
                print(f"The implied volatility is: {implied_vol_put:.4f} or {implied_vol_put * 100:.2f}%")
            except RuntimeError as e:
                print(f"Error calculating IV: {str(e)}")

            # Create a dictionary with the required structure and add it to the options_data list
            option_entry = {
                'strike': strike,
                'call_bid': call_bid,
                'call_ask': call_ask,
                'put_bid': put_bid,
                'put_ask': put_ask
            }

            options_data.append(option_entry)
            
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

        
            # Insert call data
            self.table.setItem(row_position, 0, QTableWidgetItem(str(call.get('bidsize', 'N/A'))))
            self.table.setItem(row_position, 1, QTableWidgetItem(f"{call.get('bid', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{call.get('greeks', {}).get('bid_iv', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 3, QTableWidgetItem(f"{call.get('greeks', {}).get('ask_iv', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 4, QTableWidgetItem(f"{call.get('ask', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 5, QTableWidgetItem(str(call.get('asksize', 'N/A'))))
            # self.table.setItem(row_position, 6, QTableWidgetItem(str(implied_vol_call)))
            self.table.setItem(row_position, 6, QTableWidgetItem(f"{implied_vol_call * 100:.4f}%"))

            # self.table.setItem(row_position, 6, QTableWidgetItem(str(call_option_iv)))

            # Insert strike price (common for both)
            strike_item = QTableWidgetItem(f"{call.get('strike', 'N/A'):,.2f}")
            strike_item.setFont(QFont("Arial", 10, QFont.Bold))
            strike_item.setBackground(QColor(255, 255, 0))  # Yellow background
            self.table.setItem(row_position, 7, strike_item)

            # Insert put data
            self.table.setItem(row_position, 8, QTableWidgetItem(str(put.get('bidsize', 'N/A'))))
            self.table.setItem(row_position, 9, QTableWidgetItem(f"{put.get('bid', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 10, QTableWidgetItem(f"{put.get('greeks', {}).get('bid_iv', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 11, QTableWidgetItem(f"{put.get('greeks', {}).get('ask_iv', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 12, QTableWidgetItem(f"{put.get('ask', 'N/A'):,.2f}"))
            self.table.setItem(row_position, 13, QTableWidgetItem(str(put.get('asksize', 'N/A'))))
            # self.table.setItem(row_position, 14, QTableWidgetItem(str(implied_vol_put)))
            self.table.setItem(row_position, 14, QTableWidgetItem(f"{implied_vol_put * 100:.4f}%"))
            # self.table.setItem(row_position, 14, QTableWidgetItem(str(put_option_iv)))
            # Now, options_data contains the structured data as you specified
            # print(options_data)
            # print("==========================================")
            # Step 1: Calculate mid-prices for all options
        # print("Calculating mid-prices and differences for all options:\n")
        for option in options_data:
            option['call_mid'] = (option['call_bid'] + option['call_ask']) / 2
            option['put_mid'] = (option['put_bid'] + option['put_ask']) / 2
            option['mid_diff'] = abs(option['call_mid'] - option['put_mid'])
            # print(f"Strike: {option['strike']}")
            # print(f"  Call Mid-Price: {option['call_mid']}")
            # print(f"  Put Mid-Price: {option['put_mid']}")
            # print(f"  Absolute Difference: {option['mid_diff']}\n")
        # Step 2: Find the strike with the smallest absolute difference
        min_diff_option = min(options_data, key=lambda x: x['mid_diff'])
        # Step 3: Calculate the forward price
        K = min_diff_option['strike']
        C = min_diff_option['call_mid']
        P = min_diff_option['put_mid']
        r = float(rate)  # 1% annual interest rate
        # Convert the string to a datetime object
        expiration_date = datetime.strptime(expiration, "%Y-%m-%d")
        # Define the current date (or any other given date)
        current_date = datetime.now()
        # Calculate the difference in days and convert to years
        days_until_expiration = (expiration_date - current_date).days
        years_until_expiration = days_until_expiration / 365.0
        T = float(years_until_expiration)   # 0.5 years until expiration
        e_rt = math.exp(r * T)
        F = K + (C - P) * e_rt
        self.forwardPriceLabel.setText(f"forward price: {F:.2f}")

def main():
    app = QApplication(sys.argv)
    ex = OptionsViewer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
