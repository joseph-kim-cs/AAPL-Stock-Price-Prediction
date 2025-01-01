# Joseph Kim jkim3643@usc.edu
# ITP 216, Fall 2024
# Section: 20243
# Final Project
# Description:
# Final Project app uses a linear regression model to predict stock prices based on dates and stock title

import datetime
import io
import os
import sqlite3 as sl

import pandas as pd
from flask import Flask, redirect, render_template, request, session, url_for, send_file
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = "stockprices.db"

@app.route("/") # GET instance 1
def home():
    return render_template("home.html", locales=db_get_stocks(), message="Select a stock.")

@app.route("/submit_locale", methods=["POST"]) # taken from Final Project Helper files, POST instance 1
def submit_locale():

    print(request.form['locale'])
    session["locale"] = request.form["locale"]
    if 'locale' not in session or session["locale"] == "":
        return redirect(url_for("home"))

    #if "data_request" not in request.form: # change from original app.py -> we don't need data_request since we are only looking at one type of data
    #    return redirect(url_for("home"))
    #session["data_request"] = request.form["data_request"] # -> all instances of data_request are removed from here on out

    return redirect(url_for("locale_current", locale=session["locale"]))


@app.route("/api/stocks/<locale>")
def locale_current(locale):
    return render_template("locale.html", locale=locale, project=False)


@app.route("/submit_projection", methods=["POST"]) # POST instance 2
def submit_projection():
    user_date = request.form.get("date", "") # should note that date needs to be inputted as mm/dd/yy in locale.html
    if not user_date:
        return redirect(url_for("home"))

    # stockprices.db contains date data as yyyy-mm-dd, so we need to convert user_date to this format
    session["date"] = datetime.datetime.strptime(user_date, "%m/%d/%y").strftime("%Y-%m-%d")

    if 'locale' not in session:
        return redirect(url_for("home"))
    session["date"] = request.form["date"]
    # THESE NEED TO BE BACK IN!

    if session["locale"] == "" or session["date"] == "":
        return redirect(url_for("home"))

    return redirect(url_for("locale_projection", locale=session["locale"]))


@app.route("/api/stocks/projection/<locale>") # dynamic GET endpoint
def locale_projection(locale):
    return render_template("locale.html", locale=locale, project=True, date=session["date"])


@app.route("/fig/<locale>")
def fig(locale):
    # fig() is how locale can load in figures
    fig = create_figure(locale)

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype="image/png")


def create_figure(locale):
    df = db_create_dataframe(locale)
    #print(session)
    #print(df.head())

    if 'date' not in session: # if nothing is entered in 'date' in locale, just plot the historical data
        fig = Figure() # non-ML plot
        ax = fig.add_subplot(1, 1, 1)

        # fig, ax = plt.subplots(1, 1)
        ax.plot(df["date"], df["price"], label='Historical Data')
        ax.legend()
        ax.set(xlabel="date", ylabel="price", title="Stock price of " + str(locale))
        return fig

    else: # ML Plot
        df['datemod'] = df['date'].map(datetime.datetime.toordinal)

        # define X and y for linear regression model
        y = df['price'].values
        X = df['datemod'].values.reshape(-1, 1)

        # perform linear regression model
        regr = LinearRegression()
        regr.fit(X, y)

        future_date = datetime.datetime.strptime(session["date"], "%m/%d/%y")  # remember that the date is different in db
        draw = datetime.datetime.toordinal(future_date)
        y_pred = regr.predict([[draw]])[0]  # linear regression prediction

        # similar to the given helper. I actually dont like so remove.
        '''
        if future_date and y_pred: # add to the dataframe by row from the inputs
            # use pd.concat since append does not work anymore in pandas 2.0

            temp = pd.DataFrame({'date': [future_date], 'price': [y_pred]})
            df = pd.concat([df, temp], ignore_index=True)
        '''

        # plot the figure using historical data and the prediction
        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter([future_date], [y_pred], color='red', label="projection") # insert a red dot through matplotlib scatterplot that shows the projected value at a date
        ax.plot(df["date"], df["price"], label='Historical Data')
        ax.legend()
        ax.set(xlabel="date", ylabel="price", title="Stock price of " + str(locale))
        return fig


def db_create_dataframe(locale): # does not need to be as complicated as helper file since my db is simpler
    conn = sl.connect(db)
    query = "SELECT date, price FROM stockprices WHERE name = ? ORDER BY date"

    df = pd.read_sql_query(query, conn, params=(locale, )) # based on the locale (stock) name, return all dates and values related
    df['date'] = pd.to_datetime(df['date'])
    print(df.head())

    conn.close()
    return df


def db_get_stocks():
    conn = sl.connect(db)
    query = "SELECT DISTINCT name FROM stockprices" # there are only 20 stocks, so return only these names

    stocks = [row[0] for row in conn.execute(query)]
    conn.close()
    return stocks


@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
