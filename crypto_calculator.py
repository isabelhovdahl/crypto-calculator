#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import requests

from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc

from dash import jupyter_dash
jupyter_dash.default_mode = 'external'


# # Cryptocurrency Converter Calculator
# 
# In this notebook, we replicate some of the functionalities in the Cryptocurrency Converter Calculator found here: https://www.coingecko.com/en/converter. Our calculator allows the user to convert an amount of a cryptocurrency to either USD, EUR or GBP.
# 
# To get the real-time exchange rate for the conversion, we use the CURRENCY_EXCHANGE_RATE API from Alpha Vantage: https://www.alphavantage.co/documentation/#crypto-exchange.

# Our application allows the user to select any of the ten coins in `digital_currency_list.csv`.

# In[ ]:


df_coins = pd.read_csv('digital_currency_list.csv')

df_coins


# ### Extract data from API
# 
# To make a request to the API, you must copy-paste one of the keys from `keys.txt` into the variable `my_key` below.

# In[ ]:


my_key = 'GQYCH20FNCG9NCR1'


# We create a function called `get_current_rate` to extract the current conversion rate for a given coin and currency. Note that the function use a `try`-`except` block to handle potential errors. In case the API does not have data for the selected coin or currency, or we have exceeded our number of API calls, the function will return nothing. If the API call was successful, the function will instead return the actual conversion rate.

# In[ ]:


def get_current_rate(coin, currency, apikey = my_key):

    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=' + coin + '&to_currency=' + currency + '&apikey=' + apikey
    data = requests.get(url).json()

    try:
        rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    except:
        rate = None

    return rate


# In[ ]:


# Successful API call
get_current_rate('BTC', 'USD')


# In[ ]:


# Unsuccessful API call
get_current_rate('BTC', 'NOK')


# ### Create selectors
# 
# We use a `Dropdown` component to create the selectors for both the coin and the currency. 

# To create the options in the coin selector, we use list comprehension to loop over the rows in `df_coins` to create value-label pairs for each coin the data.

# In[ ]:


coins = dcc.Dropdown(
    id = 'my_coin',
    options = [{'value' : tick, 'label' : name} for tick, name in zip(df_coins['currency code'], df_coins['currency name'])],
    value = 'BTC',
    clearable = False,
    multi = False,
)


# The selector for the currencies allow the user to choose between USD, EUR and GBP.

# In[ ]:


currencies = dcc.Dropdown(
    id = 'my_currency',
    options = ['USD', 'EUR', 'GBP'],
    value = 'USD',
    clearable = False,
    multi = False,
)


# ### Create app content
# 
# To replicate the layout of the coingekko's calculator, we create a `Row` component that contains three `Col` components:
# 
# - In the first column, we use an `Input` component to allow the user to select an amount to convert. Note that we use the `Input` component from `dbc` (instead of from `dcc`) to get nicer styling of the component.
# - In the second column, we insert the coin selector.
# - In the third column, we insert the currency selector.

# In[ ]:


input_row = dbc.Row(
    children = [
        dbc.Col(
            children = [
                html.H6('Enter amount'), 
                dbc.Input(
                    id = 'my_amount', 
                    type = 'number', 
                    value = 1, 
                )
            ], 
            width = 4
        ),
        dbc.Col([html.H6('Select coin'), coins], width = 4),
        dbc.Col([html.H6('Select currency'), currencies], width = 4)
    ]
)


# In addition, we create a second "row" that contains the output of the actual conversion. Note that instead of using a `Row` component, we create a seperate division by using a `Container` component. The division is currently empty as it will be updated in the callback. 

# In[ ]:


output_row = dbc.Container(
    id = 'my_conversion', 
    children = '',                # currently empty
    style = {'minHeight': '2rem'} # set minimum height to ensure fixed dimensions
)


# ### Create and launch app
# 
# We place our conversion calculator inside a `Card` component inside the app layout. The app has a single callback function that updates the output for the conversion every time there is a change to the selected amount, coin or currency. Note that the callback returns an empty string if an amount has not been selected, same as in coingekko's calculator. In addition, the callback returns a print statement in case the API call was unsuccessful. 

# In[ ]:


app = Dash(__name__, external_stylesheets = [dbc.themes.JOURNAL])
server = app.server
app.title = 'Crypto calculator'

description = """
Check the latest cryptocurrency prices against all USD, EUR and GBP. 

Data is extracted from [Alpha Vantage](https://www.alphavantage.co/documentation/#crypto-exchange).
"""

app.layout = dbc.Container(
    children = [

        # Header
        html.H1('Cryptocurrency Converter Calculator'),
        dcc.Markdown(description),

        # Card with calculator
        dbc.Card(
            children = [
                input_row, 
                html.Br(),
                output_row
            ],
            body = True,
            className = 'shadow-sm p-3' # add shadow to card
        )
        
    ],
)

@app.callback(
    Output('my_conversion', 'children'),
    Input('my_coin', 'value'),
    Input('my_currency', 'value'),
    Input('my_amount', 'value')
)
def update_conversion(coin, currency, amount):

    symbol = {'USD' : '$', 'EUR' : '€', 'GBP' : '£'}

    # Return nothing if no amount is entered
    if amount is None:
        return ''

    # Make API call if amount is entered
    else:
        rate = get_current_rate(coin, currency)

        # Return nothing if API call was not successfull
        if rate is None:
            return 'Data not available'
        
        # Return conversion if API call was successfull
        else:
            conversion = rate*amount
            return html.H4(f'{amount:,} {coin} = {symbol[currency]}{conversion:,.2f}')
            
    
if __name__ == '__main__':
    app.run(debug = True)


# In[ ]:





# In[ ]:




