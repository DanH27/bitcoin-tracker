from flask import render_template, url_for, flash, redirect
from cointrade import app, db, bcrypt
from cointrade.forms import RegistrationForm, LoginForm, UpdateAccountForm
from cointrade.models import User, Currency
from pusher import Pusher
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import request
import requests, json, atexit, time, plotly, plotly.graph_objs as go
from flask_login import login_user, current_user, logout_user, login_required
from flaskext.mysql import MySQL





# configure pusher object
pusher = Pusher(
        app_id='625209',
        key='d0fbb6934c4ec3d8a001',
        secret='d1471059e40c19e1a1fe',
        cluster='us2',
        ssl=True
)

# mysql = MySQL()
#
# # MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'root'
#
# app.config['MYSQL_DATABASE_DB'] = 'flaskapi'
# mysql.init_app(app)
# conn = mysql.connect()
# cursor = conn.cursor()

hello = "Hello world!"
moneyLeft = 100000
bitcoinprice = 0
currentBudget = 0
#Array of times
times = []
#The name of currencies stored in an array
currencies = ["BCN", "BTC", "LTC", "NMC", "DOGE", "PPC", "FTC", "GRC", "XPM", "AUR" ,"MZC", "POT", "XLM", "ETH"]
#Prices and their prices stored in a array in a dictionary.
prices = {"BCN": [], "BTC": [], "LTC": [], "DOGE": [], "NMC": [],
"PPC": [], "FTC": [], "GRC": [], "XPM": [], "AUR": [],
"MZC": [], "POT": [], "XLM": [], "ETH": []}



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
    nmcprice = prices["NMC"][len(prices["NMC"]) - 1]
    bytecoinprice = prices["BCN"][len(prices["BCN"]) - 1]
    peercoinprice = prices["PPC"][len(prices["PPC"]) - 1]
    feathercoinprice = prices["FTC"][len(prices["FTC"]) - 1]
    gridcoinprice = prices["GRC"][len(prices["GRC"]) - 1]
    xpmcoinprice = prices["XPM"][len(prices["XPM"]) - 1]
    auroracoinprice = prices["AUR"][len(prices["AUR"]) - 1]
    mazacoinprice = prices["MZC"][len(prices["MZC"]) - 1]
    potcoinprice = prices["POT"][len(prices["POT"]) - 1]
    stellarcoinprice = prices["XLM"][len(prices["XLM"]) - 1]
    ethereiumcoinprice = prices["ETH"][len(prices["ETH"]) - 1]


    data = {
        'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
        'bar_chart': json.dumps(list(bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder),
        'btc_price': bitcoinprice,
        'money_left': moneyLeft,
        'ltc_price': litcoinprice,
        'doge_price': dogecoinprice,
        'nmc_price': nmcprice,
        'bcn_price': bytecoinprice,
        'ppc_price': peercoinprice,
        'ftc_price': feathercoinprice,
        'grc_price': gridcoinprice,
        'xpm_price': xpmcoinprice,
        'aur_price': auroracoinprice,
        'mzc_price': mazacoinprice,
        'pot_price': potcoinprice,
        'xlm_price': stellarcoinprice,
        'eth_price': ethereiumcoinprice
    }

    #Trigger pusher event
    ##pusher.trigger("crypto", "data-updated", data)



@app.route("/btc")
def btc_dash():
#    yearly_data1('2b. high (USD)', 'BTC')
    return render_template("individual.html", data="sdfs")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        db.session.add(user)

        db.session.commit()
        currency = Currency(btc=0, user_id=user.id, cash=100000)
        db.session.add(currency)
        db.session.commit()
        print(user.id)
        flash('Youur account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('start'))
        else:
            flash('Login Uncessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('start'))

@app.route("/account")
@login_required
def account():
    strbtc = Currency.query.filter_by(user_id=str(current_user.id)).all()
    cash_amt = Currency.query.filter_by(user_id=str(current_user.id)).all()
    cash_amt_tmp = cash_amt[len(cash_amt) - 1].cash
    users_currencies = strbtc[len(strbtc) - 1].btc

    #Most recent cash amount
    print(cash_amt_tmp)

    #print the current users bitcoins
    #print(strbtc.btc)
    form = UpdateAccountForm()
    image_file = url_for('static', filename='image.png')
    return render_template('account.html', title="Account", image_file=image_file, form=form, users_currencies=users_currencies, cash_amt_tmp=cash_amt_tmp)



@app.route("/currencies", methods=['POST', 'GET'])
@login_required
def ctable():
    retrieve_data()
    cash_amt_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
    cash_amt = cash_amt_tmp[len(cash_amt_tmp) - 1].cash
    btc_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
    btc_amt = btc_tmp[len(btc_tmp) - 1].btc


    btc_price = prices["BTC"][len(prices["BTC"]) - 1]
    litcoinprice = prices["LTC"][len(prices["LTC"]) - 1]
    dogecoinprice = prices["DOGE"][len(prices["DOGE"]) - 1]
    nmcprice = prices["NMC"][len(prices["NMC"]) - 1]
    bytecoinprice = prices["BCN"][len(prices["BCN"]) - 1]
    peercoinprice = prices["PPC"][len(prices["PPC"]) - 1]
    feathercoinprice = prices["FTC"][len(prices["FTC"]) - 1]
    gridcoinprice = prices["GRC"][len(prices["GRC"]) - 1]
    xpmcoinprice = prices["XPM"][len(prices["XPM"]) - 1]
    auroracoinprice = prices["AUR"][len(prices["AUR"]) - 1]
    mazacoinprice = prices["MZC"][len(prices["MZC"]) - 1]
    potcoinprice = prices["POT"][len(prices["POT"]) - 1]
    stellarcoinprice = prices["XLM"][len(prices["XLM"]) - 1]
    ethereiumcoinprice = prices["ETH"][len(prices["ETH"]) - 1]

    current_prices = [auroracoinprice, btc_price, bytecoinprice, dogecoinprice, ethereiumcoinprice, feathercoinprice, gridcoinprice, litcoinprice, mazacoinprice, nmcprice, peercoinprice, xpmcoinprice, potcoinprice, stellarcoinprice]

    # if request.method == 'POST':
    #     return "POSTED"
    # else:
        #query = cursor.execute("SELECT * FROM books")
        #print(str("sdfdsf") + str(query))

    return render_template('currencies.html', title="currencies", btc_amt=btc_amt, cash_amt=cash_amt, current_prices = current_prices)

@app.route("/main")
def main():
    return render_template('main.html')

@app.route("/wallet")
def wallet():
    return render_template('wallet.html', title="Wallet")


# Buy stocks from table
@app.route('/buy', methods=['POST', 'GET'])
@login_required
def buy():
    error_message = "NOT ENOUGH MONEY"
    budget_tmp = Currency.query.filter_by(user_id=str(current_user.id)).first()
    budget = budget_tmp.cash
    print(request.form)
    if 'buy_coins' in request.form:
        #print(current_user.id)
        print(current_user.currency)
        amount = request.form.get('buy_coins')
        coin_name = 'Bitcoin'
        price = prices["BTC"][len(prices["BTC"]) - 1]
        total_cost = int(amount) * price
        if budget < total_cost:
            return render_template('currencies.html', error_message=error_message)
        else:
            btc_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
            btc_amt = btc_tmp[len(btc_tmp) - 1].btc
            final_amount = int(btc_amt) + int(amount)
            final_cost = budget - total_cost
            currency = Currency(btc=int(final_amount), user_id=current_user.id, cash=int(final_cost))
            db.session.add(currency)
            db.session.commit()
            return render_template('buy.html', price=price, coin_name=coin_name, total_cost=total_cost, amount=amount)

    #budget = 100000
    #select = request.form.get('buy_coins')

    #selected_coin = request.args.get('type')
    #return "Buy a " + str(selected_coin) + "for " + str(prices[str(selected_coin)][len(prices[str(selected_coin)]) - 1])
    #price = prices[str(selected_coin)][len(prices[str(selected_coin)]) - 1]
    #return render_template('buy.html')
    # bitcoinprice = prices["BTC"][len(prices["BTC"]) - 1]
    # if (budget - (int(bitcoinprice) * int(select)) >= 0):
    #     return "<h1>Buy " + str(select) + " bitcoin(s) for "  + "$" + str(int(bitcoinprice) * int(select)) +"s?" + "</h1>" # just to see what select is
    # else:
    #     return render_template("index.html", moneyLeft=moneyLeft, bitcoinprice=bitcoinprice)
@app.route('/sell', methods=['POST', 'GET'])
@login_required
def sellcoins():
    strbtc = Currency.query.filter_by(user_id=str(current_user.id)).all()
    users_currencies = strbtc[len(strbtc) - 1].btc
    return render_template('sell.html', users_currencies=users_currencies)

#Confirm you buying
@app.route('/confirmsell', methods=['POST', 'GET'])
@login_required
def confirmsell():

    if 'sell_coins' in request.form:
        #print(current_user.id)
        print(current_user.currency)
        amount = request.form.get('sell_coins')
        coin_name = 'Bitcoin'
        price = prices["BTC"][len(prices["BTC"]) - 1]
        total_cost = int(amount) * price
        strbtc = Currency.query.filter_by(user_id=str(current_user.id)).all()
        users_currencies = strbtc[len(strbtc) - 1].btc
        if int(amount) <= users_currencies and int(amount) > 0:
            budget_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
            budget = budget_tmp[len(budget_tmp) - 1].cash
            new_cash_amt = budget + total_cost

            new_btc_amt = users_currencies - int(amount)
            currency = Currency(btc=int(new_btc_amt), user_id=current_user.id, cash=int(new_cash_amt))
            db.session.add(currency)
            db.session.commit()
            return render_template('sell-confirm.html', amount=amount, total_cost=total_cost, coin_name=coin_name)

        else:
            return render_template('sell.html')

#High Scores Table - Add Later
@app.route('/highscores', methods=['GET'])
def highscores():
    currencies = Currency.query.limit(10).all()
    for currency in currencies:
        print(currency.user_id)
    return render_template('highscores.html')


#High Scores Table - Add Later
@app.route('/start', methods=['GET'])
@login_required
def start():
    return render_template('start.html')

#Press Start Tv Screen
@app.route('/pressstart', methods=['GET'])
@login_required
def pressstart():
    return render_template('pressstart.html')

#Get Personal Statistics
@app.route('/stats', methods=['GET'])
@login_required
def stats():
    retrieve_data()
    bitcoinprice = prices["BTC"][len(prices["BTC"]) - 1]
    strbtc = Currency.query.filter_by(user_id=str(current_user.id)).all()
    bitcoins = strbtc[len(strbtc) - 1].btc
    bit_value = round(int(bitcoins) * bitcoinprice, 2)
    cash = []
    dates = []
    currencies = Currency.query.filter_by(user_id=str(current_user.id)).all()
    for currency in currencies:
        cash.append(currency.cash)
        dates.append(currency.date_posted)
    return render_template('stats.html', cash=cash, dates=dates, bit_value=bit_value)

# create schedule for retrieving prices
##scheduler = BackgroundScheduler()
##scheduler.start()
##scheduler.add_job(
##    func=retrieve_data,
##    trigger = IntervalTrigger(seconds=30),
##    id='prices_retrieval_job',
##    name='Retrieve prices every 30 seconds',
##    replace_existing = True
#    )


# Shut down the scheduler when exiting the app
##atexit.register(lambda: scheduler.shutdown())
