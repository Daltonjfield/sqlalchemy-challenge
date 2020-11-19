import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#set up flask app
app=Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaiian Weather Report!<br/>"
        f"/api/v1.0/precipitation:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using `date` as the key and `prcp` as the value.""" 

    last_date = session.query(measurement.date).\
            order_by(measurement.date.desc()).first()

    date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    prcp_data = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date >= date_year_ago).\
            order_by(measurement.date.desc()).all()
    
    date_prcp_list = [prcp_data]

    return jsonify(date_prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset.""" 

    # most_active_stations = session.query(measurement.station, func.count(measurement.station)).\
    #                 group_by(measurement.station).\
    #                 order_by(func.count(measurement.station).desc()).all()

    stationresults = session.query(station.station , station.name)
    
    station_list = []

    for stations in stationresults:
        station_dict = {}
        station_dict["Station"] = stations.station
        station_dict["Name"] = stations.name
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def TOBS():
    """Query the dates and temperature observations of the most active station for the last year of data.""" 

    date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    highest_num_temp = session.query(measurement.date,(measurement.tobs)).\
                          filter(measurement.date >= date_year_ago ).\
                          filter(measurement.station == "USC00519281").all()

    temp = []

    for hightemp in highest_num_temp:
        tobs_dict = {}
        tobs_dict["Date"] = hightemp[0]
        tobs_dict["Temperature"] = hightemp[1]
        temp.append(tobs_dict)

    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def startd(date):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""

    start_date = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
    filter(measurement.station == date).all()
    
    
    input_date = []

    for tempmeasure in start_date:
        sdate_dict = {}
        sdate_dict["SDATE"] = date
        sdate_dict["MIN"] = float(tempmeasure[0])
        sdate_dict["AVG"] = float(tempmeasure[2])
        sdate_dict["MAX"] = float(tempmeasure[1])
        input_date.append(sdate_dict)

    return jsonify(input_date)



if __name__ == '__main__':
    app.run(debug=True)



