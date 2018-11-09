import os
import mysql.connector

from decimal import Decimal
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, credit_card

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to MySQL database
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    passwd=DB_PSWD,
    database=DB_NAME,
)
cursor = db.cursor(dictionary=True)


@app.route("/")
@login_required
def index():
    """Shows user's portfolio"""
    cursor.execute("SELECT * FROM portfolio WHERE id=%s", (session["user_id"],))
    user_stocks = cursor.fetchall()

    stock_holdings = 0

    # Get current prices and update portfolio
    for stock in user_stocks:
        stock_symbol = stock["symbol"]
        stock_shares = stock["shares"]
        stock_info = lookup(stock_symbol)
        share_price = stock_info["price"]
        total_price = stock_shares * share_price
        stock_holdings += total_price
        cursor.execute(
            "UPDATE portfolio SET price=%s, total=%s WHERE id=%s AND symbol=%s", 
            (share_price, total_price, session["user_id"], stock_symbol)
        )
        db.commit()

    # Get user's available cash
    cursor.execute(
        "SELECT cash FROM users WHERE id=%s", 
        (session["user_id"],)
    )
    available_cash = cursor.fetchone()

    # Add user's available cash to total holdings
    grand_total = available_cash["cash"] + Decimal(stock_holdings)

    # If shares are equal to 0 then delete from portfolio
    cursor.execute(
        "DELETE FROM portfolio WHERE id=%s AND shares=0", 
        (session["user_id"],)
    )

    # Get current portfolio
    cursor.execute(
        "SELECT * FROM portfolio WHERE id=%s ORDER BY symbol", 
        (session["user_id"],)
    )
    current_portfolio = cursor.fetchall()

    return render_template(
        "index.html", 
        stocks=current_portfolio, 
        user_cash=usd(available_cash["cash"]), 
        grand_total=usd(grand_total)
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        shares_buying = int(request.form.get("shares"))

        # Look up stock information
        stock_info = lookup(request.form.get("symbol"))

        # Ensure symbol is valid
        if not stock_info:
            return apology("invalid symbol")

        # Variable for stock name
        symbol_buying = stock_info["symbol"]

        # Variable for stock price
        share_price = float(stock_info["price"])

        # Get user's cash
        cursor.execute(
            "SELECT cash FROM users WHERE id=%s", 
            (session["user_id"],)
        )
        available_cash = cursor.fetchone()

        # Variable for the total purchase price
        purchase_price = share_price * shares_buying

        # Check if user can afford the shares
        if not available_cash or float(available_cash["cash"]) < purchase_price:
            return apology("not enough cash available")

        # Update user's history
        cursor.execute(
            "INSERT INTO history (id, symbol, transactions, price) VALUES (%s, %s, %s, %s)", 
            (session["user_id"], symbol_buying, shares_buying, share_price)
        )
        db.commit()

        # Check if user already owns shares from a company
        cursor.execute(
            "SELECT shares FROM portfolio WHERE id=%s AND symbol=%s", 
             (session["user_id"], symbol_buying)
        )
        has_shares = cursor.fetchall()

        # If user doesn't have shares from a company, insert into portfolio
        if not has_shares:
            cursor.execute(
                "INSERT INTO portfolio (id, symbol, name_, shares, price, total) \
                VALUES (%s, %s, %s, %s, %s, %s)",
                (session["user_id"], symbol_buying, stock_info["name"], shares_buying, share_price, purchase_price)
            )
            db.commit()
                
        # If user does have shares from the company, update portfolio
        else:
            cursor.execute(
                "UPDATE portfolio SET shares=shares+%s WHERE id=%s", 
                (shares_buying, session["user_id"])
            )
            db.commit()

        # Update user's available cash
        cursor.execute(
            "UPDATE users SET cash=cash-%s WHERE id=%s", 
            (purchase_price, session["user_id"])
        )
        db.commit()

        # Redirect user to home page
        flash("Bought successfully!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get user's history
    cursor.execute(
        "SELECT * FROM history WHERE id=%s ORDER BY time_", 
        (session["user_id"],) 
    )
    user_history = cursor.fetchall()

    return render_template("history.html", histories=user_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (request.form.get("username"),)
        )
        row = cursor.fetchone()

        # Ensure username exists and password is correct
        if not row or not check_password_hash(row["hash_"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row["id"]

        # Redirect user to home page
        flash("Login successful!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Look up stock information
        stock_info = lookup(request.form.get("symbol"))

        # Ensure stock exists
        if not stock_info:
            return apology("invalid symbol")

        # Show user stock information
        return render_template("quoted.html", stock=stock_info, price=usd(stock_info["price"]))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Add registered user into database
        try:
            cursor.execute(
                "INSERT INTO users (username, hash_, keyword) VALUES (%s, %s, %s)",
                    (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("keyword"))
            )
            db.commit()
        except:
            return apology("Username already exists")

        # Remember which user has logged in
        session["user_id"] = cursor.lastrowid

        # Redirect user to home page
        flash("Registered successfully!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Query database for user's stocks
    cursor.execute(
        "SELECT * FROM portfolio WHERE id=%s", 
        (session["user_id"],)
    )
    user_stocks = cursor.fetchall()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Look up stock information
        stock_info = lookup(request.form.get("symbol"))

        # Variable for number of shares trying to sell
        shares_selling = int(request.form.get("shares"))

        # Get number of shares user owns
        cursor.execute(
            "SELECT shares FROM portfolio WHERE id=%s AND symbol=%s",
            (session["user_id"], stock_info["symbol"])
        )
        user_shares = cursor.fetchone()

        # Check if user has enough shares to sell
        if user_shares["shares"] < shares_selling:
            return apology("you don't own enough shares")

        # Variable for price of the share
        share_price = float(stock_info["price"])

        # Variable for the total price of the sale
        sale_price = shares_selling * share_price

        # Update user's history to show a sell transaction
        cursor.execute(
            "INSERT INTO history (id, symbol, transactions, price) VALUES (%s, %s, %s, %s)",
            (session["user_id"], stock_info["symbol"], -shares_selling, share_price)
        )
        db.commit()

        # Update user's portfolio by deleting shares sold
        cursor.execute(
            "UPDATE portfolio SET shares=shares-%s, total=total-%s WHERE id=%s AND symbol=%s",
            (shares_selling, sale_price, session["user_id"], stock_info["symbol"])
        )
        db.commit()

        # Update user's available cash
        cursor.execute(
            "UPDATE users SET cash=cash+%s WHERE id=%s",
            (sale_price, session["user_id"])
        )
        db.commit()

        # Redirect user to home page
        flash("Sold successfully!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", stocks=user_stocks)


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    """Add more cash"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        new_money = request.form.get("new_money")
        cc_number = request.form.get("credit_number")

        # Ensure credit card number is valid
        credit_card(int(cc_number))
        if not cc_number or credit_card(int(cc_number)) == "INVALID":
            return apology("Invalid credit card number")

        # Add new money to user's available cash      
        cursor.execute(
            "UPDATE users SET cash=cash+%s WHERE id=%s",
            (new_money, session["user_id"])
        )
        db.commit()

        # Redirect user to home page
        flash("Deposited money successfully with your " + credit_card(int(cc_number)) + " credit card!")
        return redirect("/")

    else:
        return render_template("deposit.html")


@app.route("/password-reset", methods=["GET", "POST"])
def passwordreset():
    """Allow users to reset password"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username and keyword       
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND keyword=%s",
            (request.form.get("username"), request.form.get("keyword"))
        )

        # Ensure username/keyword combination exists
        if not cursor.fetchone():
            return apology("Username/Keyword combination invalid")

        # Update user's new password
        cursor.execute(
            "UPDATE users SET hash_=%s WHERE username=%s",
            (generate_password_hash(request.form.get("new_password")), request.form.get("username"))
        )
        db.commit()

        # Redirect user to home page
        return redirect("/password-reset-success")

    else:
        return render_template("password-reset.html")


@app.route("/password-reset-success")
def resetsuccess():
    return render_template("password-reset-success.html")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)