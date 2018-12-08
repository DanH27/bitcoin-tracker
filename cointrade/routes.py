from flask import render_template, url_for, flash, redirect, jsonify
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
currencies = ["BTC", "LTC", "NMC", "PPC", "XPM", "XLM", "ETH"]
#Prices and their prices stored in a array in a dictionary.
prices = {"BTC": [], "LTC": [], "NMC": [],
"PPC": [], "XPM": [], "XLM": [], "ETH": []}



@app.route("/", methods=['POST', 'GET'])
def index():

    #if request.method == 'POST':

    #    print("HEY")

    return render_template("start.html", moneyLeft=moneyLeft, bitcoinprice=bitcoinprice)


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
    #dogecoinprice = prices["DOGE"][len(prices["DOGE"]) - 1]
    nmcprice = prices["NMC"][len(prices["NMC"]) - 1]
    #bytecoinprice = prices["BCN"][len(prices["BCN"]) - 1]
    peercoinprice = prices["PPC"][len(prices["PPC"]) - 1]
    #feathercoinprice = prices["FTC"][len(prices["FTC"]) - 1]
    #gridcoinprice = prices["GRC"][len(prices["GRC"]) - 1]
    xpmcoinprice = prices["XPM"][len(prices["XPM"]) - 1]
    #auroracoinprice = prices["AUR"][len(prices["AUR"]) - 1]
    #mazacoinprice = prices["MZC"][len(prices["MZC"]) - 1]
    #potcoinprice = prices["POT"][len(prices["POT"]) - 1]
    stellarcoinprice = prices["XLM"][len(prices["XLM"]) - 1]
    ethereiumcoinprice = prices["ETH"][len(prices["ETH"]) - 1]


    data = {
        'graph': json.dumps(list(graph_data), cls=plotly.utils.PlotlyJSONEncoder),
        'bar_chart': json.dumps(list(bar_chart_data), cls=plotly.utils.PlotlyJSONEncoder),
        'btc_price': bitcoinprice,
        'money_left': moneyLeft,
        'ltc_price': litcoinprice,
        #'doge_price': dogecoinprice,
        'nmc_price': nmcprice,
        #'bcn_price': bytecoinprice,
        'ppc_price': peercoinprice,
        #'ftc_price': feathercoinprice,
        #'grc_price': gridcoinprice,
        'xpm_price': xpmcoinprice,
        #'aur_price': auroracoinprice,
        #'mzc_price': mazacoinprice,
        #'pot_price': potcoinprice,
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
        currency = Currency(btc=0, user_id=user.id, cash=25000)
        db.session.add(currency)
        db.session.commit()
        print(user.id)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
    return redirect(url_for('index'))

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

    cash_amt_formatted = "${:,.2f}".format(cash_amt)

    btc_price = prices["BTC"][len(prices["BTC"]) - 1]
    litcoinprice = prices["LTC"][len(prices["LTC"]) - 1]
    #dogecoinprice = prices["DOGE"][len(prices["DOGE"]) - 1]
    nmcprice = prices["NMC"][len(prices["NMC"]) - 1]
    #bytecoinprice = prices["BCN"][len(prices["BCN"]) - 1]
    peercoinprice = prices["PPC"][len(prices["PPC"]) - 1]
    #feathercoinprice = prices["FTC"][len(prices["FTC"]) - 1]
    #gridcoinprice = prices["GRC"][len(prices["GRC"]) - 1]
    xpmcoinprice = prices["XPM"][len(prices["XPM"]) - 1]
    #auroracoinprice = prices["AUR"][len(prices["AUR"]) - 1]
    #mazacoinprice = prices["MZC"][len(prices["MZC"]) - 1]
    #potcoinprice = prices["POT"][len(prices["POT"]) - 1]
    stellarcoinprice = prices["XLM"][len(prices["XLM"]) - 1]
    ethereiumcoinprice = prices["ETH"][len(prices["ETH"]) - 1]

    current_prices = [round(btc_price, 2), round(ethereiumcoinprice, 2), round(litcoinprice, 2), round(nmcprice, 2), round(peercoinprice, 2), round(xpmcoinprice,2), round(stellarcoinprice, 2)]

    current_btc_price_formatted = "${:,.2f}".format(current_prices[0])





    # if request.method == 'POST':
    #     return "POSTED"
    # else:
        #query = cursor.execute("SELECT * FROM books")
        #print(str("sdfdsf") + str(query))

    return render_template('currencies.html', title="currencies", btc_amt=btc_amt, cash_amt_formatted=cash_amt_formatted, current_btc_price_formatted = current_btc_price_formatted)

@app.route("/main")
def main():
    return render_template('main.html')


# Buy stocks from table
@app.route('/buy', methods=['POST', 'GET'])
@login_required
def buy():
    error_message = "NOT ENOUGH MONEY"
    cash_amt_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
    cash_amt = cash_amt_tmp[len(cash_amt_tmp) - 1].cash
    print(request.form)
    if 'buy_coins' in request.form:
        #print(current_user.id)
        print(current_user.currency)
        amount = request.form.get('buy_coins')
        coin_name = 'Bitcoin'
        price = prices["BTC"][len(prices["BTC"]) - 1]
        total_cost = int(amount) * price
        if cash_amt < total_cost:
            return render_template('buy.html', error_message=error_message)
        else:
            btc_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
            btc_amt = btc_tmp[len(btc_tmp) - 1].btc
            final_amount = int(btc_amt) + int(amount)
            final_cost = cash_amt - total_cost
            currency = Currency(btc=int(final_amount), user_id=current_user.id, cash=int(final_cost))
            db.session.add(currency)
            db.session.commit()
            return render_template('buy.html', price=price, coin_name=coin_name, total_cost=total_cost, amount=amount)


@app.route('/sell', methods=['POST', 'GET'])
@login_required
def sellcoins():
    retrieve_data()
    cash_amt_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
    cash_amt = cash_amt_tmp[len(cash_amt_tmp) - 1].cash
    btc_price = prices["BTC"][len(prices["BTC"]) - 1]
    current_prices = [btc_price]
    strbtc = Currency.query.filter_by(user_id=str(current_user.id)).all()
    users_currencies = strbtc[len(strbtc) - 1].btc
    btc_tmp = Currency.query.filter_by(user_id=str(current_user.id)).all()
    btc_amt = btc_tmp[len(btc_tmp) - 1].btc

    if btc_amt <= 0:
        current_profit_loss = 0
    else:
        current_profit_loss = round((cash_amt + (btc_amt * btc_price)) - 25000, 2)

    return render_template('sell.html', users_currencies=users_currencies, current_prices=current_prices, current_profit_loss=current_profit_loss)

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

#Get all usernames
@app.route('/api/usernames', methods=['GET'])
def getusernames():
    usernames = {}
    budget_tmp = User.query.all()
    for item in budget_tmp:
        usernames[str(item.id)] = {}
    for item in budget_tmp:
        usernames[str(item.id)]['username'] = str(item.username)
        usernames[str(item.id)]['email'] = str(item.email)
    print(usernames)
    return jsonify(usernames)

#Get one username
@app.route('/api/usernames/<user_id>', methods=['GET'])
def getuser(user_id):
    user_dict = {}
    user = User.query.filter_by(id=user_id).first()
    user_dict[str(user.id)] = {}
    user_dict[str(user.id)]['username'] = str(user.username)
    user_dict[str(user.id)]['email'] = str(user.email)
    print(user_dict)


    return jsonify(user_dict)


#Get all currency trades
@app.route('/api/trades/', methods=['GET'])
def gettrades():
    trades_dict = {}
    trades = Currency.query.all()

    for trade in trades:
        trades_dict[str(trade.user_id)] = {}
    for trade in trades:
        trades_dict[str(trade.user_id)]['btc'] = str(trade.btc)

    return jsonify(trades_dict)


#Get specific user btc amt
@app.route('/api/trades/<id>', methods=['GET'])
def gettrade(id):
    trade_dict = {}
    trade = Currency.query.filter_by(user_id=id).all()
    last_trade = trade[len(trade) - 1]
    trade_dict[str(last_trade.user_id)] = {}
    trade_dict[str(last_trade.user_id)]['btc'] = str(last_trade.btc)

    return jsonify(trade_dict)




#High Scores Table - Add Later
@app.route('/start', methods=['GET'])
@login_required
def start():
    #############API TEST WORKS################
    r = requests.get('http://127.0.0.1:5000/api/trades/')
    print(r.json())
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
    bit_value_formatted = "${:,.2f}".format(bit_value)
    cash = []
    dates = []
    btcs = []
    currencies = Currency.query.filter_by(user_id=str(current_user.id)).all()
    profitLoss = round(25000 - 25000, 2)



    for currency in currencies:
        cash.append("${:,.2f}".format(currency.cash))
        dates.append(currency.date_posted)
        btcs.append(currency.btc)

    current_cash = cash[len(cash) - 1]


    return render_template('stats.html', cash=cash, dates=dates, bit_value_formatted=bit_value_formatted, btcs=btcs, bitcoins=bitcoins, current_cash=current_cash)

@app.route("/chart")
def chart():
    values = []
    labels = []

    cash_values = []
    cash_labels = []

    currencies = Currency.query.filter_by(user_id=str(current_user.id)).all()
    for currency in currencies:
        values.append(currency.btc)
        labels.append(currency.date_posted)

    for currency in currencies:
        cash_values.append(currency.cash)
        cash_labels.append(currency.date_posted)

    return render_template('chart.html', values=values, labels=labels, cash_values=cash_values, cash_labels=cash_labels )


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
