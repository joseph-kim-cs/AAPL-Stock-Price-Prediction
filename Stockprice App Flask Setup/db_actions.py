# Description:
# modifying the db_actions.py file so that it works with stockprice.csv, which I got from Yahoo Finance
import sqlite3 as sl

db = "stockprices.db"
def create():
    # connect to the database
    conn = sl.connect(db)
    curs = conn.cursor()

    # create database table
    curs.execute('DROP TABLE IF EXISTS stockprices')
    curs.execute("""CREATE TABLE stockprices (date TEXT, name TEXT, price REAL)""")
    conn.commit()
    conn.close()

def store_data(csv_file):
    conn = sl.connect(db)
    curs = conn.cursor()

    with open(csv_file, "r") as f:
        header = f.readline().strip().split(",")
        stock_names = header[1:]  # exclude the date from the header to get the different stocks

        for line in f:
            data = line.strip().split(",")
            date = data[0]  # the first column is the date
            prices = data[1:]  # remaining columns are stock prices

            # as per the formatting of the datatable, insert each stock's data as a separate row
            for name, price in zip(stock_names, prices):
                price = float(price)
                curs.execute("INSERT INTO stockprices (date, name, price) VALUES (?, ?, ?)", (date, name, price))

    conn.commit()
    conn.close()

def main():
    create()
    store_data("csv/stockprice.csv")

if __name__ == "__main__":
    main()
