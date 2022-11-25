import pandas.core.groupby.groupby
from flask import Flask, render_template
from flask_navigation import Navigation
import mariadb
import sys
import pandas as pd


try:
    conn = mariadb.connect(
             host='127.0.0.1',
             port=3306,
             user='root',
             password='root',
             database='RnRHousing')
except mariadb.Error as e:
    print(f"An error occurred while connecting to MariaDB: ", {e})
    sys.exit(1)

cur = conn.cursor()


cur.execute("SELECT r.rentalFees, r.postalDistrict, h.numberOfRooms, r.floorArea FROM Rent as r, HouseType as h WHERE r.houseTypeID = h.houseTypeID")
rv = cur.fetchall()


rentalFees = []
postalDistrict = []
noOfRooms = []
floorArea = []
for x in rv:
    rentalFees.append(x[0])
    postalDistrict.append(x[1])
    noOfRooms.append(x[2])
    floorArea.append(x[3])

df = pd.DataFrame(list(zip(rentalFees, postalDistrict,noOfRooms,floorArea)),columns =['RentalFees', 'Postal District',"NoOfRooms","FloorArea"])
print (df)

df.to_html('templates/Rental_Graph1.html')
