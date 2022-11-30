import pandas.core.groupby.groupby
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash
#from flask_navigation import Navigation
import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import plotly
import plotly.express as px
import os

app = Flask(__name__)
#nav = Navigation(app)
app.secret_key = os.urandom(32)

#nav.Bar('top', [
    #nav.Item('Home', 'Home'),
    #nav.Item('Rental', 'GRental'),
    #nav.Item('Resale', 'Resaleindex'),
    # add more if needed
#])

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

    # test display those with lease commencement year 2021 AND june
    for doc in db.rent.find({"lease_commencement_year": 2021, "lease_commencement_month": "Jun"}):
        s = s + "<tr style='border-bottom: 1px solid black'>"
        for row in doc:
            if str(row) != "_id":  # dont print object id
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
# @app.route("/")
def index():
    insertRentDataFromCSV()  # uncomment these two lines if you want to insert data
    insertResaleDataFromCSV()

    # resale: test display those with resale price less than 168000 and flat type 1 room or 3 room
    # rent:test display those with lease commencement year 2021 AND june
    return "<html><body>" + displayResaleData() + displayRentData() + "</html></body>"


@app.route('/Register')
def Register():
    return render_template("Register.html")


@app.route("/")
def Login():
    return render_template("Login.html")

@app.route("/changePassword")
def changePassword():
    return render_template("Password.html")


# add user function
@app.route("/registerNewUser", methods=["POST"])
def registerNewUser():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        password = request.form["password"]
        mydict = {}
        mydict["username"] = username
        mydict["password"] = password
        mydict["name"] = name
        x = db["user"].find_one({"username":username})
        if(x==None):
            db["user"].insert_one(mydict)
            return redirect(url_for("Login"))
        else:
            error = "Existing user already in database"
            return render_template("Register.html", error = error)
@app.route("/loginUser", methods=["POST"])
def loginUser():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        aDict = {}
        aDict["username"] = username
        aDict["password"] = password
        x = db["user"].find(aDict)
        result = list(x)
        if len(result) == 0:
            session["loggedIn"] = False
            flash("Invalid username or password!", "LoginError")
            return redirect(url_for("Login"))
        elif len(result) == 1:
            session["loggedIn"] = True
            session["loggedInUser"] = username
            if session.get("loginMsg") == True:
                del session["loginMsg"]
            return "<html><body>" + displayResaleData() + displayRentData() + "</html></body>"
        else:
            session["loggedIn"] = False
            flash("Error occured!", "LoginError")
            return redirect(url_for("Login"))

        return redirect(url_for("Login"))

@app.route("/changePassword1", methods=["POST"])
def changePassword2():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        aDict = {}
        aDict["username"] = username

        x = db["user"].find(aDict)
        result = list(x)
        if len(result) == 0:
            session["loggedIn"] = False
            flash("Invalid username or password!", "LoginError")
            return redirect(url_for("Login"))
        elif len(result) == 1:
            test = {"username": username}
            test1 = {"$set":{"password": password}}
            db["user"].update_one(test,test1)



        return redirect(url_for("Login"))
@app.route('/Home')
def Home():
    if session.get("loggedIn") == True:
        return render_template("Home.html")
    else:
        redirect(url_for("Login"))


@app.route('/AveragePriceResale')
def GResale():
    grouped = db.resale.aggregate(
        [
            {
                "$group":
                    {
                        "_id": "$town",
                        "avgResalePrice": {"$avg": "$resale_price"}
                    }
            }
        ]
    )
    listing = list(grouped)
    df = pd.DataFrame(listing)

    fig = px.bar(df, x="_id", y="avgResalePrice", color='_id', barmode="group", labels={
        "_id": "Town", "avgResalePrice": "Average Resale Price"})

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Resale Graph "
    description = """
    A graph showing the average price comparison between the different areas.
    """
    return render_template('AveragePriceResale.html', graphJSON=graphJSON, header=header, description=description)


@app.route('/TotalResale')
def GResale2():
    grouped = db.resale.aggregate([{
        '$group': {
            '_id': '$town',
            'count': {'$sum': 1}}
    }, {
        '$match': {
            'count': {'$gt': 1}
        }}])
    listing2 = list(grouped)

    df = pd.DataFrame(listing2)
    print(df)
    fig = px.bar(df, x='_id', y='count', color='_id', barmode="group",labels={
        "_id": "Town", "count": "Number of Resale"})

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Resale Graph 2"
    description = """
    A graph showing the highest resale comparison between the different areas.
    """
    return render_template('TotalResale.html', graphJSON=graphJSON, header=header, description=description)

@app.route('/ResaleGraph')
def Resaleindex():
    return render_template('Resale_Graph.html')
@app.route('/Rental')
def GRental():
    AvgRentalOverTime = db.rent.aggregate(
        [
            {
                "$group":
                    {
                        '_id': '$lease_commencement_year',
                        "avgRentalFee": {"$avg": "$monthly_gross_rent"},

                    }
            }, {"$sort": {"_id": 1}}
        ]
    )
    AvgRentalOverTimeList = list(AvgRentalOverTime)
    AvgRentalOverTimeDF = pd.DataFrame(AvgRentalOverTimeList)
    fig1 = px.line(AvgRentalOverTimeDF, x="_id", y="avgRentalFee", title='Average Rental Price Over Years',labels={
        "_id": "Lease Commencement date", "count": "Average Rental Fees"})
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    description1 = """
    A graph showing the increase of rental prices over the years.
    """

    AvgRentalByPostalDistrict = db.rent.aggregate(
        [
            {
                "$group":
                    {
                        '_id': '$postal_district',
                        "avgRentalFee": {"$avg": "$monthly_gross_rent"},

                    }
            }, {"$sort": {"_id": 1}}
        ]
    )
    AvgRentalByPostalDistrictList = list(AvgRentalByPostalDistrict)
    AvgRentalByPostalDistrictDF = pd.DataFrame(AvgRentalByPostalDistrictList)
    fig2 = px.bar(AvgRentalByPostalDistrictDF, x="_id", y="avgRentalFee", title='Average Rental Price Over Postal District',labels={
        "_id": "Postal Distict", "count": "Average Rental Fees"})
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    description2 = """
  A graph showing the average price comparison between the different areas.
    """

    ResalePriceNoRooms = db.rent.aggregate(
        [
            {
                "$group":
                    {
                        '_id': '$no_of_bedroom',
                        "avgRentalFee": {"$avg": "$monthly_gross_rent"},

                    }
            }, {"$sort": {"_id": 1}}
        ]
    )
    ResalePriceNoRoomsList = list(ResalePriceNoRooms)
    ResalePriceNoRoomsDF = pd.DataFrame(ResalePriceNoRoomsList)
    fig3 = px.bar(ResalePriceNoRoomsDF, x="_id", y="avgRentalFee", title='Average Resale Price Over No. of Rooms',labels={
        "_id": "Number of Rooms", "count": "Average Rental Fees"})
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    description3 = """
    A graph showing the average price comparison between the different room size.
    """
    return render_template('Rental_Graph.html', graphJSON=graphJSON1,graphJSON2=graphJSON2,graphJSON3=graphJSON3, description1=description1,description2 = description2,description3 = description3 )

@app.route('/ResaleTable')
def resaleTable():
    if "filter_resale" not in session:
        resale_dict = db.resale.find({})
        return render_template('Resale_Table.html', resale_dict = resale_dict)

    else:
        filter_dict = session["filter_resale"]

        resale_dict = db.resale.find({"resale_price": {"$lt": filter_dict["resalePrice"]}, "flat_type": {"$in":[filter_dict["roomNo"]]},"town":{"$in":[filter_dict["town"]]},"floor_area":{"$lt": filter_dict["floorArea"]}})
        return render_template('Resale_Table.html', resale_dict = resale_dict)


@app.route("/updateResaleTable", methods=["POST"])
def updateResaleTable():
    if "filter_resale" in session:
        session.pop("filter_resale")
    resalePrice = int(request.form["resalePrice"])
    town = request.form["town"]
    floorArea = int(request.form["floorArea"])
    roomNo = request.form["roomNo"] + " ROOM"
    session['filter_resale'] = {"resalePrice":resalePrice,"town":town,"floorArea":floorArea, "roomNo":roomNo}
    return redirect(url_for("resaleTable"))

@app.route('/RentalTable')
def rentalTable():
    if "filter_rental" not in session:
        rental_dict = db.rent.find({})
        return render_template('Rental_Table.html', rental_dict=rental_dict)
    else:
        filter_dict = session["filter_rental"]
        rental_dict = db.rent.find(
            {"monthlyGrossRent": {"$lt": [filter_dict["monthlyGrossRent"]]},
             "bedroomNo": {"$in": [filter_dict["bedroomNo"]]}})
        return render_template('Rental_Table.html', rental_dict=rental_dict)

@app.route("/updateRentalTable", methods=["POST"])
def updateRentalTable():
    if "filter_rental" in session:
        session.pop("filter")
    monthlyGrossRent = int(request.form["monthlyGrossRent"])
    bedroomNo = request.form["bedroomNo"] + " ROOM"
    session["filter"] = {"monthlyGrossRent": monthlyGrossRent, "bedroomNo": bedroomNo}
    return redirect(url_for("rentalTable"))


if __name__ == "__main__":
    app.run(debug=True)
