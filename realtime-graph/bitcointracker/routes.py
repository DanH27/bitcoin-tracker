from flask import render_template, url_for, flash, redirect
from bitcointracker import app
from bitcointracker.forms import RegistrationForm, LoginForm
from bitcointracker.models import User, Currency
from pusher import Pusher
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import request
import requests, json, atexit, time, plotly, plotly.graph_objs as go







# configure pusher object
pusher = Pusher(
        app_id='625209',
        key='d0fbb6934c4ec3d8a001',
        secret='d1471059e40c19e1a1fe',
        cluster='us2',
        ssl=True
)

hello = "Hello world!"
moneyLeft = 100000
bitcoinprice = 0
currentBudget = 0
#Array of times
times = []
#The name of currencies stored in an array
currencies = ["BTC", "LTC", "DOGE"]
#Prices and their prices stored in a array in a dictionary.
prices = {"BTC": [], "LTC": [], "DOGE": []}


@app.route("/", methods=['POST', 'GET'])
def index():

    #if request.method == 'POST':

    #    print("HEY")

    return render_template("index.html", moneyLeft=moneyLeft, bitcoinprice=bitcoinprice)


@app.route('/form', methods=['POST', 'GET'])
def test():
    budget = 100000
    select = request.form.get('comp_select')
    bitcoinprice = prices["BTC"][len(prices["BTC"]) - 1]
    if (budget - (int(bitcoinprice) * int(select)) >= 0):
        return "<h1>Buy " + str(select) + " bitcoin(s) for "  + "$" + str(int(bitcoinprice) * int(select)) +"s?" + "</h1>" # just to see what select is
    else:
        return render_template("index.html", moneyLeft=moneyLeft, bitcoinprice=bitcoinprice)



def retrieve_data():
    #Create a dictionary of current Prices
    current_prices = {}
    #For each currency in currencies, initialize each with an empty array as key
    for currency in currencies:
        current_prices[currency] = []
        ##Debug - print current_prices dictionary
        #print(current_prices)

    times.append(time.strftime('%H:%M:%S'))

    #Make an API request and get back the object
    api_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms=USD".format(",".join(currencies))
    #Get amount of the currency
    response = json.loads(requests.get(api_url).content)

    #Iterate through the currencies
    for currency in currencies:
        #Price is equal to python dictionary response, currency name, USD value
        price = response[currency]['USD']
        #Set currency name as key, and price as value in current_prices for specified currency
        current_prices[currency] = price
        #Set prices key as currencyname and append price to list
        prices[currency].append(price)

    graph_data = [go.Scatter(
        x=times,
        y=prices.get(currency),
        name="{} Prices".format(currency)
    ) for currency in currencies]

    # create an array of traces for bar chart data
    bar_chart_data = [go.Bar(
        x=currencies,
        y=list(current_prices.values())
    )]

    bitcoinprice = prices["BTC"][len(prices["BTC"]) - 1]
    litcoinprice = prices["LTC"][len(prices["LTC"]) - 1]
    dogecoinprice = prices["DOGE"][len(prices["DOGE"]) - 1]

    data = {
        'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
        'bar_chart': json.dumps(list(bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder),
        'btc_price': bitcoinprice,
        'money_left': moneyLeft,
        'ltc_price': litcoinprice,
        'doge_price': dogecoinprice
    }

    #Trigger pusher event
    pusher.trigger("crypto", "data-updated", data)

#Get yearly data for cryptocoins
###########TEST#################################'2b. high (USD)'
def yearly_data1(c_info, c_name):
    monthly_keys = []
    monthly_btc_values = []

    api_url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol={}&market=CNY&apikey=JQ5OZI602IGDD72C".format(str(c_name))
    #Get amount of the currency
    my_response = json.loads(requests.get(api_url).content)
    for month in my_response['Time Series (Digital Currency Monthly)'].keys():
        monthly_keys.append(month)

    for month in monthly_keys:
        monthly_btc_values.append(my_response['Time Series (Digital Currency Monthly)'][month][str(c_info)])


    btc_bar_chart_data = [go.Bar(
        x=monthly_keys,
        y=monthly_btc_values
    )]

    monthly_btc_data = {'btc_month_bar': json.dumps(list(btc_bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)}

    #print(my_response['Time Series (Digital Currency Monthly)'].keys())

    #Trigger every month
    pusher.trigger("crypto", "month-updated", monthly_btc_data)

def yearly_data():
    monthly_keys = []
    monthly_btc_values = []

    api_url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market=CNY&apikey=JQ5OZI602IGDD72C"
    #Get amount of the currency
    my_response = json.loads(requests.get(api_url).content)
    for month in my_response['Time Series (Digital Currency Monthly)'].keys():
        monthly_keys.append(month)

    for month in monthly_keys:
        monthly_btc_values.append(my_response['Time Series (Digital Currency Monthly)'][month]['2b. high (USD)'])


    btc_bar_chart_data = [go.Bar(
        x=monthly_keys,
        y=monthly_btc_values
    )]

    monthly_btc_data = {'btc_month_bar': json.dumps(list(btc_bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)}
    #print(my_response['Time Series (Digital Currency Monthly)'].keys())

    #Trigger every month
    pusher.trigger("crypto", "month-updated", monthly_btc_data)


#Get litecoin by month
def monthly_ltc_data():
    monthly_keys = []
    monthly_ltc_values = []

    api_url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=LTC&market=CNY&apikey=JQ5OZI602IGDD72C"
    #Get amount of the currency
    my_response = json.loads(requests.get(api_url).content)
    for month in my_response['Time Series (Digital Currency Monthly)'].keys():
        monthly_keys.append(month)

    for month in monthly_keys:
        monthly_ltc_values.append(my_response['Time Series (Digital Currency Monthly)'][month]['2b. high (USD)'])


    ltc_bar_chart_data = [go.Bar(
        x=monthly_keys,
        y=monthly_ltc_values
    )]

    monthly_ltc_data = {'ltc_month_bar': json.dumps(list(ltc_bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)}
    #print(my_response['Time Series (Digital Currency Monthly)'].keys())
    pusher.trigger("crypto", "ltc-month-updated", monthly_ltc_data)

#Get ethereium by month
def monthly_eth_data():
    monthly_keys = []
    monthly_eth_values = []

    api_url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=ETH&market=CNY&apikey=JQ5OZI602IGDD72C"
    #Get amount of the currency
    my_response = json.loads(requests.get(api_url).content)
    for month in my_response['Time Series (Digital Currency Monthly)'].keys():
        monthly_keys.append(month)

    for month in monthly_keys:
        monthly_eth_values.append(my_response['Time Series (Digital Currency Monthly)'][month]['2b. high (USD)'])


    eth_bar_chart_data = [go.Bar(
        x=monthly_keys,
        y=monthly_eth_values
    )]

    monthly_eth_data = {'eth_month_bar': json.dumps(list(eth_bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)}
    #print(my_response['Time Series (Digital Currency Monthly)'].keys())
    pusher.trigger("crypto", "eth-month-updated", monthly_eth_data)


@app.route("/btc")
def btc_dash():
#    yearly_data1('2b. high (USD)', 'BTC')
    return render_template("individual.html", data="sdfs")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!')
    return render_template('register.html', title='Register', form=form)

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

@app.route("/currencies")
def ctable():
    return render_template('currencies.html', title="currencies")

# create schedule for retrieving prices
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=retrieve_data,
    trigger = IntervalTrigger(seconds=10),
    id='prices_retrieval_job',
    name='Retrieve prices every 10 seconds',
    replace_existing = True
    )

# yearly_data1('2b. high (USD)', 'BTC')
monthly_eth_data()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
