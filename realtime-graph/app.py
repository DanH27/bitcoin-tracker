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

#Array of times
times = []
#The name of currencies stored in an array
currencies = ["BTC"]
#Prices and their prices stored in a array in a dictionary.
prices = {"BTC": []}


@app.route("/")
def index():
    return render_template("index.html")
