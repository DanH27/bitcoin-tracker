#app.py
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pusher import Pusher
import requests, json, atexit, time, plotly, plotly.graph_objs as go

app = Flask(__name__)

# configure pusher object
pusher = Pusher(
        app_id='625209',
        key='d0fbb6934c4ec3d8a001',
        secret='d1471059e40c19e1a1fe',
        cluster='us2',
        ssl=True
)

hello = "Hello world!"
#Array of times
times = []
#The name of currencies stored in an array
currencies = ["BTC", "ETH", "LTC"]
#Prices and their prices stored in a array in a dictionary.
prices = {"BTC": [], "ETH": [], "LTC": []}


@app.route("/")
def index():
    return render_template("index.html")

def retrieve_data():
    #Create a dictionary of current Prices
    current_prices = {}
    #For each currency in currencies, initialize each with an empty array as key
    for currency in currencies:
        current_prices[currency] = []
        ##Debug - print current_prices dictionary
        print(current_prices)

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

    data = {
        'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
        'bar_chart': json.dumps(list(bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder)
    }

    #Trigger pusher event
    pusher.trigger("crypto", "data-updated", data)

#Get yearly data for cryptocoins
def yearly_data():
    monthly_keys = []
    monthly_btc_values = []

    api_url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market=CNY&apikey=demo"
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
    pusher.trigger("crypto", "month-updated", monthly_btc_data)



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

yearly_data()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


app.run(debug=True, use_reloader=False)
