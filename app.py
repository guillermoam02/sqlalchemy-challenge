import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/Hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurements = Base.classes.measurements

session = Session(engine)

app = Flask(__name__)

#########################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - List of prior year rain totals from all stations<br/>"
        f"/api/v1.0/stations - List of Station numbers and names<br/>"
        f"/api/v1.0/tobs - List of prior year temperatures from all stations<br/>"
        f"/api/v1.0/start - When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"/api/v1.0/start/end - When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"
    )
#########################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
    lminfo = session.query(Measurement.date)\
        .order_by(Measurement.date.desc()).first()
    yearago=dt.date(2017, 8, 23)- dt.timedelta(days=365)
    prec= session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date>yearago)\
        .order_by(Measurement.date).all()

    RainTots = []
    for result in prec:
        row = {}
        row["date"] = prec[0]
        row["prcp"] = prec[1]
        RainTots.append(row)

    return jsonify(RainTots)

#########################################
@app.route("/api/v1.0/stations")
def stations():
    activestations=session.query(Measurement.station,\
        func.count(Measurement.station))\
        .group_by(Measurement.station)\
            .order_by(func.count(Measurement.station).desc()).all()
    return jsonify(stations.to_dict())

#########################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    lminfo = session.query(Measurement.date)\
        .order_by(Measurement.date.desc()).first()
    yearago=dt.date(2017, 8, 23)- dt.timedelta(days=365)
    HObs = session.query(Measurement.date, Measurement.tobs)\
        .filter (Measurement.date>yearago)\
        .filter (Measurement.station == ID)\
        .order_by (Measurement.date)\
        .all()

    TempTots = []
    for result in HObs:
        row = {}
        row["date"] = HObs[0]
        row["tobs"] = HObs[1]
        TempTots.append(row)

    return jsonify(TempTots)

#########################################
@app.route("/api/v1.0/<start>")
def OnlyStart(start):

    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    DataList = list(np.ravel(data))
    return jsonify(DataList)

#########################################
@app.route("/api/v1.0/<start>/<end>")
def StartAndEnd(start,end):

    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    DataList = list(np.ravel(data))
    return jsonify(DataList)

#########################################

if __name__ == "__main__":
    app.run(debug=True)
