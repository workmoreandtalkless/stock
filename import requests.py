# Version 3.6.1    
import requests
def get_option_prices(symbol, expiration):
    url = 'https://sandbox.tradier.com/v1/markets/options/chains'
    headers={'Authorization': 'Bearer UuzyUcag13mauUfl9ATuyRvKSsxN', 'Accept': 'application/json'}
    params={'symbol': symbol, 'expiration': expiration, 'greeks': 'true'}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        return {'error': str(e)}



# Example call to the function
symbol = 'AAPL'  # Example ticker symbol for Apple
expiration = '2024-09-27'  # Example expiration date

# Call the function
option_data = get_option_prices(symbol, expiration)

# Print the output
print(option_data)