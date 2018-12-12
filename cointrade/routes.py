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


#Array of times
times = []
#The name of currencies stored in an array
currencies = ["BTC"]
#Prices and their prices stored in a array in a dictionary.
prices = {"BTC": []}


#Home page for website
@app.route("/", methods=['POST', 'GET'])
def index():
    #r = requests.get('https://btc-api-heroku.herokuapp.com/api/user/2').json()
    #print(r)


    return render_template("index.html")

#Retrieve data from crypto api
def retrieve_data():
    #Create a dictionary of current Prices
    current_prices = {}
    #For each currency in currencies, initialize each with an empty array as key
    for currency in currencies:
        current_prices[currency] = []


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

    #Get most recent price
    bitcoinprice = prices["BTC"][len(prices["BTC"]) - 1]



#Route for registration page
@app.route("/register", methods=['GET', 'POST'])
def register():
    #If you are logged in and try to access login route, redirect to index page.
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    #If registration is good, add to database and let them now it was sucessful, redirect to login page
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, admin=False)

        db.session.add(user)

        db.session.commit()
        currency = Currency(btc=0, user_id=user.id, cash=25000)
        db.session.add(currency)
        db.session.commit()
        print(user.id)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#Route for login page
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
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Uncessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#Route for logout page
@app.route("/logout")
def logout():
    logout_user()
    #If you logout the user, take them back to index page
    return redirect(url_for('index'))

#Route for personal account
@app.route("/account")
@login_required
def account():
    #Get the amount of cash and btc from last transactions
    cash_amt = requests.get('https://btc-api-heroku.herokuapp.com/api/cash/' + str(current_user.id)).json()[str(current_user.id)]['cash']
    #users_currencies = strbtc[len(strbtc) - 1].btc
    users_currencies = requests.get('https://btc-api-heroku.herokuapp.com/api/bitcoins/' + str(current_user.id)).json()[str(current_user.id)]['btc']

    #Format cash into dollars
    cash_amt = "${:,.2f}".format(int(cash_amt))
    form = UpdateAccountForm()
    #Add image file later on
    #image_file = url_for('static', filename='image.png')
    #Add change email and username form later
    return render_template('account.html', title="Account", form=form, users_currencies=users_currencies, cash_amt=cash_amt)



#Get a table of the cryptocurrencies to buy
@app.route("/currencies", methods=['POST', 'GET'])
@login_required
def ctable():
    #Make request to the API before the page loads
    retrieve_data()
    #Call the API and get the users cash amount
    cash_amt = requests.get('https://btc-api-heroku.herokuapp.com/api/cash/' + str(current_user.id)).json()[str(current_user.id)]['cash']


    #Make API request to get bitcoin amt
    btc_amt = requests.get('https://btc-api-heroku.herokuapp.com/api/bitcoins/' + str(current_user.id)).json()[str(current_user.id)]['btc']

    #Format cash into dollar amount
    cash_amt_formatted = "${:,.2f}".format(int(cash_amt))
    #Get most recent price for bitcoins
    btc_price = prices["BTC"][len(prices["BTC"]) - 1]

    #Round the current btc price 2 places
    current_prices = [round(btc_price, 2)]
    #Format currency to a dollar amount
    current_btc_price_formatted = "${:,.2f}".format(current_prices[0])


    return render_template('currencies.html', title="currencies", btc_amt=btc_amt, cash_amt_formatted=cash_amt_formatted, current_btc_price_formatted = current_btc_price_formatted)

#Simulator menu screen
@app.route("/menu")
@login_required
def menu():
    return render_template('menu.html')


# Buy coins from table
@app.route('/buy', methods=['POST', 'GET'])
@login_required
def buy():

    #Call the API and get the users cash amount
    cash_amt = requests.get('https://btc-api-heroku.herokuapp.com/api/cash/' + str(current_user.id)).json()[str(current_user.id)]['cash']
    if 'buy_coins' in request.form:
        #Get users input from the form
        amount = request.form.get('buy_coins')
        #Get most recent bitcoin price
        price = prices["BTC"][len(prices["BTC"]) - 1]
        #Total cost of the bitcoins
        total_cost = int(amount) * price
        #If you don't have enough cash, return a message
        if int(cash_amt) < total_cost:
            message = 'NOT ENOUGH MONEY'
            return render_template('buy.html', message=message)
        #If you try to buy less than 0, return an error message
        if int(amount) < 0:
            message = 'MUST BE HIGHER THAN 0'
            return render_template('buy.html', message=message)

        else:
            #Make API request to get bitcoin amt
            btc_amt = requests.get('https://btc-api-heroku.herokuapp.com/api/bitcoins/' + str(current_user.id)).json()[str(current_user.id)]['btc']
            #Final amount of bitcoins
            final_amount = int(btc_amt) + int(amount)
            #Ending cost of the bitcoins
            final_cost = int(cash_amt) - total_cost
            #If the final cost is more than the cash you have
            if final_cost > int(cash_amt):
                message = 'NOT ENOUGH MONEY'
                return render_template('buy.html', message=message)
            #Update currency database
            currency = Currency(btc=int(final_amount), user_id=current_user.id, cash=int(final_cost))
            db.session.add(currency)
            db.session.commit()
            #Send message after you buy the coins
            message = 'BOUGHT ' + str(amount) + ' BITCOINS(s) FOR ' + "${:,.2f}".format(total_cost)
            return render_template('buy.html', price=price, total_cost=total_cost, amount=amount, message=message)

#Get table to sell coins
@app.route('/sell', methods=['POST', 'GET'])
@login_required
def sellcoins():
    retrieve_data()
    #Get current cash amt
    cash_amt = requests.get('https://btc-api-heroku.herokuapp.com/api/cash/' + str(current_user.id)).json()[str(current_user.id)]['cash']
    #Get most recent btc price
    btc_price = prices["BTC"][len(prices["BTC"]) - 1]
    #Format most recent price
    current_prices = ["${:,.2f}".format(btc_price)]

    users_currencies = requests.get('https://btc-api-heroku.herokuapp.com/api/bitcoins/' + str(current_user.id)).json()[str(current_user.id)]['btc']
    #Format cash amount
    cash_amt_formatted = "${:,.2f}".format(int(cash_amt))


    return render_template('sell.html', users_currencies=users_currencies, current_prices=current_prices, cash_amt_formatted=cash_amt_formatted)

#Confirm you're buying
@app.route('/confirmsell', methods=['POST', 'GET'])
@login_required
def confirmsell():

    #If user submits the sell coins form
    if 'sell_coins' in request.form:

        amount = request.form.get('sell_coins')

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
            message = 'SOLD ' + str(amount) + ' BITCOIN(s)'+ ' FOR ' + "${:,.2f}".format(total_cost)
            return render_template('sell-confirm.html', amount=amount, total_cost=total_cost, message=message)
        #If you try to sell more bitcoins than you have
        if int(amount) > int(users_currencies):
            message = 'NOT ENOUGH BITCOINS'
            return render_template('sell-confirm.html', message=message)


#Admin Panal
@app.route('/admin', methods=['GET'])
def adminpanal():
    #Make request for all usernames
    users = requests.get('https://btc-api-heroku.herokuapp.com/api/users').json()
    userids = []
    usernames = []
    #Get all usernames in the list of usernames
    userids.append(users.keys())

    return render_template('admin.html', users=users)



#Press Start Tv Screen
@app.route('/pressstart', methods=['GET'])
@login_required
def pressstart():
    return render_template('pressstart.html')

#Get Personal Statistics
@app.route('/stats', methods=['GET'])
@login_required
def stats():
    #Make an api request for btc prices
    retrieve_data()
    #Get most recent btc price
    bitcoinprice = prices["BTC"][len(prices["BTC"]) - 1]
    #Get users btc amount
    strbtc = Currency.query.filter_by(user_id=str(current_user.id)).all()
    bitcoins = strbtc[len(strbtc) - 1].btc
    #Round up the bitcoin value
    bit_value = round(int(bitcoins) * bitcoinprice, 2)
    bit_value_formatted = "${:,.2f}".format(bit_value)
    #Make array of cash amts
    cash = []
    #Make an array of all the dates
    dates = []
    #Make an array of the bitcoin amounts
    btcs = []
    currencies = Currency.query.filter_by(user_id=str(current_user.id)).all()
    profitLoss = round(25000 - 25000, 2)


    #Format all cash in the array
    for currency in currencies:
        cash.append("${:,.2f}".format(currency.cash))
        dates.append(currency.date_posted)
        btcs.append(currency.btc)
    #Get most recent cash amt
    current_cash = cash[len(cash) - 1]


    return render_template('stats.html', cash=cash, dates=dates, bit_value_formatted=bit_value_formatted, btcs=btcs, bitcoins=bitcoins, current_cash=current_cash)

#Chart route
@app.route("/chart")
def chart():
    #Get all values for the btc graph
    btc_values = []
    #Labels are the dates
    btc_labels = []
    #Get all values for the cash graph
    cash_values = []
    #Labels are the dates
    cash_labels = []

    currencies = Currency.query.filter_by(user_id=str(current_user.id)).all()
    #Go through the users bitcoin amts
    for currency in currencies:
        btc_values.append(currency.btc)
        btc_labels.append(currency.date_posted)
    #Go through the users cash amts
    for currency in currencies:
        cash_values.append(currency.cash)
        cash_labels.append(currency.date_posted)

    return render_template('chart.html', btc_values=btc_values, btc_labels=btc_labels, cash_values=cash_values, cash_labels=cash_labels )

#About Page Route
@app.route("/about")
def about():
    title = 'About'
    return render_template('about.html', title=title)
