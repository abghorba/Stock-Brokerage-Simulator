from decimal import Decimal

import mysql.connector
from flask import Flask, flash, g, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from config import SECRET_KEY, MySQL_DB
from helpers import apology, login_required, lookup, usd

# Configure application
application = Flask(__name__)
application.secret_key = SECRET_KEY

# Ensure templates are auto-reloaded
application.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@application.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
application.jinja_env.filters["usd"] = usd

# Parameters for MySQL database
params = {
    "host": MySQL_DB.DB_HOST,
    "user": MySQL_DB.DB_USER,
    "passwd": MySQL_DB.DB_PASSWORD,
    "database": MySQL_DB.DB_NAME,
}


def open_database():
    """Opens a new database connection if there is none yet"""
    if not hasattr(g, "db"):
        g.db = mysql.connector.connect(**params)
        g.cursor = g.db.cursor(dictionary=True)
    return g.db, g.cursor


@application.teardown_appcontext
def close_database(error):
    """Closes the database connection at the end of the request"""
    if hasattr(g, "db"):
        g.db.close()


@application.route("/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Query database for username
        db, cursor = open_database()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s", (request.form.get("username"),)
        )
        row = cursor.fetchone()

        # Ensure username exists and password is correct
        if not row or not check_password_hash(
            row["hash_"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row["id"]
        print(row["id"])
        print(session["user_id"])

        # Redirect user to home page
        flash("Login successful!")
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@application.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Add registered user into database
        try:
            db, cursor = open_database()
            cursor.execute(
                "INSERT INTO users (username, hash_, keyword) VALUES (%s, %s, %s)",
                (
                    request.form.get("username"),
                    generate_password_hash(request.form.get("password")),
                    request.form.get("keyword"),
                ),
            )
            db.commit()
        except Exception as e:
            print(e)
            return apology("Username already exists")

        # Remember which user has logged in
        session["user_id"] = cursor.lastrowid

        # Redirect user to home page
        flash("Registered successfully!")
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@application.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@application.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    """Allow users to reset password"""
    db, cursor = open_database()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Query database for username and keyword
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND keyword=%s",
            (request.form.get("username"), request.form.get("keyword")),
        )

        # Ensure username/keyword combination exists
        if not cursor.fetchone():
            return apology("Username/Keyword combination invalid")

        # Update user's new password
        cursor.execute(
            "UPDATE users SET hash_=%s WHERE username=%s",
            (
                generate_password_hash(request.form.get("new_password")),
                request.form.get("username"),
            ),
        )
        db.commit()

        # Redirect user to success landing page
        return redirect("/password-reset-success")

    else:
        return render_template("password-reset.html")


@application.route("/password-reset-success")
def reset_success():
    return render_template("password-reset-success.html")


@application.route("/portfolio")
@login_required
def portfolio():
    """Shows user's portfolio"""
    db, cursor = open_database()
    cursor.execute(
        "SELECT * FROM portfolio WHERE id=%s",
        (session["user_id"],),
    )
    user_stocks = cursor.fetchall()

    total_stock_value = 0

    # Get current prices and update portfolio
    for stock in user_stocks:
        stock_symbol = stock["symbol"]
        owned_shares = stock["shares"]
        stock_info = lookup(stock_symbol)
        market_price_per_share = float(stock_info["price"])
        total_market_price = owned_shares * market_price_per_share
        total_stock_value += total_market_price
        cursor.execute(
            "UPDATE portfolio SET price=%s, total=%s WHERE id=%s AND symbol=%s",
            (
                market_price_per_share,
                total_market_price,
                session["user_id"],
                stock_symbol,
            ),
        )
        db.commit()

    # If shares are equal to 0 then delete from portfolio
    cursor.execute(
        "DELETE FROM portfolio WHERE id=%s AND shares=0", (session["user_id"],)
    )
    db.commit()

    # Get user's available cash
    cursor.execute("SELECT cash FROM users WHERE id=%s", (session["user_id"],))
    available_cash = cursor.fetchone()

    # Add user's available cash to total holdings
    total_portfolio_value = available_cash["cash"] + Decimal(total_stock_value)

    # Get current portfolio
    cursor.execute(
        "SELECT * FROM portfolio WHERE id=%s ORDER BY symbol", (session["user_id"],)
    )
    current_portfolio = cursor.fetchall()

    return render_template(
        "portfolio.html",
        stocks=current_portfolio,
        user_cash=usd(available_cash["cash"]),
        grand_total=usd(total_portfolio_value),
    )


@application.route("/quote", methods=["GET", "POST"])
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
        return render_template(
            "quoted.html", stock=stock_info, price=usd(stock_info["price"])
        )

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@application.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        db, cursor = open_database()
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
        cursor.execute("SELECT cash FROM users WHERE id=%s", (session["user_id"],))
        available_cash = cursor.fetchone()

        # Variable for the total purchase price
        purchase_price = share_price * shares_buying

        # Check if user can afford the shares
        if not available_cash or float(available_cash["cash"]) < purchase_price:
            return apology("not enough cash available")

        # Update user's history
        cursor.execute(
            "INSERT INTO history (id, symbol, transactions, price) VALUES (%s, %s, %s, %s)",
            (session["user_id"], symbol_buying, shares_buying, share_price),
        )
        db.commit()

        # Check if user already owns shares from a company
        cursor.execute(
            "SELECT shares FROM portfolio WHERE id=%s AND symbol=%s",
            (session["user_id"], symbol_buying),
        )
        has_shares = cursor.fetchall()

        # If user already has shares from the company, update portfolio
        if has_shares:
            cursor.execute(
                "UPDATE portfolio SET shares=shares+%s WHERE id=%s",
                (shares_buying, session["user_id"]),
            )
            db.commit()

        # If user doesn't have shares from the company, insert into portfolio
        else:
            cursor.execute(
                "INSERT INTO portfolio (id, symbol, name_, shares, price, total) \
                VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    session["user_id"],
                    symbol_buying,
                    stock_info["name"],
                    shares_buying,
                    share_price,
                    purchase_price,
                ),
            )
            db.commit()

        # Update user's available cash
        cursor.execute(
            "UPDATE users SET cash=cash-%s WHERE id=%s",
            (purchase_price, session["user_id"]),
        )
        db.commit()

        # Redirect user to home page
        flash(
            "Bought {} share(s) of {} successfully!".format(
                shares_buying, symbol_buying
            )
        )
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@application.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    db, cursor = open_database()

    # Query database for user's stocks
    cursor.execute("SELECT * FROM portfolio WHERE id=%s", (session["user_id"],))
    user_stocks = cursor.fetchall()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Look up stock information
        stock_info = lookup(request.form.get("symbol"))

        # Variable for stock name
        symbol_selling = stock_info["symbol"]

        # Variable for number of shares trying to sell
        shares_selling = int(request.form.get("shares"))

        # Get number of shares user owns
        cursor.execute(
            "SELECT shares FROM portfolio WHERE id=%s AND symbol=%s",
            (session["user_id"], symbol_selling),
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
            (session["user_id"], symbol_selling, -shares_selling, share_price),
        )
        db.commit()

        # Update user's portfolio by deleting shares sold
        cursor.execute(
            "UPDATE portfolio SET shares=shares-%s, total=total-%s WHERE id=%s AND symbol=%s",
            (shares_selling, sale_price, session["user_id"], symbol_selling),
        )
        db.commit()

        # Update user's available cash
        cursor.execute(
            "UPDATE users SET cash=cash+%s WHERE id=%s",
            (sale_price, session["user_id"]),
        )
        db.commit()

        # Redirect user to home page
        flash(
            "Sold {} share(s) of {} successfully!".format(
                shares_selling, symbol_selling
            )
        )
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", stocks=user_stocks)


@application.route("/history")
@login_required
def history():
    """Show history of transactions"""
    db, cursor = open_database()

    # Get user's history
    cursor.execute(
        "SELECT * FROM history WHERE id=%s ORDER BY time_", (session["user_id"],)
    )
    user_history = cursor.fetchall()

    return render_template("history.html", histories=user_history)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    application.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    application.run()
