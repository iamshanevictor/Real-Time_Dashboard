import random
import time
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from threading import Thread

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bitcoin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define HistoricalPrice model for Bitcoin
class HistoricalPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Define a similar model for Ethereum
class EthereumPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
def create_databases():
    with app.app_context():
        db.create_all()

create_databases()

# Function to generate a random price with limited volatility
def generate_price(previous_price):
    # Generate a change percentage between -3% to -1% or 1% to 3%
    change_percent = random.uniform(0.01, 0.03) * random.choice([-1, 1])
    new_price = previous_price * (1 + change_percent)
    return round(new_price, 2)

# Function to simulate price generation
def generate_bitcoin_price():
    previous_price = 10000.00  # Initial price
    while True:
        time.sleep(5)
        new_price = generate_price(previous_price)
        previous_price = new_price
        # Store the new price in the database
        with app.app_context():
            new_record = HistoricalPrice(price=new_price)
            db.session.add(new_record)
            db.session.commit()

def generate_ethereum_price():
    previous_price = 2000.00  # Initial price
    while True:
        time.sleep(5)
        new_price = generate_price(previous_price)
        previous_price = new_price
        # Store the new price in the database
        with app.app_context():
            new_record = EthereumPrice(price=new_price)
            db.session.add(new_record)
            db.session.commit()

# Routes for rendering the index page
@app.route('/')
def index():
    bitcoin_prices = HistoricalPrice.query.order_by(HistoricalPrice.timestamp.desc()).limit(5).all()
    ethereum_prices = EthereumPrice.query.order_by(EthereumPrice.timestamp.desc()).limit(5).all()
    
    price_history = [(price.timestamp.strftime("%Y-%m-%d %H:%M:%S"), price.price) for price in bitcoin_prices]
    ethereum_price_history = [(price.timestamp.strftime("%Y-%m-%d %H:%M:%S"), price.price) for price in ethereum_prices]
    
    return render_template('index.html', price_history=price_history, ethereum_price_history=ethereum_price_history)

# API routes for current price
@app.route('/api/bitcoin')
def bitcoin_api():
    last_record = HistoricalPrice.query.order_by(HistoricalPrice.timestamp.desc()).first()
    current_price = last_record.price if last_record else 0.0
    return jsonify(current_price=current_price)

@app.route('/api/ethereum')
def ethereum_api():
    last_record = EthereumPrice.query.order_by(EthereumPrice.timestamp.desc()).first()
    current_price = last_record.price if last_record else 0.0
    return jsonify(current_price=current_price)

# Start the price generation threads
if __name__ == '__main__':
    Thread(target=generate_bitcoin_price).start()
    Thread(target=generate_ethereum_price).start()
    app.run(debug=True)
