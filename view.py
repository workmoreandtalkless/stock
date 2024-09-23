import sys
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
                             QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox)

class OptionsViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Real-Time Options Data Viewer')
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        widget = QWidget(self)
        self.setCentralWidget(widget)
        vLayout = QVBoxLayout(widget)

        self.symbolInput = QLineEdit(self)
        self.symbolInput.setPlaceholderText('Enter ticker symbol...')
        vLayout.addWidget(self.symbolInput)

        self.symbolInput = QLineEdit(self)
        self.symbolInput.setPlaceholderText('Enter ticker symbol...')
        vLayout.addWidget(self.symbolInput)
        # self.expirationDropdown = QComboBox(self)
        # vLayout.addWidget(self.expirationDropdown)

        self.loadButton = QPushButton('Load Data', self)
        self.loadButton.clicked.connect(self.load_data)
        vLayout.addWidget(self.loadButton)

        self.table = QTableWidget(self)
        self.table.setColumnCount(13)  # Number of columns as per requirements
        self.table.setHorizontalHeaderLabels([
            "Call Bid Size", "Call Bid Price", "Call Bid IV", "Call Ask IV",
            "Call Ask Price", "Call Ask Size", "Strike Price", "Put Bid Size",
            "Put Bid Price", "Put Bid IV", "Put Ask IV", "Put Ask Price", "Put Ask Size"
        ])
        vLayout.addWidget(self.table)

        self.show()

    def load_data(self):
        print("Load data called")  # Check if this prints when button is clicked
        symbol = self.symbolInput.text()
        expiration = self.symbolInput.text()
        # expiration = self.expirationDropdown.currentText()
        print(f"Fetching data for {symbol} with expiration {expiration}")
        if symbol and expiration:
            data = self.get_option_prices(symbol, expiration)
            print("Data received:", data)  # See what data is received
            self.update_table(data)

    def get_option_prices(self, symbol, expiration):
        url = 'https://sandbox.tradier.com/v1/markets/options/chains'
        headers = {'Authorization': 'Bearer YourAccessToken', 'Accept': 'application/json'}
        params = {'symbol': symbol, 'expiration': expiration, 'greeks': 'true'}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def update_table(self, data):
        self.table.setRowCount(0)  # Clear existing rows
        if data and 'options' in data and 'option' in data['options']:
            for option in data['options']['option']:
                row_count = self.table.rowCount()
                self.table.insertRow(row_count)
                # Here, you would create QTableWidgetItem for each piece of data
                # you want to display, and add them to the table. For example:
                # self.table.setItem(row_count, 0, QTableWidgetItem(str(option['bid_size'])))
                # Repeat for all required fields

def main():
    app = QApplication(sys.argv)
    ex = OptionsViewer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
