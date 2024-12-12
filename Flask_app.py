pip install Flask yfinance sqlite3
from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import sqlite3

app = Flask(__name__)

# SQLite Database setup (for simplicity)
DATABASE = 'portfolio.db'

# Helper function to get database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Helper function to initialize database
def init_db():
    with app.app_context():
        conn = get_db()
        conn.execute('''CREATE TABLE IF NOT EXISTS portfolio
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         symbol TEXT NOT NULL,
                         quantity INTEGER NOT NULL,
                         purchase_price REAL NOT NULL)''')
        conn.commit()

# Get real-time stock data
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    current_price = data['Close'].iloc[0]
    return current_price

# Home route to display portfolio
@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolio")
    stocks = cursor.fetchall()
    portfolio_value = 0
    for stock in stocks:
        current_price = get_stock_data(stock[1])
        stock_value = current_price * stock[2]
        portfolio_value += stock_value
    return render_template('index.html', stocks=stocks, portfolio_value=portfolio_value)

# Route to add a new stock
@app.route('/add', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        quantity = int(request.form['quantity'])
        purchase_price = float(request.form['purchase_price'])
        conn = get_db()
        conn.execute("INSERT INTO portfolio (symbol, quantity, purchase_price) VALUES (?, ?, ?)",
                     (symbol, quantity, purchase_price))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('add_stock.html')

# Route to remove a stock
@app.route('/remove/<int:stock_id>', methods=['GET'])
def remove_stock(stock_id):
    conn = get_db()
    conn.execute("DELETE FROM portfolio WHERE id = ?", (stock_id,))
    conn.commit()
    return redirect(url_for('index'))

# Run app
if __name__ == '__main__':
    init_db()  # Initialize database if not already done
    app.run(debug=True)
