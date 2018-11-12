#################################################
# Dependencies
#################################################

# Packages for data processing and preliminary analyses
import numpy as np
import pandas as pd

# Package for handling time data
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the climate app! Today we explore precipitation and temperature in Oahu.<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def rain():
    """Returns precipitation results."""
    # Query all precipitation data
    results = session.query(Measurement).all()
    
    all_rain = []
    for precipitation in results:
        precipitation_dict = {}
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["precipitation"] = precipitation.prcp
        all_rain.append(precipitation_dict)
        
    return jsonify(all_rain)   


@app.route("/api/v1.0/stations")
def stns():
    """Returns a list of weather stations."""
    # Query all weather stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    
    # Convert list of tuples into a regular list
    all_stns = list(np.ravel(results)) 
    
    return jsonify(all_stns)
    

@app.route("/api/v1.0/tobs")
def temp():
    """Returns observed temperature records for 1 year from the last record."""
    # Query the last record in the list
    Latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = Latest_date[0]
    
    # Estimate the date for 1 year ago
    year_ago = dt.date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:11])) - dt.timedelta(days = 365)
    
    # Query the temperature records for the last 365 days
    results = session.query(Measurement).filter(Measurement.date > year_ago).all()
    
    all_tobs = []
    for temp in results:
        temp_dict = {}
        temp_dict["date"] = temp.date
        temp_dict["temp_obs"] = temp.tobs
        
        all_tobs.append(temp_dict)
           
    return jsonify(all_tobs)


if __name__ == '__main__':
    app.run(debug=True)
        