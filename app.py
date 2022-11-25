import pandas.core.groupby.groupby
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_navigation import Navigation
import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import plotly
import plotly.express as px
import os

app = Flask(__name__)
nav = Navigation(app)
app.secret_key = os.urandom(32)

nav.Bar('top', [
    nav.Item('Home', 'Home'),
    nav.Item('Rental', 'GRental'),
    nav.Item('Resale', 'Resaleindex'),
    #add more if needed
])

client = MongoClient('localhost', 27017)

db = client.rnrhousing


def insertRentDataFromCSV():
    try:
        data = pd.read_csv("./rental data.csv")
        df = pd.DataFrame(data)
        records = df.to_dict(orient="records")
        print("Adding rent data")

        if db.rent.count_documents({}) == 0:
            db.rent.insert_many(records)
        else:
            print("Data already exists in Rent collection")

    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})
    else:
        print("InsertRentData ran successfully")


def insertResaleDataFromCSV():
    try:
        data = pd.read_csv("./resale data.csv")
        df = pd.DataFrame(data)
        records = df.to_dict(orient="records")
        print("Adding resale data")

        if db.resale.count_documents({}) == 0:
            db.resale.insert_many(records)
        else:
            print("Data already exists in Resale collection")

    except pandas.core.groupby.groupby.DataError as pe:
        print("Error in Pandas: ", {pe})
    else:
        print("InsertResaleData ran successfully")

def displayRentData():
    s = "<table style='border:1px solid red; border-collapse: collapse;'>"
    s = s + '''<tr style='border-bottom: 1px solid black'>
                        <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>no of bedroom</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>rental fees (monthly)</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>postal district</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>lease commencement year</td>
                        <td style='padding: 10px; border-right: 1px solid blue'>lease commencement month</td></tr>
                        '''

    #test display those with lease commencement year 2021 AND june
    for doc in db.rent.find({"lease_commencement_year": 2021, "lease_commencement_month": "Jun"}):
        s = s + "<tr style='border-bottom: 1px solid black'>"
        for row in doc:
            if str(row) != "_id": #dont print object id
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(doc[str(row)]) + "</td>"
        s = s + "</tr>"

    s = s + "</table>"

    return s

def displayResaleData():
    s = "<table style='border:1px solid red; border-collapse: collapse;'>"
    s = s + '''<tr style='border-bottom: 1px solid black'>
                            <td style='padding: 10px; border-right: 1px solid blue'>resale price</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>town</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>remaining lease</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>room type</td>
                            <td style='padding: 10px; border-right: 1px solid blue'>floor area (sqm)</td></tr>
                            '''

    # test display those with resale price less than 168000 and flat type 1 room or 3 room
    for doc in db.resale.find({"resale_price": {"$lt": 168000}, "flat_type": {"$in": ["1 ROOM", "3 ROOM"]}}):
        s = s + "<tr style='border-bottom: 1px solid black'>"
        for row in doc:
            if str(row) != "_id":  # dont print object id
                s = s + "<td style='padding: 10px; border-right: 1px solid blue'>" + str(doc[str(row)]) + "</td>"
        s = s + "</tr>"

    s = s + "</table>"

    return s

# uncomment if u wanna add to database and see if records are added
@app.route("/")
def index():

    insertRentDataFromCSV() #uncomment these two lines if you want to insert data
    insertResaleDataFromCSV()

    #resale: test display those with resale price less than 168000 and flat type 1 room or 3 room
    #rent:test display those with lease commencement year 2021 AND june
    return "<html><body>" + displayResaleData() + displayRentData() + "</html></body>"



if __name__ == "__main__":
    app.run(debug=True)
