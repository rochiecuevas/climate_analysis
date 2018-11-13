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
        f"/api/v1.0/<br/>"
        f"/api/v2.0/"
    )


@app.route("/api/v1.0/precipitation")
def rain():
    """Returns precipitation results for 1 year from the last record."""

    # Query the last record in the list
    Latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = Latest_date[0]
    
    # Estimate the date for 1 year ago
    year_ago = dt.date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:11])) - dt.timedelta(days = 365)
    
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
              order_by(Measurement.date).filter(Measurement.date > year_ago).all()
    
    # Organise query object contents into a nested dictionary
        # Main dictionary key is row[0], which contains dates
        # Subdictionary keys are in row[1], which contains station ids
        # Values are in row[2], which contains precipitation records  
    rain = []
    prcp_dict = {}
    for row in results:
        if row[0] not in prcp_dict:
            prcp_dict[row[0]] = {}
        prcp_dict[row[0]][row[1]] = row[2]
    rain.append(prcp_dict)
        
    return jsonify(rain)   


@app.route("/api/v1.0/stations")
def stns():
    """Returns a list of weather stations."""
    # Query information about the weather stations
    sel = [Measurement.station, Station.name, Station.elevation, 
           Station.latitude, Station.longitude]

    results = session.query(*sel).filter(Measurement.station == Station.station).\
              group_by(Measurement.station).all()
    
    # Organise query object contents into a nested dictionary
        # Main dictionary key is row[0], which contains station ids
        # Subdictionary keys are: 
            # row[1], station name
            # row[2], station elevation
            # row[3], latitude
            # row[4], longitude
    stations = []
    all_stns = {}
    for row in results:
        if row[0] not in all_stns:
            all_stns[row[0]] = {}
            all_stns[row[0]]["name"] = row[1]
            all_stns[row[0]]["elevation"] = row[2]
            all_stns[row[0]]["lat"] = row[3]
            all_stns[row[0]]["lng"] = row[4]
    stations.append(all_stns)
    
    return jsonify(stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns observed temperature records for 1 year from the last record."""
    # Query the last record in the list
    Latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = Latest_date[0]
    
    # Estimate the date for 1 year ago
    year_ago = dt.date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:11])) - dt.timedelta(days = 365)
    
    # Query the temperature records for the last 365 days
    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
              filter(Measurement.date > year_ago).all()
    
    # Organise query object contents into a nested dictionary
        # Main dictionary key is row[0], which contains dates
        # Subdictionary key is row[1], which contains station ids
        # Values are in row[2], which contains tobs (observed temperature)
    temps = []
    all_tobs = {}
    for row in results:
        if row[0] not in all_tobs:
            all_tobs[row[0]] = {}
        all_tobs[row[0]][row[1]] = row[2]
    temps.append(all_tobs)   
    
    return jsonify(temps)


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
        results2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
        func.max(Measurement.tobs), func.min(Measurement.prcp), func.avg(Measurement.prcp), 
        func.max(Measurement.prcp)).filter(Measurement.date >= start_date).all()
    
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
        

@app.route("/api/v2.0/") 
def report_start_end():
    """Provide the start and the end dates."""
    start_date = request.args.get["startdate"] 
    end_date = request.args.get("enddate") 
    
    # Query the validity of the dates
    results = session.query(Measurement.date).all()
    results_list = [date[0] for date in results]
    
    if start_date not in results_list:
        return f"The start date has no record. Try again."
    else:
        if end_date not in results_list:
            return f"The end date has no record. Try again."
        else:
            if start_date > end_date:
                return(
                    f"WARNING: Your tropical paradise vacation *cannot* end before it starts.<br/>" 
                    f"Try different start and end dates."
                )
            else:
                # Query for results if date values are valid
                results2 = session.query(func.min(Measurement.tobs), 
                func.avg(Measurement.tobs), func.max(Measurement.tobs), 
                func.min(Measurement.prcp), func.avg(Measurement.prcp), 
                func.max(Measurement.prcp)).filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all()

                all_weather2 = []
                for data in results2:
                    data_dict = {}
                    data_dict["TempF min"] = int(data[0])
                    data_dict["TempF avg"] = int(data[1])
                    data_dict["TempF max"] = int(data[2])
                    data_dict["Precipitation min"] = round(data[3],2)
                    data_dict["Precipitation avg"] = round(data[4],2)
                    data_dict["Precipitation max"] = round(data[5],2)
                    all_weather2.append(data_dict)
    
                return jsonify(all_weather2)
    

@app.route("/query-example") 
def weather_reports():

    # Provide start and end dates for the analysis
    start_date = request.args.get("startdate") 
    end_date = request.args.get("enddate")

    if start_date is None:
        return("Enter a start date.")

    # Validate start date
    results = session.query(Measurement.date).all()
    results_list = [date[0] for date in results]

    if start_date not in results_list:
        return("Pick another start date.")

    if end_date not in results_list and end_date is not None:
        return("Pick another end date.")    

    if end_date is None:
        # Query the last record in the list
        Latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        end_date = Latest_date[0]
        
        # Query for results if date values are valid
        results2 = session.query(func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), func.max(Measurement.tobs), 
        func.min(Measurement.prcp), func.avg(Measurement.prcp), 
        func.max(Measurement.prcp)).filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

        all_weather2 = []
        for data in results2:
            data_dict = {}
            data_dict["TempF min"] = int(data[0])
            data_dict["TempF avg"] = int(data[1])
            data_dict["TempF max"] = int(data[2])
            data_dict["Precipitation min"] = round(data[3],2)
            data_dict["Precipitation avg"] = round(data[4],2)
            data_dict["Precipitation max"] = round(data[5],2)
        all_weather2.append(data_dict)
    
        return jsonify(all_weather2)
    
    if end_date < start_date:
        return("Vacation cannot start before it ends. Enter a new end date.")

    # Query for results if date values are valid
    results3 = session.query(func.min(Measurement.tobs), 
    func.avg(Measurement.tobs), func.max(Measurement.tobs), 
    func.min(Measurement.prcp), func.avg(Measurement.prcp), 
    func.max(Measurement.prcp)).filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()

    all_weather3 = []
    for data in results3:
        data_dict = {}
        data_dict["TempF min"] = int(data[0])
        data_dict["TempF avg"] = int(data[1])
        data_dict["TempF max"] = int(data[2])
        data_dict["Precipitation min"] = round(data[3],2)
        data_dict["Precipitation avg"] = round(data[4],2)
        data_dict["Precipitation max"] = round(data[5],2)
    all_weather3.append(data_dict)
    
    return jsonify(all_weather3)     
    

if __name__ == '__main__':
    app.run(debug=True)
        