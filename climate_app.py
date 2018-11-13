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

from flask import Flask, request, jsonify

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
        f"/api/v1.0/<start_date><br/>"
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


@app.route("/api/v1.0/") 
def report_start():
    """Returns minimum, maximum, & average temperatures & precipitation values from start date onwards.
       First validates the date indicated by the user. Then returns the summary weather stats.
       
       Args:
           start_date (string): A date value that follows the %Y-%m-%d format.
       
       Output:
           min, max, avg for temperature and precipitation.
    """
    
    start_date = request.args.get("startdate")
    
    # Query for the dates to validate user-input dates
    results = session.query(Measurement.date).all()
    results_list = [date[0] for date in results]
    
    if start_date not in results_list:
        return "Date not found. Please try again."
    
    else:
        # Query for results if date values are valid
        results2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.prcp), func.avg(Measurement.prcp), func.max(Measurement.prcp)).filter(Measurement.date >= start_date).all()
    
        all_weather = []
        for data in results2:
            data_dict = {}
            data_dict["TempF min"] = int(data[0])
            data_dict["TempF avg"] = int(data[1])
            data_dict["TempF max"] = int(data[2])
            data_dict["Precipitation min"] = round(data[3],2)
            data_dict["Precipitation avg"] = round(data[4],2)
            data_dict["Precipitation max"] = round(data[5],2)
            all_weather.append(data_dict)
    
            return jsonify(all_weather)
        

@app.route("/v2.0/") 
def report_start_end():
    """Provide the start and the end dates."""
    start_date = request.args.get("startdate") # If key doesn't exist, return None.
    end_date = request.args.get("enddate") # If key doesn't exist, return None.
    
    # Query the validity of the dates
    results = session.query(Measurement.date).all()
    results_list = [date[0] for date in results]
    
    if start_date not in results_list or end_date not in results_list:
        return f"Dates are not in the list. Try again."
    else:
        return f"Aha!"
    

if __name__ == '__main__':
    app.run(debug=True)
        